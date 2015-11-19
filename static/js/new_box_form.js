(function() {
  'use strict';

  $(function() {
    var $select = $('#new_box_select');
    if (!$select.length) {
      return;
    }

    var $group = $('#new_box_group');
    var $nameInput = $group.find('[name="name"]');

    var showGroup = function() {
      $group.removeClass('hidden');
      $group.show();
      $nameInput.attr('type', 'text');
    };

    var hideGroup = function() {
      $group.addClass('hidden');
      $nameInput.attr('type', 'hidden');
    };

    $select.change(function() {
      console.log('changed');

      if ($select.val() == 'new') {
        showGroup();
      } else {
        hideGroup();
      }
    });
  });
})();
