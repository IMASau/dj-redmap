
snapshot:
	rm ../../var/dev.sqlite3
	./manage.py syncdb --noinput
	./manage.py sqlflush | ./manage.py dbshell
	./manage.py loaddata snapshot

all:
	rm ../../var/dev.sqlite3 
	./manage.py syncdb --noinput
	./manage.py load_redmapdb_data
	./manage.py load_test_users
	./manage.py load_cms_data
	./manage.py rebuild_index --noinput

