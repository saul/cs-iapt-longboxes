import datetime

db.define_table('box',
                Field('owner', 'reference auth_user', required=True, notnull=True, writable=False),
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY()),
                Field('private', 'boolean', required=True, notnull=True),
                Field('created', 'datetime', required=True, notnull=True, default=datetime.datetime.now, writable=False)
                )
