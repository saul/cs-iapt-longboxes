def user_can_view(db, comic_id, user_id):
    """Can a specific user view a comic?"""
    return not db(db.comicbox.box == db.box.id)(db.comicbox.comic == comic_id)(
        (db.box.owner == user_id) | (db.box.private == False)).isempty()


def user_can_edit(db, comic_id, user_id):
    """Does a specific user have permission to edit a comic's details?"""
    return not db(db.box.owner == user_id)(db.comicbox.box == db.box.id)(db.comicbox.comic == comic_id).isempty()
