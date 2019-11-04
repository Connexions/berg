from pathlib import Path

import pretend
import pytest

from nebu.config import (
    INITIAL_DEFAULT_CONFIG,
    discover_settings,
    prepare,
    Config, Environ,
)


TESTING_CONFIG = """\
[settings]
foo = bar

[environ-local]
url = http://localhost:6543

[environ-dev]
url = https://dev.cnx.org
"""

@pytest.fixture
def testee_config_filepath(tmp_path):
    """Returns a filepath with the contents of ``TESTING_CONFIG`` within"""
    filepath = tmp_path / "nebu.ini"
    with filepath.open('w') as fb:
        fb.write(TESTING_CONFIG)
    return filepath


class TestDiscoverSettings:

    def test_home_dir_config_found(self, tmpdir, monkeypatch):
        loc = Path(str(tmpdir / 'config.ini'))
        monkeypatch.setattr('nebu.config.CONFIG_FILE_LOC', loc)
        monkeypatch.setattr('os.environ', {})

        with loc.open('w') as fb:
            fb.write(TESTING_CONFIG)

        settings = discover_settings()

        expected_settings = {
            '_config_file': loc,
            'environs': {
                'dev': {'url': 'https://dev.cnx.org'},
                'local': {'url': 'http://localhost:6543'},
            },
            'settings': {'foo': 'bar'},
        }
        assert settings == expected_settings

    def test_environ_var_config(self, tmpdir, monkeypatch):
        loc = Path(str(tmpdir / 'config.ini'))
        monkeypatch.setattr('os.environ', {'NEB_CONFIG': str(loc)})

        with loc.open('w') as fb:
            fb.write(TESTING_CONFIG)

        settings = discover_settings()

        expected_settings = {
            '_config_file': loc,
            'environs': {
                'dev': {'url': 'https://dev.cnx.org'},
                'local': {'url': 'http://localhost:6543'},
            },
            'settings': {'foo': 'bar'},
        }
        assert settings == expected_settings

    def test_missing_config(self, tmpdir, monkeypatch):
        loc = Path(str(tmpdir / 'config.ini'))
        monkeypatch.setattr('nebu.config.CONFIG_FILE_LOC', loc)
        monkeypatch.setattr('os.environ', {})

        settings = discover_settings()

        expected_settings = {
            '_config_file': loc,
            'environs': {
                'dev': {'url': 'https://dev.cnx.org'},
                'qa': {'url': 'https://qa.cnx.org'},
                'staging': {'url': 'https://staging.cnx.org'},
                'prod': {'url': 'https://cnx.org'},
                'content01': {'url': 'https://content01.cnx.org'},
                'content02': {'url': 'https://content02.cnx.org'},
                'content03': {'url': 'https://content03.cnx.org'},
                'content04': {'url': 'https://content04.cnx.org'},
                'content05': {'url': 'https://content05.cnx.org'},
                'staged': {'url': 'https://staged.cnx.org'},
            },
            'settings': {},
        }
        assert settings == expected_settings

        with loc.open('r') as fb:
            assert fb.read() == INITIAL_DEFAULT_CONFIG

    def test_missing_config_and_parent_directory(self, tmpdir, monkeypatch):
        loc = Path(str(tmpdir)) / '.config' / 'config.ini'
        monkeypatch.setattr('nebu.config.CONFIG_FILE_LOC', loc)
        monkeypatch.setattr('os.environ', {})

        settings = discover_settings()

        expected_settings = {
            '_config_file': loc,
            'environs': {
                'dev': {'url': 'https://dev.cnx.org'},
                'qa': {'url': 'https://qa.cnx.org'},
                'staging': {'url': 'https://staging.cnx.org'},
                'prod': {'url': 'https://cnx.org'},
                'content01': {'url': 'https://content01.cnx.org'},
                'content02': {'url': 'https://content02.cnx.org'},
                'content03': {'url': 'https://content03.cnx.org'},
                'content04': {'url': 'https://content04.cnx.org'},
                'content05': {'url': 'https://content05.cnx.org'},
                'staged': {'url': 'https://staged.cnx.org'},
            },
            'settings': {},
        }
        assert settings == expected_settings

        with loc.open('r') as fb:
            assert fb.read() == INITIAL_DEFAULT_CONFIG


class TestPrepare:

    def test(self, monkeypatch):
        settings_marker = object()
        discover_settings = pretend.call_recorder(lambda: settings_marker)
        monkeypatch.setattr('nebu.config.discover_settings',
                            discover_settings)

        env = prepare()

        assert callable(env['closer'])
        assert env['settings'] is settings_marker


class TestEnviron:

    def test_objecticity(self):
        name = 'foo'
        url = 'http://example.com'
        e = Environ(name, url)
        assert e.name == name
        assert e.url == url

    def test_repr(self):
        name = 'foo'
        url = 'http://example.com'
        e = Environ(name, url)

        expected = "Environ('{}', **{{'url': '{}'}})".format(name, url)
        assert repr(e) == expected

    def test_as_dict(self):
        url = 'http://example.com'
        e = Environ('foo', url)
        assert e.as_dict() == {'url': url}

    def test_equal(self):
        name = 'foo'
        url = 'http://example.com'
        e1 = Environ(name, url)
        e2 = Environ(name, url)
        assert e1 is not e2  # identity inequality
        assert e1 == e2

    def test_not_equal_in_name(self):
        name = 'foo'
        url = 'http://example.com'
        e1 = Environ(name, url)
        e2 = Environ('bar', url)
        assert e1 is not e2  # identity inequality
        assert e1 != e2

    def test_not_equal_in_property(self):
        name = 'foo'
        url = 'http://example.com'
        e1 = Environ(name, url)
        e2 = Environ(name, 'http://example.ORG')
        assert e1 is not e2  # identity inequality
        assert e1 != e2


class TestConfig:

    def test_from_file(self, testee_config_filepath):
        config = Config.from_file(testee_config_filepath)

        assert config.settings == {'foo': 'bar'}

        expected_environs = {
            'local': Environ('local', **{'url': 'http://localhost:6543'}),
            'dev': Environ('dev', **{'url': 'https://dev.cnx.org'}),
        }
        assert config.environs == expected_environs

    def test_get_env(self, testee_config_filepath):
        config = Config.from_file(testee_config_filepath)

        expected = Environ('local', **{'url': 'http://localhost:6543'})
        assert config.get_env('local') == expected
