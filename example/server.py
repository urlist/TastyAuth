import settings

import bottle
from bottle import route, redirect, request, response, debug, run

from tastyauth import Twitter, Facebook, Google

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
        <meta name="google-site-verification" content="%s" />
    </head>
    <body>
    <ul>
        <li><a href="/twitter/login">twitter</a></li>
        <li><a href="/google/login">google</a></li>
        <li><a href="/facebook/login">facebook</a></li>
    </ul>
    </body>
</html>""" % settings.GOOGLE_SITE_VERIFICATION

@route('/facebook/login')
def facebook_login():
    url = facebook.redirect(request.environ)
    redirect(url)

@route('/facebook/callback')
def facebook_callback():
    user = facebook.get_user(request.environ)
    return user

@route('/twitter/login')
def twitter_login():
    url = twitter.redirect(request.environ, CookieMonster())
    redirect(url)

@route('/twitter/callback')
def twitter_callback():
    user = twitter.get_user(request.environ, CookieMonster())
    return user


@route('/google/login')
def google_login():
    url = google.redirect(request.environ)
    print 'redirecting to...', url
    redirect(url)

@route('/google/callback')
def google_callback():
    user = google.get_user(request.environ)
    return user


debug(True)
app = bottle.app()
run(app=app)

