from helpers import flash_and_redirect_back


@auth.requires_login()
def create():
    fields = [field for field in db.comic]

    # TODO: add writer and artist
    # TODO: calculate which boxes this comic can be a part of
    fields += [
        Field('box', 'reference box', requires=IS_IN_SET(customer_types, zero=None, sort=False)),
    ]

    form = SQLFORM.factory(
        *fields,
        formstyle='table3cols',
        table_name='comic'
    )

    if form.process().accepted:
        comic_id = db.customer.insert(**db.comic._filter_fields(form.vars))

        session.flash = 'Created comic'

        redirect(URL('comic', 'view', args=[comic_id]))
    elif form.errors:
        response.flash = 'Form has errors'

    return {'form': form}


@auth.requires_login()
def delete():
    pass


@auth.requires_login()
def edit():
    comic = db.comic(request.args(0))
    if not comic:
        raise HTTP(404)

    # Ensure the user owns this comic
    if db(db.box.owner == auth.user.id)(db.comicbox.box == db.box.id)(db.comicbox.comic == comic.id).isempty():
        flash_and_redirect_back('You cannot edit a comic you did not create.')

    form = SQLFORM(db.comic, comic, formstyle='table3cols')

    if form.process().accepted:
        response.flash = 'Comic updated successfully'
    elif form.errors:
        response.flash = 'Form has errors'

    return {'form': form}


@auth.requires_login()
def view():
    pass
