from gluon.globals import current
from gluon.http import redirect, HTTP
from gluon.html import URL


def flash_and_redirect_back(flash):
    current.session.flash = flash

    if current.request.env.http_referer:
        redirect(current.request.env.http_referer)
    else:
        redirect(URL('default', 'index'))


def get_or_404(model, id, **kwargs):
    record = model(id, **kwargs)
    if not record:
        raise HTTP(404)
    return record


def get_or_create(model, **fields):
    record = model(**fields)
    if record:
        return record.id
    return model.insert(**fields)
