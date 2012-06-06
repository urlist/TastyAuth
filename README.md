TastyAuth
=========

TastyAuth is an extremely tasty python module to integrate third-party
authentication schemes (read: Google, Twitter and Facebook auth).

TastyAuth is designed to be framework agnostic: it just exposes plain
functions that you can use *everywhere* WSGI is supported.
The only hard dependency is [WebOb](http://www.webob.org/).

The goal is to give to the developer an easy API to authenticate users and to
retrieve some basic information about them: the `dict` returned by the
`(twitter|facebook|google).get_user` method will always be structured as
follows.


    user['attrs'] { ... the raw data retrieved from the third party ... }

    user['parsed'] = {

        # user unique ID, this is valid for the third party, if you
        # need to store it in your Model as a primary key prepend a
        # string to identify the provider
        'uid': 'UID',

        'email': 'foo@example.org'
        'username': 'foobar',
        'screen_name': 'Foo Bar',
        'first_name': 'Foo',
        'last_name': 'Bar',
        'language': 'it'
        'profile_url': 'https://example.org/foobar',
        'profile_image_small': 'https://example.org/foobar-small.png',
        'profile_image': 'https://example.org/foobar.png',
    }

Show me teh code
----------------
A typical setup is the following (I am using
[Bottle](https://github.com/defnull/bottle) but you can use whatever you want)


    from bottle import route, redirect, request
    from tastyauth import Facebook, UserDenied, NegotiationError
    from pprint import pformat

    facebook = Facebook('fb-key', 'fb-secret',
                        'http://127.0.0.1:8080/facebook/callback', 'email')

    @route('/facebook/login')
    def facebook_login():
        # request.environ is a WSGI environment
        url = facebook.redirect(request.environ)
        redirect(url)

    @route('/facebook/callback')
    def facebook_callback(provider):
        try:
            # get the current user!
            user = facebook.get_user(request.environ)
        except UserDenied:
            # the user refused to log
            return 'User denied'
        except NegotiationError:
            # oops, something nasty happend
            return 'Negotiation error, maybe expired stuff'

        return '<pre>{0}</pre>'.format(pformat(user))


You can find a working example under the `example` dir. If you want to run the
example provided, do not forget to:

    pip install bottle

or drop the bottle module somewhere in your `PYHONPATH`.

Quick start
-----------

Clone the repo, `git clone git@github.com:twitter/bootstrap.git`,
or [download the latest release](https://github.com/vrde/TastyAuth/zipball/master).

If you are using [virtualenv](http://www.virtualenv.org/) cd to the directory
containing `setup.py` and install TastyAuth's dependencies with:

    pip install -e .

Pip will install just [WebOb](http://www.webob.org/)


Request a key for authenticating with:
 * Facebok on https://developers.facebook.com/docs/reference/api/permissions/
 * Twitter on http://www.example.org/twitter/callback
 * Google on https://www.google.com/accounts/ManageDomains

Put all your Facebook, Twitter and Google keys somewhere in your configuration.

For every third-party service you wish to use for your webapp, you need to
define a redirect and a callback controller. The API is really easy to
use, please take a look to the example provided.

