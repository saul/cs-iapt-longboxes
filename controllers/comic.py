import comic_helpers
from helpers import flash, flash_and_redirect_back, get_or_create, get_or_404, add_element_required_attr


class ComicForm:
    """
    Form to represent a comic.

    Automatically handles artist/writers many-to-many relationship and enforces referential integrity.
    """

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
            table_name='comic',
            showid=False
        )

        add_element_required_attr(db.comic, self.form)

    def _on_success(self, form):
        """Called when a form is validated correctly."""

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

        # Update the writers and artists many-to-many relationship
        self._process_writers_and_artists()

    def process(self, **kwargs):
        kwargs['onsuccess'] = self._on_success
        return self.form.process(**kwargs)

    def _process_writers_and_artists(self):
        """Update the writers and artists many-to-many relationship."""

        db(db.comicartist.comic == self.id).delete()

        for artist_name in self.form.vars.artists.split(';'):
            artist_id = get_or_create(db.artist, name=artist_name)
            db.comicartist.insert(comic=self.id, artist=artist_id)

        db(db.comicwriter.comic == self.id).delete()

        for writer_name in self.form.vars.writers.split(';'):
            writer_id = get_or_create(db.writer, name=writer_name)
            db.comicwriter.insert(comic=self.id, writer=writer_id)

        # find the IDs of all the artists and writers
        all_artist_ids = set(map(lambda x: x.id, db().select(db.artist.id)))
        all_writer_ids = set(map(lambda x: x.id, db().select(db.writer.id)))

        # find the IDs of the artists and writers that are referenced by comics
        used_artist_ids = set(map(lambda x: x.artist, db().select(db.comicartist.artist, distinct=True)))
        used_writer_ids = set(map(lambda x: x.writer, db().select(db.comicwriter.writer, distinct=True)))

        # clean up - delete any unused artists or writers
        db(db.artist.id.belongs(all_artist_ids - used_artist_ids)).delete()
        db(db.writer.id.belongs(all_writer_ids - used_writer_ids)).delete()


@auth.requires_login()
def create():
    """
    POST /comic/create?box=:box_id

    Creates a new comic.
    """

    form = ComicForm()

    # Pre-select the box that the user wants to add to
    if not form.form.vars.box and request.get_vars['box']:
        form.form.vars.box = get_or_404(db.box, request.get_vars['box'], owner=auth.user.id).id

    if form.process().accepted:
        flash('success', 'Created comic.', URL('comic', 'view', args=[form.id]))
    elif form.form.errors:
        flash('danger', 'Form has errors.')

    return {
        'form': form.form,
        'owner': auth.user,
    }


@auth.requires_login()
def delete():
    """
    POST /comic/delete/:id

    Deletes a comic.
    """
    comic = get_or_404(db.comic, request.args(0))

    if not comic_helpers.user_can_edit(db, comic.id, auth.user.id):
        flash_and_redirect_back('danger', 'You cannot delete a comic you did not create.')

    comic.delete_record()
    flash_and_redirect_back('info', 'Deleted %s.' % comic.full_name,
                            default=URL('collection', 'view', args=[auth.user.id]),
                            avoid='/comic/view')


@auth.requires_login()
def edit():
    """
    POST /comic/edit/:id

    Updates comic details.
    """

    comic = get_or_404(db.comic, request.args(0))

    # Ensure the user owns this comic
    if not comic_helpers.user_can_edit(db, comic.id, auth.user.id):
        flash_and_redirect_back('danger', 'You cannot edit a comic you did not create.')

    form = ComicForm(comic)

    if form.process().accepted:
        flash('info', 'Comic updated successfully.', comic.url)
    elif form.form.errors:
        flash('danger', 'Form has errors.')

    return {
        'form': form.form,
        'comic': comic,
        'owner': auth.user,
    }


def view():
    """
    GET /comic/view/:id

    Views the details for a specific comic.
    """

    comic = get_or_404(db.comic, request.args(0))

    # Ensure that the user either owns the comic or that it belongs to a public box
    user_id = auth.user.id if auth.is_logged_in() else 0
    if not comic_helpers.user_can_view(db, comic.id, user_id):
        raise HTTP(404)

    available_boxes = db(db.box.owner == user_id).select()

    return {
        'comic': comic,
        'boxes': db(db.comicbox.comic == comic.id)(db.box.id == db.comicbox.box)(
            (db.box.private == False) | (db.box.owner == user_id)).select(db.box.ALL),
        'artists': db(db.comicartist.comic == comic.id)(db.artist.id == db.comicartist.artist).select(db.artist.ALL),
        'writers': db(db.comicwriter.comic == comic.id)(db.writer.id == db.comicwriter.writer).select(db.writer.ALL),
        'owner': db(db.comicbox.comic == comic.id)(db.box.id == db.comicbox.box)(
            db.auth_user.id == db.box.owner).select(db.auth_user.ALL).first(),
        'can_edit': comic_helpers.user_can_edit(db, comic.id, user_id),
        'available_boxes': available_boxes
    }


def search():
    """
    GET /comic/search?search=:query

    Searches all public comics across a number of criteria.
    """

    original_search = request.get_vars.get('search', '')

    user_id = auth.user.id if auth.is_logged_in() else 0

    # generate a base query which finds all comics that the logged in user has permission to see
    base_query = db(db.comic.id == db.comicbox.comic)(db.comicbox.box == db.box.id)(
        (db.box.private == False) | (db.box.owner == user_id))

    # basic partial matching
    fuzzy_like = lambda f, q: f.like('%{0}%'.format(q))

    # generate the queries for each criteria
    queries = {
        'title': lambda q: base_query(fuzzy_like(db.comic.title, q)),
        'publisher': lambda q: base_query(db.publisher.id == db.comic.publisher)(fuzzy_like(db.publisher.name, q)),
        'writer': lambda q: base_query(db.comicwriter.comic == db.comic.id)(db.writer.id == db.comicwriter.writer)(
            fuzzy_like(db.writer.name, q)),
        'artist': lambda q: base_query(db.comicartist.comic == db.comic.id)(db.artist.id == db.comicartist.artist)(
            fuzzy_like(db.artist.name, q)),
    }

    only_field, search = None, original_search

    search_parts = original_search.split(':', 1)

    # determine which (if any) criteria to search against
    if len(search_parts) > 1:
        if search_parts[0] in queries:
            only_field, search = search_parts
        else:
            flash('danger', 'Invalid criteria "%s", expected one of: %s' % (search_parts[0], ', '.join(queries.keys())))

    if only_field:
        # filter using a single criteria
        comics = queries[only_field](search).select(db.comic.ALL, distinct=True)
    else:
        # combine all queries to a single set of comics
        query_results = map(lambda q: q(search).select(db.comic.ALL, distinct=True), queries.values())
        comics = reduce(lambda c, q: c | q, query_results)

    return {
        'original_search': original_search,
        'search': search,
        'comics': comics,
        'only_field': only_field
    }
