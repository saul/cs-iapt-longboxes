from gluon.globals import current
from gluon.validators import IS_NOT_EMPTY
from gluon.html import URL
from gluon.http import redirect, HTTP


def flash(flash_class, text, redirect_url=None):
    """Updates the flash key and optionally redirects to another URL."""
    flash_info = {
        'class': flash_class,
        'text': text
    }

    if redirect:
        current.session.flash = flash_info
        redirect(redirect_url)
    else:
        current.response.flash = flash_info


def flash_and_redirect_back(flash_class, text, default=URL('default', 'index'), avoid=None):
    """Flashes and redirects to the URL in the referrer, optionally avoiding some URLs."""
    referrer = current.request.env.http_referer

    if referrer and (avoid is None or avoid not in referrer):
        redirect_url = current.request.env.http_referer
    else:
        redirect_url = default

    flash(flash_class, text, redirect_url)


def get_or_404(model, id, **kwargs):
    """Gets the first instance that matches a criteria or raises 404."""
    record = model(id, **kwargs)
    if not record:
        raise HTTP(404)
    return record


def get_or_create(model, **fields):
    """Gets the first instance that matches a criteria or creates it."""
    record = model(**fields)
    if record:
        return record.id
    return model.insert(**fields)


def add_element_required_attr(model, form):
    """Adds the HTML5 required attribute to all field values which must not be empty."""

    def is_not_empty(field):
        # Some fields have multiple validators
        if isinstance(field.requires, (list, tuple)):
            requires = field.requires
        else:
            requires = [field.requires]

        for validator in requires:
            if isinstance(validator, IS_NOT_EMPTY):
                return True

    required_fields = filter(is_not_empty, model)
    elements = map(lambda f: form.element(_name=f.name), required_fields)

    for element in filter(bool, elements):
        element['_required'] = 'required'
