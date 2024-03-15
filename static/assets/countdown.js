function countdown(to, element, expire_message, expired_callback){
    var countDownDate = new Date(to).getTime();

    // Update the countdown every 1 second
    var x = setInterval(function() {

      // Get today's date and time
      var now = new Date().getTime();

      // Find the distance between now and the countdown date
      var distance = countDownDate - now;

      // Time calculations for hours, minutes and seconds
      var hours = Math.floor(distance / (1000 * 60 * 60));
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);

      // Display the result in the element with id="demo"
      element.innerHTML = String(hours).padStart(2, '0') + ":"
      + String(minutes).padStart(2, '0') + ":" + String(seconds).padStart(2, '0');

      // If the countdown is finished, write some text
      if (distance < 0) {
        clearInterval(x);
        element.innerHTML = expire_message;
        expired_callback();
      }
    }, 1000);
}
