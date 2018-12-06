REDMAP
======

Redmap Australia Django project.

Requirements
------------

* Python 2.7.x (`python2.7`)
* Python headers (`python2.7-dev`)
* [Fabric](fabfile.org)
* PIL deps (libjpeg / libfreetype2 / libpng / etc)
* unixODBC headers (`unixodbc-dev`)
* Sqlite spacial queries deps (GDAL / numpy)
* Xapian and the language bindings (libxapian / xapian-python)
* GeoDjango (`binutils libproj-dev gdal-bin`)

You can install all the requirements for running Redmap under Ubuntu by
installing the following packaged:

	$ sudo apt-get install python2.7-dev libjpeg-dev libfreetype6-dev \
		libpng12-dev unixodbc-dev gdal-bin libgdal1-dev python-numpy \
		libxapian xapian-python

Include ./src and ./src/redmap/apps in your PYTHONPATH.
`add2virtualenv` is a handy way to do this if you use `virtualenvwrapper`.
Otherwise, append the following lines to your `venv/bin/activate`:

	BASE=$( dirname "$VIRTUAL_ENV" )
	_OLD_VIRTUAL_PYTHONPATH="$PYTHONPATH"
	PYTHONPATH="$BASE/src:$BASE/src/redmap/apps"
	export PYTHONPATH

and the following lines inside the `deactivate()` function in the same file:

	PYTHONPATH="$_OLD_VIRTUAL_PYTHONPATH"
	export PYTHONPATH
	unset _OLD_VIRTUAL_PYTHONPATH

The xapian python bindings are not currently pip-installable so you will need to manaually add
them to your virtual environment by symlinking them in.  On my machine (Debian/amd64) the process
is as follows:

	cd $PROJECT_ROOT/venv/lib/python2.6/site-packages
	ln -s /usr/lib/python2.6/dist-packages/xapian .

Installation
------------

1. Clone the git repository:

    $ git clone git@bitbucket.org:ionata/redmap.git

2. Configure the deployment settings scripts located in the `{{PROJECT_ROOT}}/conf/` directory.

3. Use Fabric to deploy to either a `beta`, `staging`, or `production` environment:

    $ fab -R {{environment}} install


Upgrading
----------

1. Currently changes ready for deployment are on the stage branch, so clone a copy:

    $ git clone git@bitbucket.org:ionata/redmap.git -b stage


2. Use fabric to deploy, either a `full` or `sync` release to one of the available targets:

    $ fab -R {{target}} upgrade:{{releasetype}}

    So for instance to perform a quick hotfix to the beta server you would issue the following command:

    $ fab -R beta upgrade:sync

    A `full` upgrade is the default, so you can omit the release type option if that is desired.


3. If something goes awry with the gunicorn procs the following commands are available to help:

    * $ fab -R {{target}} gunicorn_server_status
    * $ fab -R {{target}} gunicorn_stop_server
    * $ fab -R {{target}} gunicorn_start_server


Migration
---------

When setting up a development version of Redmap, there are a few steps necessary to get the data you need to work with. This should only ever need to be performed once, on an un-migrated dataset.


### Requirements

* A fresh instance of the live MSSQL database
* A fresh instance of the live MySQL database
* A fresh instance of the `/media/` directory

### Instructions

1. Hook project up to MSSQL database
    1. Run export: `./manage.py dumpdata > data.json`
2. Export MySQL tables as CSVs
    1. `redmap_users`
    2. `pictures`
    3. `species`
    4. `species_categories`
3. Move `/media/` dir to development environment media directory
4. Run four migration scripts to merge CSV data to MSSQL database and update records as necessary
    1. users
    2. pictures
    3. species
    4. speciescategories
5. Load initial data into database
    1. Groups
    2. Tags
    3. ...
6. Run script to set up initial group assignments (TODO)

_Disclaimer: These instructions are based off what I can remember right now and need refining._
