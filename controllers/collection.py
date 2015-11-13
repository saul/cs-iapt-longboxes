from helpers import flash_and_redirect_back, get_or_404


def view():
    logged_in_user = auth.user.id if auth.user else 0

    if request.args(0) is None:
        # Must be logged in to view your own collection
        if not logged_in_user:
            redirect(URL('default', 'user', args=['login'], vars={'_next': URL()}))

        redirect(URL('collection', 'view', args=[auth.user.id]))

    user = get_or_404(db.auth_user, request.args(0))

    comics = db(db.comic.id == db.comicbox.comic)(db.box.id == db.comicbox.box)(db.box.owner == user.id)((db.box.owner == logged_in_user) | (db.box.private == False)).select(db.comic.ALL, groupby=db.comic.id)

    boxes = db((db.box.owner == user.id) & ((db.box.private == False) | (db.box.owner == logged_in_user))).select()

    return {
        'user': user,
        'boxes': boxes,
        'comics': comics
    }
