from urlparse import urlparse
import re

from tastyauth.tornado.auth import TwitterMixin, GoogleMixin, FacebookGraphMixin
from tastyauth.tornado.auth import HTTPRedirect
import logging

log = logging.getLogger('tastyauth.auth')

class AuthException(Exception): pass
class UserDenied(AuthException): pass
class NegotiationError(AuthException): pass

class Twitter(object):

    PROFILE_URL_BASE = 'https://twitter.com/'

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
            log.debug('Redirecting Twitter user to {0}'.format(e.url))
            return e.url
        except KeyError, e:
            log.warning('Negotiation error for Twitter user')
            raise NegotiationError
        return None

    def get_user(self, environ, cookie_monster):
        auth = TwitterMixin(environ, self.settings, cookie_monster)

        if auth.get_argument('denied', None):
            log.debug('User denied attributes exchange')
            raise UserDenied()

        container = {}

        def get_user_callback(user):
            if not user:
                raise NegotiationError()

            container['attrs'] = user

            profile_image_small = user['profile_image_url_https']
            profile_image = re.sub('_normal(?=.\w+$)', '', profile_image_small)

            container['parsed'] = {
                'uid': user['id_str'],
                'email': None,
                'username': user['username'],
                'screen_name': user['screen_name'],
                'first_name': user.get('name'),
                'last_name': None,
                'language': user.get('lang'),
                'profile_url': self.PROFILE_URL_BASE + user['username'],
                'profile_image_small': profile_image_small,
                'profile_image': profile_image,
            }

        auth.get_authenticated_user(get_user_callback)
        return container


class Facebook(object):

    PROFILE_IMAGE_URL = 'https://graph.facebook.com/{id}/picture?type=large'
    PROFILE_IMAGE_SMALL_URL = 'https://graph.facebook.com/{id}/picture'

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
            log.debug('Redirecting Facebook user to {0}'.format(e.url))
            return e.url
        return None

    def get_user(self, environ):
        auth = FacebookGraphMixin(environ)

        if auth.get_argument('error', None):
            log.debug('User denied attributes exchange')
            raise UserDenied()

        container = {}

        def get_user_callback(user):
            if not user:
                raise NegotiationError()

            container['attrs'] = user
            container['parsed'] = {
                'uid': user['id'],
                'email': user.get('email'),
                'username': user.get('username'),
                'screen_name': user.get('name'),
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'language': user.get('locale'),
                'profile_url': user.get('link'),
                'profile_image_small': self.PROFILE_IMAGE_SMALL_URL.format(id=user['id']),
                'profile_image': self.PROFILE_IMAGE_URL.format(id=user['id']),
            }

        auth.get_authenticated_user(
                redirect_uri=self.callback_url,
                client_id=self.settings['facebook_api_key'],
                client_secret=self.settings['facebook_secret'],
                code=auth.get_argument('code'),
                callback=get_user_callback)

        return container
    
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
        auth = GoogleMixin(environ, self.settings)
        ax_attrs = self.scope.split(',')
        try:
            auth.authenticate_redirect(
                    callback_uri=self.callback_url,
                    ax_attrs=ax_attrs)
        except HTTPRedirect, e:
            log.debug('Redirecting Google user to {0}'.format(e.url))
            return e.url
        return None

    def get_user(self, environ):
        auth = GoogleMixin(environ, self.settings)

        if auth.get_argument('error', None):
            log.debug('User denied attributes exchange')
            raise UserDenied()

        container = {}
        def get_user_callback(user):
            if not user:
                raise NegotiationError()

            container['attrs'] = user
            query_string = urlparse(user['claimed_id']).query
            params = dict(param.split('=') for param in query_string.split('&'))
            container['parsed'] = {
                'uid': params['id'],
                'email': user['email'],
                'username': None,
                'screen_name': user.get('first_name'),
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'language': user.get('locale'),
                'profile_url': None,
                'profile_image_small': None,
                'profile_image': None
            }

        auth.get_authenticated_user(get_user_callback)

        return container

