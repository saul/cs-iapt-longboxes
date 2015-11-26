from helpers import flash, flash_and_redirect_back, get_or_404, add_element_required_attr


def _validate_box_form(form):
    """Ensures that the name of the box does not conflict with any other box. Case insensitive."""
    if not db(db.box.owner == auth.user.id)(db.box.name.like(form.vars.name))(db.box.id != form.record).isempty():
        form.errors.name = 'Box already exists'


def _unfiled_box():
    """Gets the 'Unfiled' box for the current logged in user."""
    return db.box((db.box.name == 'Unfiled') & (db.box.owner == auth.user.id))


def view():
    """
    GET /box/view/:id

    Views a box, ensures that the logged in user has permission to view it.
    """

    user_id = auth.user.id if auth.is_logged_in() else 0
    box = get_or_404(db.box, ((db.box.id == request.args(0)) & ((db.box.owner == user_id) | (db.box.private == False))))

    # find all comics in this box
    comics = db(db.comicbox.comic == db.comic.id)(db.comicbox.box == box.id).select(db.comic.ALL)
    comic_ids = map(lambda c: c.id, comics)

    # find all the comics owned by this user that aren't already in the box
    other_comics = db(db.comic.id == db.comicbox.comic)(db.box.id == db.comicbox.box)(
        db.box.owner == user_id).select(db.comic.ALL, groupby=db.comic.id)
    other_comics = filter(lambda c: c.id not in comic_ids, other_comics)

    user_owned = user_id == box.owner.id
    can_edit = user_owned and not box.is_unfiled

    if can_edit:
        rename_form = SQLFORM(db.box, box, fields=['name'], showid=False)
        add_element_required_attr(db.box, rename_form)

        if rename_form.process(onvalidation=_validate_box_form).accepted:
            flash('info', 'Box renamed successfully.', request.env['PATH_INFO'])
        elif rename_form.errors:
            flash('danger', 'Form has errors.')
    else:
        rename_form = None

    return {
        'box': box,
        'comics': comics,
        'other_comics': other_comics,
        'can_edit': can_edit,
        'user_owned': user_owned,
        'rename_form': rename_form
    }


@auth.requires_login()
def create():
    """
    POST /box/create

    Creates a new box for this user.
    """

    form = SQLFORM(db.box, fields=['name', 'private'])
    add_element_required_attr(db.box, form)

    form.vars.owner = auth.user

    if form.process(onvalidation=_validate_box_form).accepted:
        flash('success', 'Created box.', URL('box', 'view', args=[form.vars.id]))
    elif form.errors:
        flash('danger', 'Form has errors.')

    return {
        'form': form
    }


@auth.requires_login()
def delete():
    """
    POST /box/delete/:id

    Deletes a box and ensures any comics that were in only this box are moved to 'Unfiled'.
    """

    box = get_or_404(db.box, request.args(0), owner=auth.user.id)

    if box.is_unfiled:
        flash('danger', 'You cannot delete the Unfiled box.', box.url)

    comics = [x.comic for x in box.comicbox.select()]

    # Find the comics who only reside in the box we're deleting
    count = db.comicbox.id.count()
    comic_just_in_box = db(db.comicbox.comic.belongs(comics)).select(db.comicbox.id, count, groupby=db.comicbox.comic)
    comic_just_in_box = filter(lambda row: row[count] == 1, comic_just_in_box)

    # Move all comics that only reside in the box we're deleting to 'Unfiled'
    for record in comic_just_in_box:
        record.comicbox.update_record(box=_unfiled_box().id)

    # Remove all comics from this box
    db(db.comicbox.box == box.id).delete()

    # Delete the old box
    box.delete_record()

    flash('info', '%s box deleted.' % box.name, URL('collection', 'view', args=[auth.user.id]))


@auth.requires_login()
def add_comic():
    """
    POST /box/add_comic

    Adds a comic to a box, also may create or update an existing box if 'new box' was specified.
    The 'comic' POST var can occur multiple times to add many comics to a single box in one operation.
    """

    # Create a new box
    if request.post_vars['box'] == 'new':
        target_box = db.box(db.box.name.like(request.post_vars['name']) & (db.box.owner == auth.user.id))
        private = bool(request.post_vars['private'])

        if target_box:
            target_box.update(private=private)
        else:
            target_box_id = db.box.insert(name=request.post_vars['name'], owner=auth.user.id, private=private)
            target_box = db.box[target_box_id]
    else:
        target_box = get_or_404(db.box, request.post_vars['box'], owner=auth.user.id)

    raw_comic = request.post_vars['comic']

    if raw_comic is None:
        flash_and_redirect_back('warning', 'No comics selected.')

    comics = raw_comic if isinstance(raw_comic, list) else [raw_comic]

    for source_comic_id in comics:
        source_comic = get_or_404(db.comic, source_comic_id)

        # Is the comic already in the box we want to add it to?
        if db.comicbox((db.comicbox.box == target_box.id) & (db.comicbox.comic == source_comic.id)):
            flash_and_redirect_back('warning', 'This comic already exists in %s.' % target_box.name)

        # If this user doesn't own the comic, duplicate it
        if db(db.box.owner == auth.user.id)(db.comicbox.box == db.box.id)(db.comicbox.comic == source_comic.id).isempty():
            target_comic_id = db.comic.insert(
                publisher=source_comic.publisher,
                title=source_comic.title,
                issue=source_comic.issue,
                description=source_comic.description,
                cover_image=source_comic.cover_image
            )

            for comicwriter in source_comic.comicwriter.select():
                db.comicwriter.insert(writer=comicwriter.writer, comic=target_comic_id)

            for comicartist in source_comic.comicartist.select():
                db.comicartist.insert(artist=comicartist.artist, comic=target_comic_id)

        elif target_box.is_unfiled:
            return flash_and_redirect_back('danger',
                                           'This comic cannot be added to "Unfiled" as it is already belongs to a box.')

        else:
            target_comic_id = source_comic.id

        # Add comic to box
        db.comicbox.insert(comic=target_comic_id, box=target_box.id)

        # Find the Unfiled box for this user
        if not target_box.is_unfiled:
            db((db.comicbox.comic == target_comic_id) & (db.comicbox.box == _unfiled_box().id)).delete()

    flash_text = 'Added comic%s to %s.' % ('s' if len(comics) > 1 else '', target_box.name)

    # if we just duplicated this comic, redirect to the new comic
    if source_comic.owner.id != auth.user.id:
        flash('success', flash_text, URL('comic', 'view', args=[target_comic_id]))

    # otherwise, redirect back
    else:
        flash_and_redirect_back('success', flash_text)


@auth.requires_login()
def remove_comic():
    """
    POST /box/remove_comic

    Removes a comic from a box and ensures it is in at least the 'Unfiled' box.
    """

    box = get_or_404(db.box, request.post_vars['box'], owner=auth.user.id)
    comic = get_or_404(db.comic, request.post_vars['comic'])

    if box.is_unfiled:
        flash_and_redirect_back('danger', 'A comic cannot be removed from the Unfiled box.')

    db(db.comicbox.box == box.id)(db.comicbox.comic == comic.id).delete()

    # if the comic no longer belongs to any boxes, add it to the 'Unfiled' box
    if db(db.comicbox.comic == comic.id).isempty():
        db.comicbox.insert(comic=comic.id, box=_unfiled_box().id)

    flash_and_redirect_back('info', 'Removed %s from %s.' % (comic.full_name, box.name))


@auth.requires_login()
def set_privacy():
    """
    GET /box/set_privacy/:id?privacy=(private|public)

    Updates the privacy of a box from private <-> public.
    """
    box = get_or_404(db.box, request.args(0), owner=auth.user.id)

    new_privacy_str = request.get_vars['privacy']
    privacy_str_to_private_bool = {
        'private': True,
        'public': False
    }

    new_private_value = privacy_str_to_private_bool.get(new_privacy_str)
    if new_private_value is None:
        flash_and_redirect_back('danger', 'Invalid privacy option for box.')

    box.update_record(private=new_private_value)
    flash_and_redirect_back('info', 'Box is now %s.' % new_privacy_str)
