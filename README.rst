CNX Nebu Publishing Utility
===========================

This is a command-line interface for interacting with connexions content. The tools is primarily used to publish content to the cnx.org website.

This software requires:

- Python >= 3.6 <= 3.8
- libmagic(libmagic1 on Linux)
- JRE >= 6


Install
=======

1. Install ``python3`` (on OSX you can run ``brew install python3``)
#. Run ``pip3 install --upgrade pip setuptools`` in a terminal to upgrade python tools
#. Make sure libmagic is installed (default on Linux, on OSX use ``brew install libmagic``)
#. Run ``pip3 install nebuchadnezzar`` in a terminal
#. Run ``neb --help`` to verify the application is installed


Development
===========

Install
-------

1. Install ``python3`` (on OSX you can run ``brew install python3``)
#. Make sure libmagic is installed (default on Linux, on OSX use ``brew install libmagic``)
#. Install ``virtualenv`` (on OSX you can run ``pip3 install virtualenv``)
#. Initialize the python virtual environment:

   a. ``virtualenv ./venv/ --python=python3.5``
   #. ``source ./venv/bin/activate``
   #. ``pip3 install --upgrade pip setuptools``
   #. ``python setup.py develop`` or  (preferably) ``pip3 install -e .``

Developer Run
-------------

1. Open up a new terminal
#. ``source ./venv/bin/activate``
#. Now you can run various commands:

   - ``neb --help`` for help with the various commands

Testing
-------------
To run all tests: ``make test``

To run a single test called ``test_main``: ``make test -- -k test_main``

Usage
-----
There are a few ways to ensure ``neb`` attempts to connect with the desired server:

#. Use a configuration file
#. Don't use a configuration file, and pass an environment name
#. (For ``neb get``) Don't use a configuration file, and pass a specific archive host as an argument

Using a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^

The CLI will expect a configuration file as either ``~/.config/nebuchadnezzar.ini`` or as defined by the ``NEB_CONFIG`` environment variable. You can use this file to configure environment-specific URL values for:

- ``url``: The environment specific URL
- ``archive_url``: The archive endpoint URL (this is optional, and if not provided the tool will construct the URL based upon convention)

An example of using both of these values to define a ``test`` environment::

    [settings]

    [environ-test]
    url = https://test.cnx.org
    archive_url = https://archive.test.cnx.org

Passing target host as environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For the ``get``, ``publish``, and ``ping`` commands, you can specify an environment value in the following forms and avoid a configuration file:

#. An ``environment`` where the target host is ``environment.cnx.org``

    Example: ``neb publish qa ...`` will access ``https://qa.cnx.org``

#. An ``environment`` that is a FQDN but doesn't specifiy protocol

    Example: ``neb publish qa.cnx.org ...`` will access ``https://qa.cnx.org``

#. An ``environment`` that is a FQDN with protocol

    Example: ``neb publish http://host.foobar.org ...`` will access ``http://host.foobar.org``

Specifying archive host
^^^^^^^^^^^^^^^^^^^^^^^
For the ``get`` command, if you need to access an archive host that doesn't follow the ``archive-{environment}`` convention and also want to avoid using a configuration file, you can use the ``--archive`` argument:

* Example: ``neb get vagrant --archive archive.local.cnx.org ...``

Configuring an Editor
=====================
Preparation
-----------

#. Install https://atom.io
#. Install Java

    #. For macOS you can install Java by installing https://brew.sh and then running ``brew install java`` in a terminal.

Install (with automatic Atom config)
------------------------------------

#. Start up Atom
#. Install the ``linter-autocomplete-jing`` package

#. Type <kbd>⌘</kbd>+<kbd>,</kbd> (for Mac) to open Settings (or click **Atom**, **Preferences...** in the menu bar)

   #. Click **Install** in the left-hand-side
   #. Enter ``linter-autocomplete-jing`` and click **Install**
   #. **Alternative:** run ``apm install linter-autocomplete-jing`` from the commandline

#. Run ``neb atom-config`` (**NOTE:** *This will overwrite your Atom config file. If you'd prefer updating the config file yourself, see 'Manual Atom config' below.*)
#. Restart Atom
#. Open an unzipped complete-zip. (I run ``atom ~/Downloads/col1234_complete`` **From a terminal**)
#. Verify by opening an ``index.cnxml`` file and typing in ``<figure>`` somewhere in the file. You should see a red flag near the tag that says ``RNG: element "figure" missing required attribute "id"``.

Manual Atom config
------------------

This step is only necessary if you didn't run ``neb atom-config`` above. After completing this step, resume the instructions above from the 'Restart Atom' step.

Add the following to your Atom configuration by clicking **Atom**, **Config** in the menu bar and copying and pasting the below (**NOTE**: indentation is important)::

    "*":
      core:
        customFileTypes:

          # Add this to the bottom of the customFileTypes area.
          # Note: Indentation is important!
          "text.xml": [
            "index.cnxml"
          ]


      # And then this to the bottom of the file
      # 1. Make sure "linter-autocomplete-jing" only occurs once in this file!
      # 1. make sure it is indented by 2 spaces just like it is in this example.

      "linter-autocomplete-jing":
        displaySchemaWarnings: true
        rules: [
          {
            priority: 1
            test:
              pathRegex: ".cnxml$"
            outcome:
              schemaProps: [
                {
                  lang: "rng"
                  path: "~/.neb/cnxml-validation/cnxml/xml/cnxml/schema/rng/0.7/cnxml-jing.rng"
                }
              ]
          }
        ]

License
-------

This software is subject to the provisions of the GNU Affero General
Public License Version 3.0 (AGPL). See `<LICENSE.txt>`_ for details.
Copyright (c) 2016-2018 Rice University
