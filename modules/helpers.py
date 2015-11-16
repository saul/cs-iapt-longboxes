from gluon.globals import current
from gluon.http import redirect, HTTP
from gluon.html import URL


def flash_and_redirect_back(flash, default=URL('default', 'index'), avoid=None):
    current.session.flash = flash

    referrer = current.request.env.http_referer

    if referrer and (avoid is None or avoid not in referrer):
        redirect(current.request.env.http_referer)
    else:
        redirect(default)


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
