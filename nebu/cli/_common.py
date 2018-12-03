from functools import wraps

import click
import json
import re
import requests

from urllib.parse import urlparse, urlunparse

from ..logger import configure_logging, logger
from .exceptions import UnknownEnvironment


console_logging_config = {
    'version': 1,
    'formatters': {
        'cli': {
            'format': '%(message)s',
        },
    },
    'filters': {},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'cli',
            'filters': [],
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        'nebuchadnezzar': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': 0,
        },
        'litezip': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': 0,
        },
    },
    'root': {
        'level': 'NOTSET',
        'handlers': [],
    },
}


def common_params(func):
    @click.option('-v', '--verbose', is_flag=True, help='enable verbosity')
    @click.pass_context
    @wraps(func)
    def wrapper(ctx, verbose, *args, **kwargs):
        set_verbosity(verbose)
        logger.debug('Using the configuration file at {}'
                     .format(ctx.obj['settings']['_config_file']))
        return func(*args, **kwargs)
    return wrapper


def confirm(prompt="OK to continue? [Y/N] "):
    """
    Ask for Y/N answer.
    returns bool
    """
    answer = ""
    while answer not in ["y", "n"]:
        answer = input(prompt).lower()
    return answer == "y"


def get_base_url(context, environ_name):
    try:
        return context.obj['settings']['environs'][environ_name]['url']
    except KeyError:
        raise UnknownEnvironment(environ_name)


def get_base_url_from_url(url):
    """Take advantage of webview settings.js to find archive api server"""
    # HACK this whole thing is a bit of a hack - it takes advantage of
    # webview serving a settings.js file that defines an anonymous
    # function that returns a json data tree. This extracts it and makes
    # it python-json friendly
    settings_pr = urlparse(url)._replace(path='/scripts/settings.js')

    if settings_pr.netloc.startswith('legacy'):  # Remove 'legacy[.-]'
        settings_pr = settings_pr._replace(netloc=settings_pr.netloc[7:])

    settings_url = urlunparse(settings_pr)
    # Fetch the JS, chop out the definition
    s = requests.get(settings_url).text
    s = s[s.find('return ') + 7:]
    # we now point at the { after the return
    # Find the other end of the nested json structure.
    lvl = 0
    for i, c in enumerate(s):
        if c == '{':
            lvl += 1
        elif c == '}':
            lvl -= 1
        if lvl == 0:  # First char was a {, so doesn't just fall through
            break
    # Fixup quoting of everything, remove comment and blank lines
    set_str = ' '.join([line for line in
                        re.sub("'", '"',
                               re.sub(r'(\w+):', r'"\1":',
                                      re.sub(r': ([a-zA-Z._]+)', r': "\1"',
                                             s[:i + 1]))).split('\n')
                        if '//' not in line and line != ''])
    settings = json.loads(set_str)
    if 'port' in settings['cnxarchive']:
        host = 'https://{host}:{port}'.format(**settings['cnxarchive'])
    else:
        host = 'https://{host}'.format(**settings['cnxarchive'])
    return host


def set_verbosity(verbose):
    config = console_logging_config.copy()
    if verbose:
        level = 'DEBUG'
    else:
        level = 'INFO'
    config['loggers']['nebuchadnezzar']['level'] = level
    configure_logging(config)
