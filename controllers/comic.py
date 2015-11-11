from helpers import flash_and_redirect_back, get_or_create


class ComicForm:
    def __init__(self, record=None):
        if record:
            self.id = record.id

            artists = record.comicartist(db.artist.id == db.comicartist.artist).select()
            record.artists = ';'.join(map(lambda row: row.artist.name, artists))

            writers = record.comicwriter(db.writer.id == db.comicwriter.writer).select()
            record.writers = ';'.join(map(lambda row: row.writer.name, writers))

            record.publisher = record.publisher.name
        else:
            self.id = None

        fields = [field for field in db.comic if field.name != 'publisher']

        # Only show a 'box' field if we're creating the comic
        if not self.id:
            user_boxes = [(row.id, row.name) for row in db(db.box.owner == auth.user.id).select(orderby=db.box.id)]
            fields.insert(0, Field('box', 'reference box', requires=IS_IN_SET(user_boxes, zero=None)))

        fields.insert(3, Field('publisher', 'string', requires=IS_NOT_EMPTY()))
        fields.insert(4, Field('artists', 'string', requires=IS_NOT_EMPTY()))
        fields.insert(5, Field('writers', 'string', requires=IS_NOT_EMPTY()))

        self.form = SQLFORM.factory(
            *fields,
            record=record,
            formstyle='table3cols',
            table_name='comic'
        )

    def _on_success(self, form):
        # Create the publisher if it doesn't exist already
        publisher_id = get_or_create(db.publisher, name=form.vars.publisher)

        comic_fields = db.comic._filter_fields(form.vars)
        comic_fields['publisher'] = publisher_id

        # Update the record if it's already in the database
        if self.id:
            db(db.comic.id == self.id).update(**comic_fields)
        else:
            self.id = db.comic.insert(**comic_fields)

            # Add the comic to the box
            db.comicbox.insert(comic=self.id, box=form.vars.box)

        self._process_writers_and_artists()

    def process(self, **kwargs):
        kwargs['onsuccess'] = self._on_success
        return self.form.process(**kwargs)

    def _process_writers_and_artists(self):
        db(db.comicartist.comic == self.id).delete()

        for artist_name in self.form.vars.artists.split(';'):
            artist_id = get_or_create(db.artist, name=artist_name)
            db.comicartist.insert(comic=self.id, artist=artist_id)

        db(db.comicwriter.comic == self.id).delete()

        for writer_name in self.form.vars.writers.split(';'):
            writer_id = get_or_create(db.writer, name=writer_name)
            db.comicwriter.insert(comic=self.id, writer=writer_id)


@auth.requires_login()
def create():
    form = ComicForm()

    if form.process().accepted:
        session.flash = 'Created comic'
        redirect(URL('comic', 'view', args=[form.id]))
    elif form.form.errors:
        response.flash = 'Form has errors'

    return {'form': form.form}


@auth.requires_login()
def delete():
    comic = get_or_404(db.comic, request.args(0))

    if not comic_helpers.user_can_edit(db, comic.id, auth.user.id):
        flash_and_redirect_back('You cannot delete a comic you did not create.')

    comic.delete_record()
    flash_and_redirect_back('Comic deleted')


@auth.requires_login()
def edit():
    comic = get_or_404(db.comic, request.args(0))

    # Ensure the user owns this comic
    if db(db.box.owner == auth.user.id)(db.comicbox.box == db.box.id)(db.comicbox.comic == comic.id).isempty():
        flash_and_redirect_back('You cannot edit a comic you did not create.')

    form = ComicForm(comic)

    if form.process().accepted:
        session.flash = 'Comic updated successfully'
        redirect(URL('comic', 'view', args=[form.id]))
    elif form.form.errors:
        response.flash = 'Form has errors'

    return {'form': form.form}


def view():
    comic = get_or_404(db.comic, request.args(0))

    # Ensure that the user either owns the comic or that it belongs to a public box
    user_id = auth.user.id if auth.is_logged_in() else 0
    if db(db.comicbox.box == db.box.id)(db.comicbox.comic == comic.id)((db.box.owner == user_id) | (db.box.private == False)).isempty():
        raise HTTP(404)

    return {'record': comic}
