#!/usr/bin/env python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "redmap.webapp.settings")
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line([__file__, 'test', 'tests.apps.restapi.test_users.UserTests'])
