import os
import shutil
from pathlib import Path

import click
from cnxepub.formatters import (
    HTMLFormatter,
    SingleHTMLFormatter,
)
from cnxepub.models import flatten_to_documents

from ._common import common_params, logger
from ..models.binder import Binder
from ..models.utils import scan_for_id_mapping
from ..utils import relative_path


def produce_collection_xhtml(binder, output_dir):
    collection_xhtml = output_dir / 'collection.assembled.xhtml'
    with collection_xhtml.open('wb') as fb:
        fb.write(bytes(SingleHTMLFormatter(binder)))

    return collection_xhtml


def provide_supporting_files(input_dir, output_dir, binder):
    documents = {doc.id: doc for doc in flatten_to_documents(binder)}
    for id, filepath in scan_for_id_mapping(input_dir).items():
        (output_dir / id).symlink_to(relative_path(filepath.parent, output_dir))
        with (output_dir / '{}.xhtml'.format(id)).open('wb') as fb:
            fb.write(bytes(HTMLFormatter(documents[id])))


@click.command(name='assemble')
@common_params
@click.argument('input-dir', type=click.Path(exists=True))
@click.argument('output-dir', type=click.Path())
@click.pass_context
def assemble(ctx, input_dir, output_dir):
    """Assembles litezip structure data into a single-page-html file.

    This also stores the intermediary results alongside the resulting
    assembled single-page-html.

    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if output_dir.exists():
        confirm_msg = (
            "This will remove '{}', continue?"
            .format(str(output_dir))
        )
        click.confirm(confirm_msg, abort=True, err=True)
        shutil.rmtree(str(output_dir))
    output_dir.mkdir()

    collection_xml = input_dir / 'collection.xml'
    binder = Binder.from_collection_xml(collection_xml)

    # Write the collection.xml symlink to the output directory
    (output_dir / 'collection.xml').symlink_to(relative_path(collection_xml, output_dir))

    # Write the binder out as a single-page-html
    collection_xhtml = produce_collection_xhtml(binder, output_dir)
    logger.debug('Wrote: {}'.format(str(collection_xhtml.resolve())))

    # Write the symbolic links for modules to the output directory
    provide_supporting_files(input_dir, output_dir, binder)

    return 0