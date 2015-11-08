from gluon.globals import current
from gluon.http import redirect
from gluon.html import URL


def flash_and_redirect_back(flash):
    current.response.flash = flash

    if current.request.env.http_referer:
        redirect(current.request.env.http_referer)
    else:
        redirect(URL('default', 'index'))
