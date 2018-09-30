from pathlib import Path
from urllib.parse import urlparse, urlunparse
import os

import click
import requests

from ..logger import logger
from ._common import common_params, confirm, get_base_url
from .exceptions import *  # noqa: F403


@click.command()
@common_params
@click.option('-d', '--output-dir', type=click.Path(),
              help="output directory name (can't previously exist)")
@click.argument('env')
@click.argument('col_id')
@click.argument('col_version')
@click.pass_context
def get(ctx, env, col_id, col_version, output_dir):
    """download and expand the completezip to the current working directory"""
    # Determine the output directory

    # Build the base url
    base_url = get_base_url(ctx, env)
    parsed_url = urlparse(base_url)
    sep = len(parsed_url.netloc.split('.')) > 2 and '-' or '.'
    url_parts = [
        parsed_url.scheme,
        'archive{}{}'.format(sep, parsed_url.netloc),
    ] + list(parsed_url[2:])
    base_url = urlunparse(url_parts)

    col_hash = '{}/{}'.format(col_id, col_version)
    # Fetch metadata
    url = '{}/content/{}'.format(base_url, col_hash)
    resp = requests.get(url)
    if resp.status_code >= 400:
        raise MissingContent(col_id, col_version)
    col_metadata = resp.json()
    uuid = col_metadata['id']
    version = col_metadata['version']

    # Generate full output dir as soon as we have the version
    if output_dir is None:
        output_dir = Path.cwd() / '{}_1.{}'.format(col_id, version)
    else:
        output_dir = Path(output_dir)

    # ... and check if it's already been downloaded
    if output_dir.exists():
        raise ExistingOutputDir(output_dir)

    # Fetch extras (includes head and downloadable file info)
    url = '{}/extras/{}@{}'.format(base_url, uuid, version)
    resp = requests.get(url)

    if col_version == 'latest':
        version = resp.json()['headVersion']
        url = '{}/extras/{}@{}'.format(base_url, uuid, version)
        resp = requests.get(url)

    col_extras = resp.json()

    if version != col_extras['headVersion']:
        logger.warning("Fetching non-head version of {}."
                       "\n    Head: {},"
                       " requested {}".format(col_id,
                                              col_extras['headVersion'],
                                              version))
        if not(confirm("Fetch anyway? [y/n] ")):
            raise OldContent()

    # Write tree

    os.mkdir(str(output_dir))
    num_pages = _count_leaves(col_metadata['tree']) + 1
    label = 'Downloading to {}'.format(output_dir.relative_to(Path.cwd()))
    with click.progressbar(length=num_pages,
                           label=label,
                           show_pos=True) as pbar:
        _write_node(col_metadata['tree'], base_url, output_dir, pbar)


def _count_leaves(node, count=0):
    if 'contents' in node:
        for child in node['contents']:
            count = _count_leaves(child, count)
        return count
    else:
        return count + 1


def _write_node(node, base_url, out_dir, pbar):
    """Write out a tree node"""
    resp = requests.get('{}/contents/{}'.format(base_url, node['id']))
    if resp:  # Subcollections cannot be fetched directly
        metadata = resp.json()
        resources = {r['filename']: r for r in metadata['resources']}
        url = '{}/resources/{}'.format(base_url, resources[filename]['id'])
        file_resp = requests.get(url)
        if metadata['mediaType'] == 'application/vnd.org.cnx.collection':
            filepath = out_dir / 'collection.xml'
        else:
            modpath = out_dir / metadata['legacy_id']
            os.mkdir(str(modpath))
            filepath = modpath / 'index.cnxml'
        filepath.write_text(file_resp.text)
        pbar.update(1)

    if 'contents' in node:
        for child in node['contents']:
            _write_node(child, base_url, out_dir, pbar)
