document.addEventListener('DOMContentLoaded', () => {

  // Modify modal when a menu item is clicked
  document.querySelectorAll('.menu-items').forEach((menu) => {
    menu.onclick = function() {
      const template = Handlebars.compile(document.querySelector("#modalContent").innerHTML);

      const menuName = this.dataset.menuname;      
      const menuType = this.dataset.type;
      let data = {'menuType': menuType, 'menuName': menuName};

      if (["regularPizza", "sicilianPizza"].includes(menuType)) {
        const items = JSON.parse(document.querySelector(`#${menuType}-items`).textContent);
        const toppings = JSON.parse(document.querySelector('#pizzaTopping-items').textContent);
        data.pizza = items;
        data.toppings = toppings;
      } else if (menuType === "sub" && menuName === "Steak & Cheese") {
        let items = JSON.parse(document.querySelector('#sub-items').textContent);
        items = items.filter(sub => sub.name === menuName);

        let menuItem = [{'id': items[0].id, 'name': items[0].name, 'small': items[0].small, 'large': items[0].large}];
        let extras = [];
        for (let i=0; i<items.length; i++) { 
          extras.push({'id': items[i].add_Ons__id, 'name': items[i].add_Ons__name, 'price': items[i].add_Ons__price}); 
        }
        data.extras = extras;
        data.subX = menuItem[0];
      } else if (menuType === "sub" && menuName !== "Steak & Cheese") {
        let item = JSON.parse(document.querySelector('#sub-items').textContent);
        item = item.find(sub => sub.name === menuName);
        data.sub = item;
      } else if (menuType === "dinnerPlatter") {
        let item = JSON.parse(document.querySelector('#dinnerPlatter-items').textContent);
        item = item.find(dinnerPlatter => dinnerPlatter.name === menuName);
        data.dinnerPlatter = item;
      } else {
        let item = JSON.parse(document.querySelector(`#${menuType}-items`).textContent);
        item = item.find(menuItem => menuItem.name === menuName);
        data.menuItem = item;
      }

      let modalLabel = document.querySelector("#menuModalLabel").innerHTML;
      switch (menuType) {
        case "dinnerPlatter":
          modalLabel = menuName + " Dinner Platter";
          break;
        case "sub":
          modalLabel = menuName + " Sub";
          break;
        default:
          modalLabel = menuName;
      }

      document.querySelector("#menuModalLabel").innerHTML = modalLabel;
      document.querySelector("#dynamicModalBody").innerHTML = template(data);
    }
  })

  // When modal pops up
  $('#menuModal').on('show.bs.modal', () => {
    let orderBtn = document.querySelector('#addToOrder');
    orderBtn.disabled = true;
    let minusBtn = document.querySelector('#minusBtn');
    minusBtn.disabled = true;
    let plusBtn = document.querySelector('#plusBtn');
    let orderQty = document.querySelector('#orderQty');
    let orderTotal = document.querySelector('#orderTotal');
    orderTotal.innerHTML = "";
    let extra = 0;
    let itemPrice;

    orderQty.oninput = function() {
      if ((parseInt(this.value) < 1) || isNaN(parseInt(this.value))) {
        this.value = 1;
      } else {
        updateOrderTotal(orderTotal, orderQty.value, itemPrice, extra);
      }
    }

    minusBtn.onclick = function() {
      if (parseInt(orderQty.value) === 1) {
        this.disabled = true;
      } else {
        this.disabled = false;
        orderQty.stepDown();
        updateOrderTotal(orderTotal, orderQty.value, itemPrice, extra);
        if (parseInt(orderQty.value) === 1) {
          this.disabled = true;
        }
      }
    }

    plusBtn.onclick = () => {
      orderQty.stepUp();
      updateOrderTotal(orderTotal, orderQty.value, itemPrice, extra);
      if (parseInt(orderQty.value) > 1) {
        minusBtn.disabled = false;
      }
    }

    const formName = document.querySelector('#menuModalForm').name;
    if (['regularPizza', 'sicilianPizza'].includes(formName)) {
      const basePrice = JSON.parse(document.querySelector(`#${formName}-items`).textContent);
      itemPrice = parseFloat(basePrice[0].small).toFixed(2);
      let toppingsDiv = document.querySelector('#menuAddons');
      toppingsDiv.style.display = "none";

      document.querySelectorAll('input[name="size"]').forEach((pizzaSize) => {
        pizzaSize.oninput = function () {
          itemPrice = parseFloat(this.dataset.price).toFixed(2);

          const pizzaName = this.dataset.name.toLowerCase();
          if (pizzaName.search("one") >= 0) {
            showToppings(toppingsDiv, 1);
            updateOrderTotal(orderTotal, orderQty.value, itemPrice);
          } else if (pizzaName.search("two") >= 0) {
            showToppings(toppingsDiv, 2);
            updateOrderTotal(orderTotal, orderQty.value, itemPrice);
          } else if (pizzaName.search("three") >= 0) {
            showToppings(toppingsDiv, 3);
            updateOrderTotal(orderTotal, orderQty.value, itemPrice);
          } else {
            document.querySelectorAll('input[name="toppings"]').forEach(topping => {
              topping.checked = false;
            });
            toppingsDiv.style.display = "none";
            orderBtn.disabled = false;
            updateOrderTotal(orderTotal, orderQty.value, itemPrice);
          }
        }
      })
    } else if (['sub', 'subX', 'dinnerPlatter'].includes(formName)) {
      itemPrice = getSubBasePrice();

      document.querySelectorAll('input[name="size"]').forEach(menuSize => {
        menuSize.oninput = function () {
          itemPrice = parseFloat(this.dataset.price).toFixed(2);
          updateOrderTotal(orderTotal, orderQty.value, itemPrice, extra);
          orderBtn.disabled = false;
        }
      })

      if (['sub', 'subX'].includes(formName)) {
        document.querySelectorAll('input[name="subExtras"]').forEach(subExtra => {
          subExtra.oninput = function() {
            if (this.checked) {
              extra += parseFloat(this.dataset.price);
              updateOrderTotal(orderTotal, orderQty.value, itemPrice, extra);
            } else if (!this.checked) {
              extra -= this.dataset.price;
              updateOrderTotal(orderTotal, orderQty.value, itemPrice, extra);
            }
          }
        })
      }
    } else {
      itemPrice = parseFloat(document.querySelector('.pastaSalad').dataset.price).toFixed(2);
      updateOrderTotal(orderTotal, orderQty.value, itemPrice);
      orderBtn.disabled = false;
    }

    // Create AJAX request when submitting form
    document.querySelector('#menuModalForm').onsubmit = () => {
      let data = getFormData();
      $.ajax({
        url: 'cart/addorder/',
        type: 'GET',
        data: data,
        dataType: 'json',
        success: function (data) {
          if (data.error) {
            alert("Please refresh the page and fix your order.");
          } else {
            if (document.querySelector('#zero-cart')) {
              document.querySelector('#zero-cart').style.display = "none";
            }
            document.querySelector('#checkout-btn').disabled = false;
            document.querySelector('#cart-header').innerHTML = "<i class='fas fa-2x fa-cart-arrow-down text-success'></i><br>Ooh, smells delicious in here!";

            const template = Handlebars.compile(document.querySelector('#cart_item').innerHTML);
            const content = template(data);
            document.querySelector('#cartItems').innerHTML += content;
            
            document.querySelector('#cart-total').innerHTML = `: <mark>$${data.cart_total}</mark>`;
            $('#menuModal').modal('hide');
            document.quertSelector('.fa-cart-arrow-down').style.animationPlayState = 'running';
          }
        }
      });
      return false;
    }
  })
  
})


// **************** //
// HELPER FUNCTIONS //
// **************** //
function showToppings(toppingsDiv, limit) {
  document.querySelector('#addToOrder').disabled = true;

  let toppingsHeadline = document.querySelector('#menuAddons>h5>u');
  switch (limit) {
    case 1:
      toppingsHeadline.innerHTML = "Choose <span class='text-success'>one</span> topping";
      break;
    case 2:
      toppingsHeadline.innerHTML = "Choose <span class='text-success'>two</span> toppings";
      break;
    case 3:
      toppingsHeadline.innerHTML = "Choose <span class='text-success'>three</span> toppings";
      break;
  }

  toppingsDiv.style.display = "block";
  let uncheckAll = document.querySelectorAll('input[name="toppings"]');
  uncheckAll.forEach(topping => { topping.checked = false; topping.disabled = false; });

  let checkedToppings = 0;

  let toppings = document.querySelectorAll('input[name="toppings"]');
  toppings.forEach((topping) => {
    topping.oninput = function() {
      if (this.checked) {
        checkedToppings++;
      } else if (!this.checked) {
        checkedToppings--;
      }

      if (limit === checkedToppings) {
        document.querySelectorAll('input[name="toppings"]:not(:checked)').forEach(topping => {
          topping.disabled = true;
          document.querySelector('#addToOrder').disabled = false;
        })
      } else {
        document.querySelectorAll('input[name="toppings"]:not(:checked)').forEach(topping => {
          topping.disabled = false;
          document.querySelector('#addToOrder').disabled = true;
        })
      }
    }
  })
}

function updateOrderTotal(orderTotalButton, quantity, price, extra) {
  extra = extra ? extra : 0;
  orderTotalButton.innerHTML = `: <mark>$${(quantity * price + (extra * quantity)).toFixed(2)}</mark>`
}

function getSubBasePrice() {
  const basePrice = document.querySelector('#menuSize');
  let price = basePrice.querySelector('input[value="small"]');

  if(!price) {
    return parseFloat(basePrice.querySelector('input[value="large"]').dataset.price).toFixed(2);
  } else {
    return parseFloat(price.dataset.price).toFixed(2);
  }
}

function getFormData() {
  const data = {};
  data.category = document.querySelector('input[name="category"]').value;
  data.type = document.querySelector('input[name="type"]').value;
  data.quantity = document.querySelector('#orderQty').value;

  if (data.category === "pizza") {
    data.size = document.querySelector('input[name="size"]:checked').value;
    let toppings = document.querySelectorAll('input[name="toppings"]:checked');
    if (toppings.length > 0) {
      data.toppings = [];
      for (let i = 0; i < toppings.length; i++) {
        data.toppings[i] = toppings[i].value;
      }
    }
  } else if (data.category === "sub") {
    data.size = document.querySelector('input[name="size"]:checked').value;
    let extras = document.querySelectorAll('input[name="subExtras"]:checked');
    if (extras.length > 0) {
      data.extras = [];
      for (let i = 0; i < extras.length; i++) {
        data.extras[i] = extras[i].value;
      }
    }
  } else if (data.category === "dinnerPlatter") {
    data.size = document.querySelector('input[name="size"]:checked').value;
  }

  return data;
}

function cleanupCart() {
  document.querySelector('#cart-total').innerHTML = "";
  document.querySelector('#cart-header').innerHTML = "This space looks desolate. <br> Where's the food? ಥ_ಥ";
  document.querySelector('#cartItems').innerHTML = '<div class="text-center" id="zero-cart"> <i class="fas fa-shopping-cart fa-3x mt-4 text-secondary"></i> <br> <small class="font-weight-bold text-white"> Your order goes here. </small> </div>';
  document.querySelector('#checkout-btn').disabled = true;
  document.querySelector('.fa-shopping-cart').style.animationPlayState = 'running';
}

function deleteOrder(order) {
  const order_id = order.parentElement.parentElement.dataset.orderid;
  const data = {'order_id' : order_id};
  var csrftoken = getCookie('csrftoken');
  
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
  $.ajax({
    url: 'cart/deleteorder/',
    type: 'POST',
    data: data,
    dataType: 'json',
    success: function (data) {
      if (data.error) {
        alert("Please refresh the page and fix your order.");
      } else {
        order.parentElement.parentElement.style.display = "none";
        document.querySelector('#cart-total').innerHTML = `: <mark>$${data.cart_total}</mark>`;
        if (data.cart_total == 0) {
          cleanupCart();
        }
      }
    }
  })
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


// Handlebars.registerHelper("isPizza", function(menuType, options) { 
//   if (["regularPizza", "sicilianPizza"].includes(menuType)) {
//     return options.fn(this);
//   } else {
//     return options.inverse(this);
//   }
// })