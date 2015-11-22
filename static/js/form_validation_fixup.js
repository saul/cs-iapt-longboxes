/*
 * Unfortunately, web2py's bootstrap3 form styles don't use the correct
 * Bootstrap error classes.
 *
 * This script adds the correct styles to erroneous form inputs on
 * document load.
 */

(function() {
  'use strict';

  $(function() {
    $('.error_wrapper').each(function() {
      var $this = $(this);

      $this.addClass('help-block');
      $this.parents('.form-group').addClass('has-error');

      // if a form in a modal has errors, show the modal
      var $modalParent = $this.parents('.modal');
      if ($modalParent.length) {
        $modalParent.modal('show');
      }
    });
  });
})();
