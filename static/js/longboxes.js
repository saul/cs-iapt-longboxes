$('[data-confirm-click]').click(function() {
  return confirm('Are you sure you want to ' + $(this).data('confirmClick') + '?');
});
