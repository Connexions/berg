from pathlib import Path
import tempfile
from unittest import mock

from lxml import etree
import pytest

from nebu.cli.bake import INPUT_FILE, OUTPUT_FILE


@pytest.fixture
def bake_cleanup(request, datadir):
    def cleanup():
        for filename in (INPUT_FILE, OUTPUT_FILE):
            output_file = datadir / filename
            if output_file.is_file():
                output_file.unlink()
    cleanup()
    request.addfinalizer(cleanup)


@pytest.fixture
def easybake_oven():
    patcher = mock.patch('nebu.cli.bake.cnxeasybake')
    easybake = patcher.start()
    yield easybake.Oven
    patcher.stop()


def create_collection_mathified_xhtml(datadir):
    with (datadir / INPUT_FILE).open('w') as f:
        f.write('<html xmlns="http://www.w3.org/1999/xhtml"><head></head>'
                '<body></body></html>')


class TestBakeCmd:
    def test_wo_mathified_xhtml(self, datadir, invoker, bake_cleanup,
                                easybake_oven):
        from nebu.cli.main import cli
        args = ['bake', str(datadir)]
        with mock.patch('nebu.cli.bake.mathify') as mathify:
            mathify.side_effect = lambda *args, **kwargs: \
                create_collection_mathified_xhtml(datadir)
            result = invoker(cli, args)
            assert mathify.called

        assert result.exit_code == 0
        easybake_oven.assert_called_with(None)
        assert (datadir / OUTPUT_FILE).exists()

    def test_w_mathified_xhtml(self, datadir, invoker, bake_cleanup,
                               easybake_oven):
        create_collection_mathified_xhtml(datadir)
        from nebu.cli.main import cli
        with tempfile.NamedTemporaryFile() as f:
            args = ['bake', '-r', f.name, str(datadir)]
            with mock.patch('nebu.cli.bake.mathify') as mathify:
                result = invoker(cli, args)
                assert not mathify.called

        assert result.exit_code == 0
        easybake_oven.assert_called_with(f.name)
        oven = easybake_oven(f.name)
        assert oven.bake.called
        assert etree.tostring(oven.bake.call_args[0][0]) == \
            b'<html xmlns="http://www.w3.org/1999/xhtml"><head/><body/></html>'
        assert (datadir / OUTPUT_FILE).exists()

    def test_w_style(self, datadir, invoker, bake_cleanup, easybake_oven):
        create_collection_mathified_xhtml(datadir)
        from nebu.cli.main import cli
        with tempfile.NamedTemporaryFile() as f:
            with tempfile.NamedTemporaryFile() as g:
                style = g.name
                args = ['bake', '-r', f.name, '-s', style, str(datadir)]
                result = invoker(cli, args)

        assert result.exit_code == 0
        assert (datadir / OUTPUT_FILE).exists()
        with (datadir / OUTPUT_FILE).open('r') as f:
            root = etree.parse(f)
            link = root.xpath('/x:html/x:head/x:link', namespaces={
                'x': 'http://www.w3.org/1999/xhtml'})[0]
            assert link.attrib['href'] == str(Path(style).absolute())
            assert link.attrib['type'] == 'text/css'
            assert link.attrib['rel'] == 'stylesheet'
