import datetime

db.define_table('box',
                Field('owner', 'reference auth_user', required=True, notnull=True, writable=False),
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY(), unique=True),
                Field('private', 'boolean', required=True, notnull=True),
                Field('created', 'datetime', required=True, notnull=True, default=datetime.datetime.now, writable=False)
                )


class BoxVirtualFields:
    def is_unfiled(self):
        return self.box.name == 'Unfiled'


db.box.virtualfields.append(BoxVirtualFields())


def on_user_created(form):
    db.box.insert(owner=form.vars.id, name='Unfiled', private=True)

auth.settings.register_onaccept.append(on_user_created)
