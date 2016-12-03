#!/usr/bin/env python 
import os
from os import environ
import sys
from django.contrib.auth.models import User

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
	from otree.management.cli import execute_from_command_line
	execute_from_command_line(sys.argv, script_file=__file__)
	u = User.objects.create_user('Ben', 'benedict.white@uwa.edu.au', os.environ.get('OTREE_BEN'))
	u.is_superuser = True
	u.is_staff = True
	u.save()
	u = User.objects.create_user('Mark', 'mark.hurlstone@uwa.edu.au', os.environ.get('OTREE_MARK'))
	u.is_superuser = True
	u.is_staff = True 
	u.save() 