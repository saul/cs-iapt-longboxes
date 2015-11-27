# Longboxes Y0070944

The following tree details all files that were added or changed for the Longboxes application. 

```
  + controllers/ - Controllers and their functions to manage back-end logic
    | box.py
    | collection.py
    | comic.py
    | default.py
  + models/ - Models defining the database schema for the application.
    | 0_db.py - Main initialisation file. `0_` prefix is to ensure it is called before other modules.
    | box.py
    | comic.py
  + static/
    + css/
      | bootstrap-longboxes.css - Bootstrap 3 recompiled with changes made in static/less/variables.less
      | longboxes.css - Single stylesheet for entire application. Compiled from static/less/longboxes.less
    + less/
      | <Bootstrap 3 LESS source files...>
      | variables.less - Bootstrap 3 variables that have been changed to make the Longboxes application look more unique.
      | longboxes.less - Single stylesheet for entire application.
    + js/
      | comic_form.js - JavaScript to manage word counting and people lists on the comic form.
      | form_validation_fixup.js - Fixes web2py SQLFORMs incorrect usage of Bootstrap classes on forms.
      | longboxes.js - Initialises Bootstrap tooltips and handles confirmation dialogs for destructive actions. 
      | new_box_form.js - Handles the `Create new` dropdown option when adding a comic to new box.
  + views/
    + box/ - Views for the box controller functions
      | ...
    + collection/ - View for the collection controller function
      | ...
    + comic/ - Views for the comic controller functions
      | ...
    + default/
      | index.html - Index page of the entire application.
      | user.html - Enables web2pys auth system to use the Longboxes layout
    | box_listgroup.html - Partial template to list boxes in a Bootstrap `list-group`
    | comics_preview.html - Partial template to list comic previews in a Bootstrap grid
    | longboxes_layout.html - Base layout template for the entire application
    | longboxes_singlecol.html - Extends from longboxes_layout.html: has a single column layout
    | longboxes_sidebar.html - Extends from longboxes_singlecol.html: adds a sidebar column
```
