import os

from customvalidators import IS_FEWER_WORDS

# ------------------------------------------------------------------------
#  Writer
# ------------------------------------------------------------------------
db.define_table('writer',
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY())
                )


class WriterVirtualFields:
    def search_url(self):
        """URL to search for comics that this writer contributed to."""
        return URL('comic', 'search', vars={'search': 'writer:' + self.writer.name})


db.writer.virtualfields.append(WriterVirtualFields())

# ------------------------------------------------------------------------
#  Artist
# ------------------------------------------------------------------------
db.define_table('artist',
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY())
                )


class ArtistVirtualFields:
    def search_url(self):
        """URL to search for comics that this artist contributed to."""
        return URL('comic', 'search', vars={'search': 'artist:' + self.artist.name})


db.artist.virtualfields.append(ArtistVirtualFields())

# ------------------------------------------------------------------------
#  Publisher
# ------------------------------------------------------------------------

db.define_table('publisher',
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY())
                )


class PublisherVirtualFields:
    def search_url(self):
        """URL to search for comics that this publisher published."""
        return URL('comic', 'search', vars={'search': 'publisher:' + self.publisher.name})


db.publisher.virtualfields.append(PublisherVirtualFields())

# ------------------------------------------------------------------------
#  Comic
# ------------------------------------------------------------------------
db.define_table('comic',
                Field('publisher', db.publisher,
                      required=True, notnull=True,
                      requires=IS_IN_DB(db, 'publisher.id', '%(name)s', zero='Choose publisher')),
                Field('title', required=True, notnull=True, requires=IS_NOT_EMPTY()),
                Field('issue', 'integer', required=True, notnull=True, requires=IS_INT_IN_RANGE(1, 1e100), default=1,
                      comment='Must be a number greater than 0.'),
                Field('description', 'text',
                      required=True, notnull=True,
                      requires=[IS_FEWER_WORDS(300), IS_NOT_EMPTY()]),
                Field('cover_image', 'upload',
                      required=True, notnull=True,
                      requires=[IS_IMAGE(maxsize=(300, 400))],
                      uploadfolder=os.path.join(os.path.dirname(__file__), '..', 'uploads'),
                      comment='Image dimensions must not exceed 300x400 pixels.')
                )


class ComicVirtualFields:
    def owner(self):
        """Returns the owner of this comic."""
        return db(db.comicbox.comic == self.comic.id)(db.box.id == db.comicbox.box)(
            db.auth_user.id == db.box.owner).select(db.auth_user.ALL).first()

    def boxes(self):
        """Returns the boxes that contain this comic that the logged in user can see."""
        user_id = auth.user.id if auth.user else 0

        return db(db.comicbox.comic == self.comic.id)(db.box.id == db.comicbox.box)(
            (db.box.private == False) | (db.box.owner == user_id)).select(db.box.ALL)

    def full_name(self):
        return '%s #%s' % (self.comic.title, self.comic.issue)

    def url(self):
        """Returns the URL to view this comic."""
        return URL('comic', 'view', args=[self.comic.id])

    def cover_url(self):
        """Returns the URL to the cover image."""
        return URL('default', 'download', args=[self.comic.cover_image])


db.comic.virtualfields.append(ComicVirtualFields())

# ------------------------------------------------------------------------
#  Comic Box
# ------------------------------------------------------------------------
db.define_table('comicbox',
                Field('box', db.box, required=True, notnull=True),
                Field('comic', db.comic, required=True, notnull=True))

# ------------------------------------------------------------------------
#  Comic Writer
# ------------------------------------------------------------------------
db.define_table('comicwriter',
                Field('comic', db.comic, required=True, notnull=True),
                Field('writer', db.writer, required=True, notnull=True)
                )

# ------------------------------------------------------------------------
#  Comic Artist
# ------------------------------------------------------------------------
db.define_table('comicartist',
                Field('comic', db.comic, required=True, notnull=True),
                Field('artist', db.artist, required=True, notnull=True)
                )
