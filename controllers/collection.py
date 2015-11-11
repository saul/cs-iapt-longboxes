from helpers import flash_and_redirect_back, get_or_404


def view():
    logged_in_user = auth.user.id if auth.user else 0

    if request.args(0) is None:
        # Must be logged in to view your own collection
        if not logged_in_user:
            raise HTTP(401)

        user = db.auth_user[auth.user.id]
    else:
        user = get_or_404(db.auth_user, request.args(0))

    public_boxes = db((db.box.owner == user.id) & ((db.box.private == False) | (db.box.owner == logged_in_user))).select()
    return {'user': user, 'public_boxes': public_boxes}


@auth.requires_login()
def all():
    comics = db(db.comic.id == db.comicbox.comic)(db.box.id == db.comicbox.box)(db.box.owner == auth.user.id).select(db.comic.ALL, groupby=db.comic.id)

    return {'comics': comics}
