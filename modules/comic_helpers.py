from gluon.globals import current


def user_can_view(db, comic_id, user_id):
    return not db(db.comicbox.box == db.box.id)(db.comicbox.comic == comic_id)((db.box.owner == user_id) | (db.box.private == False)).isempty()


def user_can_edit(db, comic_id, user_id):
    return not db(db.box.owner == user_id)(db.comicbox.box == db.box.id)(db.comicbox.comic == comic_id).isempty()
