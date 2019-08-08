function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
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
    url: 'deleteorder/',
    type: 'POST',
    data: data,
    dataType: 'json',
    success: function (data) {
      if (data.error) {
        alert(data.error);
      } else {
        if (data.cart_total == 0) {
          location.reload();
        } else {
          order.parentElement.parentElement.style.display = "none";
          document.querySelector('#cart-quantity').innerHTML = data.cart_quantity;
          document.querySelector('#cart-total').innerHTML = `: <mark>$${data.cart_total}</mark>`;
        }
      }
    }
  })
}