from tornado.auth import TwitterMixin, GoogleMixin, FacebookGraphMixin
from tornado.auth import HTTPRedirect

class UserDenied(Exception): pass

class Twitter(object):
    def __init__(self, key, secret, callback_url):
        self.settings = {
            'twitter_consumer_key': key,
            'twitter_consumer_secret': secret,
        }
        self.callback_url = callback_url

    def redirect(self, environ, cookie_monster):
        auth = TwitterMixin(environ, self.settings, cookie_monster)

        try:
            auth.authorize_redirect(self.callback_url)
        except HTTPRedirect, e:
            return e.url
        return None

    def get_user(self, environ, cookie_monster):
        auth = TwitterMixin(environ, self.settings, cookie_monster)

        if auth.get_argument('denied', None):
            raise UserDenied()

        container = {}

        def get_user_callback(user):
            container['user'] = user

        auth.get_authenticated_user(get_user_callback)
        return container.get('user')


class Facebook(object):
    def __init__(self, key, secret, callback_url, scope='email'):
        self.settings = {
            'facebook_api_key': key,
            'facebook_secret': secret,
        }
        self.callback_url = callback_url
        self.scope = scope

    def redirect(self, environ):
        auth = FacebookGraphMixin(environ)
        try:
            auth.authorize_redirect(
                redirect_uri=self.callback_url,
                client_id=self.settings['facebook_api_key'],
                extra_params={'scope': self.scope})

        except HTTPRedirect, e:
            return e.url
        return None

    def get_user(self, environ):
        auth = FacebookGraphMixin(environ)

        if auth.get_argument('error', None):
            raise UserDenied()

        container = {}
        def get_user_callback(user):
            container['user'] = user

        auth.get_authenticated_user(
                redirect_uri=self.callback_url,
                client_id=self.settings['facebook_api_key'],
                client_secret=self.settings['facebook_secret'],
                code=auth.get_argument('code'),
                callback=get_user_callback)

        return container.get('user')
    
    def api(self, environ, path, args, access_token):
        auth = FacebookGraphMixin(environ)

        container = {}
        def callback(response):
            container['response'] = response

        auth.facebook_request(path, callback, access_token, args)
        return container.get('response')


class Google(object):
    def __init__(self, key, secret, callback_url, scope='name,email,language,username'):
        self.settings = {
            'google_consumer_key': key,
            'google_consumer_secret': secret,
        }
        self.callback_url = callback_url
        self.scope = scope

    def redirect(self, environ):
        auth = GoogleMixin(environ)
        ax_attrs = self.scope.split(',')
        try:
            auth.authenticate_redirect(
                    callback_uri=self.callback_url,
                    ax_attrs=ax_attrs)
        except HTTPRedirect, e:
            return e.url
        return None

    def get_user(self, environ):
        auth = GoogleMixin(environ)

        if auth.get_argument('error', None):
            raise UserDenied()

        container = {}
        def get_user_callback(user):
            container['user'] = user

        auth.get_authenticated_user(get_user_callback)

        return container.get('user')

