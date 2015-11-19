import os

from customvalidators import IS_FEWER_WORDS

db.define_table('writer',
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY())
                )

db.define_table('artist',
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY())
                )

db.define_table('publisher',
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY())
                )

db.define_table('comic',
                Field('publisher', db.publisher, required=True, notnull=True, requires=IS_IN_DB(db, 'publisher.id', '%(name)s', zero='Choose publisher')),
                Field('title', required=True, notnull=True, requires=IS_NOT_EMPTY()),
                Field('issue', 'integer', required=True, notnull=True, requires=IS_INT_IN_RANGE(1, 1e100), default=1),
                Field('description', 'text', required=True, notnull=True, requires=[IS_FEWER_WORDS(300), IS_NOT_EMPTY()]),
                Field('cover_image', 'upload', required=True, notnull=True, requires=[IS_IMAGE(maxsize=(300, 400))], uploadfolder=os.path.join('applications', request.application, 'uploads'))
                )


class ComicVirtualFields:
    def owner(self):
        return db(db.comicbox.comic == self.comic.id)(db.box.id == db.comicbox.box)(db.auth_user.id == db.box.owner).select(db.auth_user.ALL).first()

    def boxes(self):
        user_id = auth.user.id if auth.user else 0
        return db(db.comicbox.comic == self.comic.id)(db.box.id == db.comicbox.box)((db.box.private == False) | (db.box.owner == user_id)).select(db.box.ALL)

    def full_name(self):
        return '%s #%s' % (self.comic.title, self.comic.issue)

    def url(self):
        return URL('comic', 'view', args=[self.comic.id])


db.comic.virtualfields.append(ComicVirtualFields())


db.define_table('comicbox',
                Field('box', db.box, required=True, notnull=True),
                Field('comic', db.comic, required=True, notnull=True))

db.define_table('comicwriter',
                Field('comic', db.comic, required=True, notnull=True),
                Field('writer', db.writer, required=True, notnull=True)
                )

db.define_table('comicartist',
                Field('comic', db.comic, required=True, notnull=True),
                Field('artist', db.artist, required=True, notnull=True)
                )
