def index():
    # Find 5 largest public boxes
    count = db.comicbox.box.count()
    largest = db(db.comicbox.box == db.box.id)(db.box.private == False).select(db.box.ALL, groupby=db.comicbox.box, orderby=~count, limitby=(0, 5))

    # Find 5 most recent public boxes
    recent = db(db.box.private == False).select(orderby=~db.box.created, limitby=(0, 5))

    return {'largest': largest, 'recent': recent}


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return {'form': auth()}


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
