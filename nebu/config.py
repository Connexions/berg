import configparser
import os
from pathlib import Path


CONFIG_FILE_LOC = Path.home() / '.config/nebuchadnezzar.ini'
CONFIG_SECTION_ENVIRON_PREFIX = 'environ-'

INITIAL_DEFAULT_CONFIG = """\
[settings]

# [environ-<short-name>]
# url = <base-url-to-the-environment>

[environ-dev]
url = https://dev.cnx.org

[environ-qa]
url = https://qa.cnx.org

[environ-staging]
url = https://staging.cnx.org

[environ-prod]
url = https://cnx.org

[environ-content01]
url = https://content01.cnx.org

[environ-content02]
url = https://content02.cnx.org

[environ-content03]
url = https://content03.cnx.org

[environ-content04]
url = https://content04.cnx.org

[environ-content05]
url = https://content05.cnx.org

[environ-staged]
url = https://staged.cnx.org
"""


def _write_default_config_file():
    """Writes the default config file to the filesystem."""
    CONFIG_FILE_LOC.parent.mkdir(exist_ok=True)  # create ~/.config
    with CONFIG_FILE_LOC.open('w') as fb:
        fb.write(INITIAL_DEFAULT_CONFIG)


def _read_props_from_filepath(config_filepath):
    """Given a ``config_filepath`` containing INI formatted settings,
    read these in and return a dictionary of properties.

    """
    config = configparser.ConfigParser()
    config.read(str(config_filepath))

    props = {
        '_config_file': config_filepath.resolve(),
        'settings': {},
        'environs': {
            # short-name : settings
        },
    }
    for section in config.sections():
        if not section.startswith(CONFIG_SECTION_ENVIRON_PREFIX):
            continue  # ignore all other sections
        short_name = section[len(CONFIG_SECTION_ENVIRON_PREFIX):]
        props['environs'][short_name] = dict(config[section])
    for k, v in config['settings'].items():
        props['settings'][k] = v
    return props


def discover_settings():
    """Discover settings from environment variables and config files

    TODO Document what env vars are actually looked at.
    TODO Document config file location lookup

    :param dict settings: An existing settings value
    :return: dictionary of settings
    :rtype: dict

    """
    # Lookup the location of the configuration file.
    # If NEB_CONFIG is defined the file specified is used.
    config_filepath = os.environ.get('NEB_CONFIG', None)
    if config_filepath:
        config_filepath = Path(config_filepath)
        assert config_filepath.exists()
    else:
        config_filepath = CONFIG_FILE_LOC
        if not config_filepath.exists():
            _write_default_config_file()
    props = _read_props_from_filepath(config_filepath)
    return props


def prepare():
    """This function prepares an application/script for use.

    :return: an environment dictionary containing the newly created
             ``settings`` and a ``closer`` function.
    :rtype: dict

    """
    # Get the settings
    settings = discover_settings()

    def closer():  # pragma: no cover
        pass

    return {'closer': closer, 'settings': settings}


class Environ(object):
    """Configuration for a specific deployed environment"""

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        r = (
            "{self.__class__.__name__}"
            "('{self.name}', **{kwargs})".format(
                self=self,
                kwargs=self.as_dict(),
            )
        )
        return r

    def __eq__(self, other):
        is_same_name = self.name == other.name
        is_same_info = self.as_dict() == other.as_dict()
        return is_same_name and is_same_info

    def as_dict(self):
        attrs = ['url']
        return {a: getattr(self, a, None) for a in attrs}


class Config(object):
    """Configuration for the whole application"""

    def __init__(self, settings, environs=[]):
        self.settings = settings
        self._environs = environs

    @classmethod
    def from_file(cls, file):
        p = _read_props_from_filepath(file)
        environs = [Environ(k, **v) for k, v in p['environs'].items()]
        return cls(p['settings'], environs)

    @property
    def environs(self):
        return {e.name: e for e in self._environs}

    def get_env(self, env):
        return self.environs.get(env, None)
