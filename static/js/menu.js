document.addEventListener('DOMContentLoaded', () => {
  let modal_form, cart_text = "";
  (function () {
    var csrftoken = getCookie('csrftoken');
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
        }
      });
      $.ajax({
        url: '/',
        type: 'POST',
        data: {'data': 'hbtext'},
        dataType: 'json',
        success: function (data) { 
          modal_form = data.modal_form;
          cart_text = data.cart_text;
        }
      })
  })()

  // Modify modal when a menu item is clicked
  document.querySelectorAll('.menu-items').forEach((menu) => {
    menu.onclick = function() {
      const template = Handlebars.compile(modal_form);

      const menuName = this.dataset.menuname;      
      const menuType = this.dataset.type;
      let data = {'menuType': menuType, 'menuName': menuName};

      if (["RegularPizza", "SicilianPizza"].includes(menuType)) {
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
    if (['RegularPizza', 'SicilianPizza'].includes(formName)) {
      const basePrice = JSON.parse(document.querySelector(`#${formName}-items`).textContent);
      itemPrice = parseFloat(basePrice[0].small).toFixed(2);
      let toppingsDiv = document.querySelector('#menuAddons');
      toppingsDiv.style.display = "none";

      document.querySelectorAll('input[name="size"]').forEach((pizzaSize) => {
        pizzaSize.oninput = function () {
          itemPrice = parseFloat(this.dataset.price).toFixed(2);
          toppingsCount = parseInt(this.dataset.toppings);

          if (toppingsCount > 0) {
            showToppings(toppingsDiv, toppingsCount);
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
      var csrftoken = getCookie('csrftoken');
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
        }
      });
      $.ajax({
        url: 'cart/addorder/',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function (data) {
          let zeroCartDiv = document.querySelector('#zero-cart');
          if (zeroCartDiv) {
            zeroCartDiv.style.display = "none";
          }
          let cartItemsDiv = document.querySelector('#cart-items-div');
          if (data.error) {
            console.log(data.error);
            window.reload();
          } else {
            const template = Handlebars.compile(cart_text);
            const content = template(data);
            document.querySelector('#cartItems').innerHTML += content;
            
            document.querySelector('#checkout-btn').disabled = false;
            document.querySelector('#cart-header').innerHTML = "<i class='fas fa-2x fa-cart-arrow-down text-success'></i><br>Smells delicious in here!";
            document.querySelector('#cart-total').innerHTML = `: <mark>$${data.cart_total}</mark>`;
            $('#menuModal').modal('hide');
            document.querySelector('.fa-cart-arrow-down').style.animationPlayState = 'running';
            
            if (document.querySelector('span.cart-quantity').style.display === "none") {
              document.querySelector('span.cart-quantity').innerHTML = data.cart_quantity;
              document.querySelector('span.cart-quantity').style.display = "";
            } else {
              document.querySelector('span.cart-quantity').innerHTML = data.cart_quantity;
            }
            scrollToBottom(cartItemsDiv);
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
  const toppingsHeadline = document.querySelector('#menuAddons>h5>u');
  const numString = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];

  if (limit === 1) {
    toppingsHeadline.innerHTML = "Choose <span class='text-success'>one</span> topping";
  } else {
    toppingsHeadline.innerHTML = `Choose <span class='text-success'>${numString[limit]}</span> toppings`;
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

function scrollToBottom(div) {
  div.scrollTop = div.scrollHeight;
};

function cartPageRedirect() {
  window.location = 'https://pizza4cs50w.herokuapp.com/cart/';
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
        console.log(data.error);
        window.reload();
      } else {
        if (data.cart_total == 0) {
          location.reload();
        } else {
          order.parentElement.parentElement.style.display = "none";
          document.querySelector('#cart-total').innerHTML = `: <mark>$${data.cart_total}</mark>`;
          document.querySelector('span.cart-quantity').innerHTML = data.cart_quantity;
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