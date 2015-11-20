(function() {
  'use strict';

  function updateManyField($row) {
    var $input = $row.find('input');
    $input.attr('type', 'hidden');

    var currentValue = $input.val();
    var values = currentValue.length ? currentValue.split(';') : [];

    var $values_container = $('<p class="person-label-list"></p>');

    var $current_input = $('<input class="form-control" type="text">');
    $current_input.attr('placeholder', 'Enter name and hit Enter to add person');

    var addBufferToValues = function () {
      var newValue = $current_input.val().trim();
      if (!newValue) {
        return;
      }

      if (values.indexOf(newValue) === -1) {
        values.push(newValue);
        refresh();
      }

      $current_input.val('');
    };

    $current_input.blur(addBufferToValues);

    $current_input.keypress(function(e) {
      // only grab enter
      if (e.which != 13) {
        return;
      }

      addBufferToValues();
      return false; // don't submit the form
    });

    $input.after($values_container);
    $values_container.after($current_input);

    var refresh = function () {
      $input.attr('value', values.join(';'));
      regenerateLabels();
    };

    var regenerateLabels = function () {
      $values_container.html('');

      for(var i = 0; i < values.length; ++i) {
        var $link = $('<a href="#" class="person-label label label-primary"></a>');
        $values_container.append($link);

        $link.text(values[i]);
        $link.append('<span class="glyphicon glyphicon-remove"></span>');

        (function(i) {
          $link.click(function() {
            values.splice(i, 1);
            refresh();
            return false;
          });
        })(i);
      }

      $current_input.prop('required', values.length == 0);
    };

    regenerateLabels();
  }

  $(function () {
    var $artists = $('#comic_artists__row');
    if($artists.length) { updateManyField($artists); }

    var $writers = $('#comic_writers__row');
    if($writers.length) { updateManyField($writers); }
  });
})();
