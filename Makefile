
DESTDIR = /Users/oliver/repos/redmap-org-au
SRCDIR  = /Users/oliver/repos/redmap-org-au/src
APPSDIR = /Users/oliver/repos/redmap-org-au/src/apps

STRIPCOMMENTS = sed '/^[ \t]*\#/d'

EXCLUDES = --exclude=data.py --exclude=tests --exclude management --exclude '*.pyc' --exclude fixtures --exclude=tests.py --exclude=locale

all: docdrop reqsdrop codedrop clearnotes autopep8

docdrop:
	rsync -r --delete manual/ $(DESTDIR)/docs/ --exclude=Makefile

reqsdrop:
	$(STRIPCOMMENTS) requirements.txt > $(DESTDIR)/requirements.txt

codedrop:
	rsync -r --delete src/redmap/apps/redmapdb/ $(APPSDIR)/redmapdb/ $(EXCLUDES)
	rsync -r --delete src/redmap/apps/backend/ $(APPSDIR)/backend/ $(EXCLUDES)
	rsync -r --delete src/redmap/apps/frontend/ $(APPSDIR)/frontend/ $(EXCLUDES)
	rsync -r --delete src/redmap/apps/accounts/ $(APPSDIR)/accounts/ $(EXCLUDES)
	rsync -r --delete src/redmap/apps/formjs/ $(APPSDIR)/formjs/ $(EXCLUDES)
	rsync -r --delete src/redmap/apps/news/ $(APPSDIR)/news/ $(EXCLUDES)

	rsync -r --delete src/redmap/common/ $(SRCDIR)/common/ $(EXCLUDES)

	rsync -r --delete src/redmap/webapp/ $(SRCDIR)/webapp/ $(EXCLUDES) --exclude=templates --exclude=static --exclude=settings
	cp src/redmap/webapp/settings/base.py $(SRCDIR)/webapp/settings.py
	rsync -r --delete src/redmap/webapp/templates/ $(SRCDIR)/templates/ $(EXCLUDES)
	rsync -r --delete src/redmap/webapp/static/ $(SRCDIR)/static/ $(EXCLUDES)

clearnotes:
	for f in `find $(APPSDIR) $(SRCDIR)/common/ -name '*py'`; do echo $$f; $(STRIPCOMMENTS) $$f > /tmp/f; cp /tmp/f $$f; done

autopep8:
	autopep8 -r --in-place $(APPSDIR)
	autopep8 -r --in-place $(SRCDIR)/common
	autopep8 -r --in-place $(SRCDIR)/webapp

