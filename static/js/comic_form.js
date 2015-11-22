/*
 * Logic to make adding/removing artist and writers from a comic form is more user-friendly.
 */

(function () {
  'use strict';

  /*
   * Called on a row of many-to-many form field (artist or writer)
   */
  function updateManyField($row) {
    // hide the current form field
    var $input = $row.find('input');
    $input.attr('type', 'hidden');

    // calculate what values we already have
    var currentValue = $input.val();
    var values = currentValue.length ? currentValue.split(';') : [];

    // create a container to hold the people
    var $values_container = $('<p class="person-label-list"></p>');

    // create a new input for entering the names
    var $current_input = $('<input class="form-control" type="text">');
    $current_input.attr('placeholder', 'Enter name and hit Enter to add person');

    /*
     * Adds what's currently in the buffer to the list of people
     */
    var addBufferToValues = function () {
      var newValue = $current_input.val().replace(/;/g, '').trim();

      if (newValue) {
        // don't add the name if it already exists
        if (values.indexOf(newValue) === -1) {
          values.push(newValue);
          refresh();
        }
      }

      // clear the input
      $current_input.val('');
    };

    // when the field loses focus, add it to list of people
    $current_input.blur(addBufferToValues);

    $current_input.keypress(function (e) {
      // only grab enter
      if (e.which != 13) {
        return;
      }

      addBufferToValues();
      return false; // don't submit the form
    });

    $input.after($values_container);
    $values_container.after($current_input);

    /*
     * Updates the input and labels from the `values` array
     */
    var refresh = function () {
      $input.attr('value', values.join(';'));
      regenerateLabels();
    };

    /*
     * Regenerates the name labels
     */
    var regenerateLabels = function () {
      $values_container.html('');

      for (var i = 0; i < values.length; ++i) {
        var $link = $('<a href="#" class="person-label label label-primary"></a>');
        $values_container.append($link);

        $link.text(values[i]);
        $link.append('<span class="glyphicon glyphicon-remove"></span>');

        // wrapped in a closure otherwise i is always values.length
        (function (i) {
          $link.click(function () {
            // when the label is clicked, remove it from the list
            values.splice(i, 1);
            refresh();

            return false;
          });
        })(i);
      }

      // if there are no people listed, add the 'required' attribute to the input field
      // otherwise, clear the 'required' attribute
      $current_input.prop('required', values.length == 0);
    };

    // for edit forms we need to add the labels of the people that are already there
    regenerateLabels();
  }

  $(function () {
    var $artists = $('#comic_artists__row');
    if ($artists.length) {
      updateManyField($artists);
    }

    var $writers = $('#comic_writers__row');
    if ($writers.length) {
      updateManyField($writers);
    }
  });
})();
