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
                Field('cover_image', 'upload', required=True, notnull=True, requires=[IS_IMAGE()], uploadfolder='uploads/')
                )

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
