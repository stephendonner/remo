# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py
from funfactory.settings_base import *

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'common': (
            'css/remo/foundation.css',
            'css/remo/tabzilla.css',
            ),
        'common_ie': (
            'css/remo/ie.css',
            ),
        'remo': (
            'css/remo/app.css',
            )
    },
    'js': {
        'common': (
            'js/webtrends.js',
            'js/modernizr.foundation.js',
            'js/foundation.js',
            'js/activate.browserid.js',
            'js/tabzilla.js',
             # Our app.js is always last to override stuff
            'js/app.js',
            ),
    }
}

# Defines the views served for root URLs.
ROOT_URLCONF = 'remo.urls'

INSTALLED_APPS = ['south'] + \
                 list(INSTALLED_APPS) + [
                     # Application base, containing global templates.
                     'django.contrib.messages',
                     'django.contrib.markup',

                     'remo.base',
                     'remo.profiles',
                     'remo.featuredrep',
                     'remo.remozilla',
                     'remo.reports',

                     'django_browserid',
                     ]

# Because Jinja2 is the default template loader, add any non-Jinja templated
# apps here:
JINGO_EXCLUDE_APPS = [
    'admin',
]

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['lhtml'] = [
#    ('**/templates/**.lhtml',
#        'tower.management.commands.extract.extract_tower_template'),
# ]

# # Use this if you have localizable HTML files:
# DOMAIN_METHODS['javascript'] = [
#    # Make sure that this won't pull in strings from external libraries you
#    # may use.
#    ('media/js/**.js', 'javascript'),
# ]

LOGGING = dict(loggers=dict(playdoh = {'level': logging.DEBUG}))

# Set profile module
AUTH_PROFILE_MODULE = 'profiles.UserProfile'

# Add BrowserID as authentication backend
AUTHENTICATION_BACKENDS = ('django_browserid.auth.BrowserIDBackend',
                           'django.contrib.auth.backends.ModelBackend',
                           )

# Required for BrowserID. Very important security feature
SITE_URL = 'https://reps.mozilla.org'

# Remove LocaleURLMiddleware since we are not localing our website
MIDDLEWARE_CLASSES = filter(
    lambda x: x != 'funfactory.middleware.LocaleURLMiddleware',
    MIDDLEWARE_CLASSES)

MIDDLEWARE_CLASSES += ('django.contrib.messages.middleware.MessageMiddleware',
                       'remo.base.middleware.RegisterMiddleware')

TEMPLATE_CONTEXT_PROCESSORS += (
    'django_browserid.context_processors.browserid_form',
    'django.contrib.messages.context_processors.messages')

# Instruct session-csrf to always produce tokens for anonymous users
ANON_ALWAYS = True

LOGIN_REDIRECT_URL_FAILURE = '/login/failed/'

FROM_EMAIL = 'reps@mozilla.com'

ADMINS = (
    ('Mozilla Reps', 'reps@mozilla.com'),
)

MANAGERS = ADMINS
