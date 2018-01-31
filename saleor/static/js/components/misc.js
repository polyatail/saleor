import SVGInjector from 'svg-injector-2';

console.log('loading this code');


var placeOrderButton = document.getElementById('place-order-button');

if (placeOrderButton) {
  placeOrderButton.addEventListener('click', function () {
    var placeOrderForm = document.getElementById('place-order');
    var checkoutNowField = document.getElementById('checkout-now');

    checkoutNowField.value = 1;
    placeOrderForm.submit();
  });
}

export const getAjaxError = (response) => {
  let ajaxError = $.parseJSON(response.responseText).error.quantity;
  return ajaxError;
};
export const csrftoken = $.cookie('csrftoken');

export default $(document).ready((e) => {
  function csrfSafeMethod(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  }

  new SVGInjector().inject(document.querySelectorAll('svg[data-src]'));

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
      }
    }
  });

  // Open tab from the link

  let hash = window.location.hash;
  $('.nav-tabs a[href="' + hash + '"]').tab('show');
});

