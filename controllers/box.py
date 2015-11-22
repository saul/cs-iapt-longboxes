from helpers import flash, flash_and_redirect_back, get_or_404, add_element_required_attr


def _validate_box_form(form):
    if not db(db.box.owner == auth.user.id)(db.box.name == form.vars.name).isempty():
        form.errors.name = 'Box already exists'


def view():
    user_id = auth.user.id if auth.is_logged_in() else 0
    box = get_or_404(db.box, ((db.box.id == request.args(0)) & ((db.box.owner == user_id) | (db.box.private == False))))

    comics = db(db.comicbox.comic == db.comic.id)(db.comicbox.box == box.id).select(db.comic.ALL)

    user_owned = user_id == box.owner.id
    can_edit = user_owned and box.name != 'Unfiled'

    if can_edit:
        rename_form = SQLFORM(db.box, box, fields=['name'], showid=False)
        add_element_required_attr(db.box, rename_form)

        if rename_form.process(onvalidation=_validate_box_form).accepted:
            flash('info', 'Box renamed successfully.', request.env['PATH_INFO'])

        if rename_form.errors:
            flash('danger', 'Form has errors.')
    else:
        rename_form = None

    return {
        'box': box,
        'comics': comics,
        'can_edit': can_edit,
        'user_owned': user_owned,
        'rename_form': rename_form
    }


@auth.requires_login()
def create():
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
    box = get_or_404(db.box, request.args(0), owner=auth.user.id)

    if box.is_unfiled:
        flash('danger', 'You cannot delete the Unfiled box.', box.url)

    # Find the Unfiled box for this user
    unfiled_box = db.box((db.box.name == 'Unfiled') & (db.box.owner == auth.user.id))

    comics = [x.comic for x in box.comicbox.select()]

    # Find the comics who only reside in the box we're deleting
    count = db.comicbox.id.count()
    comic_just_in_box = db(db.comicbox.comic.belongs(comics)).select(db.comicbox.id, count, groupby=db.comicbox.comic)
    comic_just_in_box = filter(lambda row: row[count] == 1, comic_just_in_box)

    # Move all comics that only reside in the box we're deleting to 'Unfiled'
    for record in comic_just_in_box:
        record.comicbox.update_record(box=unfiled_box.id)

    # Remove all comics from this box
    db(db.comicbox.box == box.id).delete()

    # Delete the old box
    box.delete_record()

    flash('info', 'Box deleted.', URL('collection', 'view', args=[auth.user.id]))


@auth.requires_login()
def add_comic():
    if request.post_vars['box'] == 'new':
        target_box = db.box(name=request.post_vars['name'], owner=auth.user.id)
        private = bool(request.post_vars['private'])

        if target_box:
            target_box.update(private=private)
        else:
            target_box_id = db.box.insert(name=request.post_vars['name'], owner=auth.user.id, private=private)
            target_box = db.box[target_box_id]
    else:
        target_box = get_or_404(db.box, request.post_vars['box'], owner=auth.user.id)

    source_comic = get_or_404(db.comic, request.post_vars['comic'])

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
        unfiled_box = db.box((db.box.name == 'Unfiled') & (db.box.owner == auth.user.id))
        db((db.comicbox.comic == target_comic_id) & (db.comicbox.box == unfiled_box.id)).delete()

    flash('success', 'Added comic to box.', URL('comic', 'view', args=[target_comic_id]))


@auth.requires_login()
def remove_comic():
    box = get_or_404(db.box, request.post_vars['box'], owner=auth.user.id)
    comic = get_or_404(db.comic, request.post_vars['comic'])

    if box.is_unfiled:
        flash_and_redirect_back('danger', 'A comic cannot be removed from the Unfiled box.')

    db(db.comicbox.box == box.id)(db.comicbox.comic == comic.id).delete()

    # if the comic no longer belongs to any boxes, add it to the 'Unfiled' box
    if db(db.comicbox.comic == comic.id).isempty():
        unfiled_box = db.box((db.box.name == 'Unfiled') & (db.box.owner == auth.user.id))
        db.comicbox.insert(comic=comic.id, box=unfiled_box.id)

    flash_and_redirect_back('info', 'Removed comic from box.')


@auth.requires_login()
def set_privacy():
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
