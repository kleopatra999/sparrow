Sparrow
=======

.. image:: https://requires.io/github/Wikia/sparrow/requirements.svg?branch=master
     :target: https://requires.io/github/Wikia/sparrow/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://travis-ci.org/Wikia/sparrow.svg
     :target: https://travis-ci.org/Wikia/sparrow
     :alt: Travis Build Status

Performance monitoring platform which allows running automated performance tests
on a given codebase.


Getting Started - Development
-----------------------------

Installing Tools and Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up a virtual environment. Virtualenvwrapper_ is highly recommended.

.. _Virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/

::

    mkvirtualenv sparrow

or

::

    mkproject sparrow

The development requirements are defined in the ``requirements`` folder. Note that
these are divided into separate requirements for production and local development.


Install development requirements with::

    pip install -r requirements/local.txt


Install dependencies::

    apt-get install chromium-chromedriver #(for Windows or OSX go to https://sites.google.com/a/chromium.org/chromedriver/downloads)

    apt-get install phantomjs
    npm install -g phantomas

Setting Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of keeping sensitive data like the project ``SECRET_KEY`` and
database connection strings in settings files, or worse, keeping them
in an unversioned ``local_settings`` module, we use environment
variables to store these bits of data.

If you're using virtualenvwrapper, a convenient place to define these
is in your ``postactivate`` script. Otherwise, they can go in e.g.
``~/bash_profile``.

The database connection is defined using a URL instead of separate parameters
for database name, password, etc. For PostgreSQL, the string will look like::

    postgresql://username:password@hostname:port/database

For SQLite, use::

    sqlite:////full/path/to/your/database/file.sqlite

You can use a tool like `this secret key generator`_ to generate
a ``SECRET_KEY``.

.. _this secret key generator: http://www.miniwebtool.com/django-secret-key-generator/

Here is a list of the required environment variables:

* SPARROW_DATABASE_URL

* SPARROW_SECRET_KEY

* SPARROW_RUNNER_PHANTOMAS

* SPARROW_RUNNER_CHROMEDRIVER

* SPARROW_GITHUB_TOKEN

* SPARROW_API_SERVER_URL

* SPARROW_GITHUB_TOKEN

The following environment variables are required for Celery (pre-configured for Redis):

* SPARROW_CELERY_BROKER_URL

If you are using virtualenvwrapper, begin editing the ``postactivate`` script as follows::

    cdvirtualenv
    vim bin/postactivate

Set the contents as follows::

    #!/bin/bash
    # This hook is run after this virtualenv is activated.

    export PYTHONPATH="/path/to/sparrow";
    export DJANGO_SETTINGS_MODULE="sparrow.settings.local";
    export SPARROW_DATABASE_URL="postgresql://username:password@hostname:port/database";
    export SPARROW_SECRET_KEY="";
    export SPARROW_CELERY_BROKER_URL="redis://localhost:6379/0";
    export SPARROW_RUNNER_DEPLOY_HOST="dev-synth1";
    export SPARROW_RUNNER_TARGET_HOST="dev-synth1";
    export SPARROW_RUNNER_PHANTOMAS="/path/to/phantomas";
    export SPARROW_RUNNER_CHROMEDRIVER="/path/to/chromedriver";
    export SPARROW_API_SERVER_URL="http://somehost";
    export SPARROW_GITHUBTOKEN="YOUR_GITHUB_TOKEN";

Set ``SPARROW_RUNNER_PHANTOMAS`` to a path where you have installed phantomas. If you have
it installed globally just set it to ``phantomas`` if not you can run ``npm install`` and set the path
to a folder ``{PROJECT_DIR}/node_modules/.bin/phantomas`` where ``{PROJECT_DIR}`` is the path
to a project directory where you ran ``npm install`` command.

Setting ``DJANGO_SETTINGS_MODULE`` to ``sparrow.settings.local``,
is not strictly necessary, but helpful to avoid the need for the
``--settings`` flag to django management commands.

Similarly, setting ``PYTHONPATH`` lets you use ``django-admin.py`` instead of
``python manage.py``.


Running ``manage.py`` commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django's ``manage.py`` script is located in the ``apps`` directory. Any
``manage.py`` command can be run as follows::

    python apps/manage.py --settings=sparrow.settings.local COMMAND


**NOTE:** If you've set the ``DJANGO_SETTINGS_MODULE`` environment variable, and
set your ``PYTHONPATH``, you can omit the ``--settings=...`` portion of any
``manage.py`` commands, and substitute ``django-admin.py`` for ``manage.py``.


Standalone UI development
-------------------------

Install node.js static http server:

    sudo npm install http-server -g

Start the standalone static http server:

    cd apps/frontend/static
    http-server

Then open http://localhost:8080 in your web browser and enter the server address and press Enter.

