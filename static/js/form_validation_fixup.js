/*
 * Unfortunately, web2py's bootstrap3 form styles don't use the correct error
 * classes.
 *
 * This small script adds the correct styles to erroneous form inputs on
 * document load.
 */

(function() {
  'use strict';

  $(function() {
    $('.error_wrapper').each(function() {
      var $this = $(this);
      $this.addClass('help-block');
      $this.parents('.form-group').addClass('has-error');

      var $modalParent = $this.parents('.modal');
      if ($modalParent.length) {
        $modalParent.modal('show');
      }
    });
  });
})();
