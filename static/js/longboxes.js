(function() {
  'use strict';

  // add Bootstrap tooltips to elements with titles
  $('[title]').tooltip();

  // confirm the user wishes to perform the action
  $('[data-confirm-click]').click(function() {
    return confirm('Are you sure you want to ' + $(this).data('confirmClick') + '?');
  });
})();
