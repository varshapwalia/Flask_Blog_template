function subscribeForm() {
  let emailVal = $('#subscribe-email').val();
  if (emailVal && validateEmail(emailVal)) {
    $.post("/subscribe",{
      email: emailVal
    },
    function(data, status){
      alert(data);
      $('#subscribe-email').val("");
    });
  }
}