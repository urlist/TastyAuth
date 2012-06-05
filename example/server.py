import settings

import bottle
from bottle import route, redirect, request, response, debug, run
from pprint import pformat

from tastyauth import Twitter, Facebook, Google, UserDenied, NegotiationError

twitter = Twitter(
            settings.TWITTER_KEY,
            settings.TWITTER_SECRET,
            settings.TWITTER_CALLBACK)

facebook = Facebook(
            settings.FACEBOOK_KEY,
            settings.FACEBOOK_SECRET,
            settings.FACEBOOK_CALLBACK,
            settings.FACEBOOK_SCOPE)

google = Google(
            settings.GOOGLE_KEY,
            settings.GOOGLE_SECRET,
            settings.GOOGLE_CALLBACK,
            settings.GOOGLE_SCOPE)

mapping = {'twitter': twitter, 'facebook': facebook, 'google': google}


class CookieMonster(object):

    def get_cookie(self, name, default=None):
        return request.get_cookie(name, default)

    def set_cookie(self, name, value):
        response.set_cookie(name, value)

    def delete_cookie(self, name):
        response.delete_cookie(name)



@route('/')
def home():
    return """<html>
    <head>
        <meta name="google-site-verification" content="{0}" />
    </head>
    <body>
    <ul>
        <li><a href="/twitter/login">twitter</a></li>
        <li><a href="/google/login">google</a></li>
        <li><a href="/facebook/login">facebook</a></li>
    </ul>
    </body>
</html>""".format(settings.GOOGLE_SITE_VERIFICATION)


@route('/facebook/login')
def facebook_login():
    url = facebook.redirect(request.environ)
    redirect(url)


@route('/twitter/login')
def twitter_login():
    url = twitter.redirect(request.environ, CookieMonster())
    redirect(url)


@route('/google/login')
def google_login():
    url = google.redirect(request.environ)
    redirect(url)


@route('/:provider/callback')
def provider_callback(provider):
    try:
        user = mapping[provider].get_user(request.environ)
    except UserDenied:
        return 'User denied'
    except NegotiationError:
        return 'Negotiation error, maybe expired stuff'

    return '<pre>{0}</pre>'.format(pformat(user))

if __name__ == '__main__':
    debug(True)
    app = bottle.app()
    run(app=app)

