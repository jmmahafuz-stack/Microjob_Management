// MJMS worker available jobs & bookings page
// Disables the accept/decline buttons on submit so a worker can't double-click
// and send the same accept/decline request twice.
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('form').forEach(function (f) {
    var b = f.querySelector('[data-booking-action]');
    if (b) {
      f.addEventListener('submit', function () {
        b.disabled = true;
        b.textContent = 'Processing…';
      });
    }
  });
});
