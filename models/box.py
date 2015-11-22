import datetime

db.define_table('box',
                Field('owner', 'reference auth_user', required=True, notnull=True, writable=False),
                Field('name', required=True, notnull=True, requires=IS_NOT_EMPTY()),
                Field('private', 'boolean', required=True, notnull=True,
                      comment='Private boxes can only be seen by you.'),
                Field('created', 'datetime', required=True, notnull=True, default=datetime.datetime.now, writable=False)
                )


class BoxVirtualFields:
    def is_unfiled(self):
        return self.box.name == 'Unfiled'

    def comic_count(self):
        """The number of comics that this box contains."""
        return db(db.comicbox.comic == db.comic.id)(db.comicbox.box == self.box.id).count()

    def url(self):
        """URL to view this box."""
        return URL('box', 'view', args=[self.box.id])


db.box.virtualfields.append(BoxVirtualFields())


#
# When a user registers, create a private 'Unfiled' box for them.
#
def on_user_created(form):
    db.box.insert(owner=form.vars.id, name='Unfiled', private=True)


auth.settings.register_onaccept.append(on_user_created)
