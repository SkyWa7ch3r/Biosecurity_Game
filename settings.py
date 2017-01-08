import os
from os import environ

import dj_database_url
from boto.mturk import qualification

import otree.settings
import csv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# the environment variable OTREE_PRODUCTION controls whether Django runs in
# DEBUG mode. If OTREE_PRODUCTION==1, then DEBUG=False
if environ.get('OTREE_PRODUCTION') not in {None, '', '0'}:
    DEBUG = False
else:
    DEBUG = True

ADMIN_USERNAME = 'admin'

# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

# don't share this with anybody.
SECRET_KEY = '*qwd9e5(%#-9__^ab*1jwin-@o^h@5itm8&arta_d7ztrsb*1&'

# To use a database other than sqlite,
# set the DATABASE_URL environment variable.
# Examples:
# postgres://USER:PASSWORD@HOST:PORT/NAME
# mysql://USER:PASSWORD@HOST:PORT/NAME

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    )
}

# AUTH_LEVEL:
# If you are launching a study and want visitors to only be able to
# play your app if you provided them with a start link, set the
# environment variable OTREE_AUTH_LEVEL to STUDY.
# If you would like to put your site online in public demo mode where
# anybody can play a demo version of your game, set OTREE_AUTH_LEVEL
# to DEMO. This will allow people to play in demo mode, but not access
# the full admin interface.

AUTH_LEVEL = environ.get('OTREE_AUTH_LEVEL')

# setting for integration with AWS Mturk
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')


# e.g. EUR, CAD, GBP, CHF, CNY, JPY
#REAL_WORLD_CURRENCY_CODE = '$'
USE_POINTS = True
POINTS_DECIMAL_PLACES = 2
POINTS_CUSTOM_NAME = ""



# e.g. en, de, fr, it, ja, zh-hans
# see: https://docs.djangoproject.com/en/1.9/topics/i18n/#term-language-code
LANGUAGE_CODE = 'en'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

# SENTRY_DSN = ''

DEMO_PAGE_INTRO_TEXT = """
Welcome to the Biosecurity Game Admin Page. If you are looking to simply test out the games not play them,
follow the instructions for 'Demo' and 'Sessions' inside the Biosecurity Game: Administration Instructions.
Please read the Biosecurity Game: Administration Instructions.
"""

# from here on are qualifications requirements for workers
# see description for requirements on Amazon Mechanical Turk website:
# http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html
# and also in docs for boto:
# https://boto.readthedocs.org/en/latest/ref/mturk.html?highlight=mturk#module-boto.mturk.qualification

mturk_hit_settings = {
    'keywords': ['easy', 'bonus', 'choice', 'study'],
    'title': 'Title for your experiment',
    'description': 'Description for your experiment',
    'frame_height': 500,
    'preview_template': 'global/MTurkPreview.html',
    'minutes_allotted_per_assignment': 60,
    'expiration_hours': 7*24,  # 7 days
    # 'grant_qualification_id': 'YOUR_QUALIFICATION_ID_HERE',# to prevent retakes
    'qualification_requirements': [
        # qualification.LocaleRequirement("EqualTo", "US"),
        # qualification.PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo", 50),
        # qualification.NumberHitsApprovedRequirement("GreaterThanOrEqualTo", 5),
        # qualification.Requirement('YOUR_QUALIFICATION_ID_HERE', 'DoesNotExist')
    ]
}

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = {
    'real_world_currency_per_point': 1,
    'participation_fee': 0,
    'num_bots': 6,
    'doc': "",
    'mturk_hit_settings': mturk_hit_settings,
}

SESSION_CONFIGS = [
    {
        'name': 'Lottery_Test',
        'display_name': 'Lottery_Test',
        'num_demo_participants': 2,
        'app_sequence': ['Lottery'],
        'players_per_group': 2,
        'player_communication' : False,
        'use_browser_bots': False,
    },
	#Start of Biosecurity Test Treatments
	{
        'name': 'Biosecurity_Test_NoCalc',
        'display_name': 'Biosecurity Test NoCalc',
        'num_demo_participants': 2,
        'app_sequence': ['Biosecurity'],
        'players_per_group': 2,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
        'use_browser_bots': False,
		'calculator': False,
		'monitoring' : False,
		'pledge' : False,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 0,
		'contribution_looper' : 0,
    },
	{
        'name': 'basic_biosecurity_test',
        'display_name': 'Basic Biosecurity Test',
        'num_demo_participants': 2,
        'app_sequence': ['Biosecurity'],
        'players_per_group': 2,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : False,
		'pledge' : False,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 0,
		'contribution_looper' : 0,
    },
	{
        'name': 'freeform_biosecurity_test',
        'display_name': 'Freeform Communication Biosecurity Test',
        'num_demo_participants': 2,
        'app_sequence': ['Biosecurity'],
        'players_per_group': 2,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : True,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : False,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 0,
		'contribution_looper' : 0,
    },
	{
        'name': 'monitoring_biosecurity_test',
        'display_name': 'Monitoring Biosecurity Test',
        'num_demo_participants': 2,
        'app_sequence': ['Biosecurity'],
        'players_per_group': 2,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : False,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 0,
		'contribution_looper' : 0,
    },
	{
        'name': 'pledging_biosecurity_test',
        'display_name': 'Pledging Biosecurity Test',
        'num_demo_participants': 2,
        'app_sequence': ['Biosecurity'],
        'players_per_group': 2,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : False,
		'pledge' : True,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 5,
		'contribution_looper' : 0,
    },
	{
        'name': 'pledging_mon_biosecurity_test',
        'display_name': 'Monitoring + Pledging Biosecurity Test',
        'num_demo_participants': 2,
        'app_sequence': ['Biosecurity'],
        'players_per_group': 2,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : True,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 5,
		'contribution_looper' : 0,
    },
	{
        'name': 'aop_biosecurity_test',
        'display_name': 'Approval on Pledges Biosecurity Test',
        'num_demo_participants': 2,
        'app_sequence': ['Biosecurity'],
        'players_per_group': 2,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : True,
		'Papproval' : True,
		'Capproval' : False,
		'pledge_looper' : 5,
		'contribution_looper' : 0,
    },
	{
        'name': 'aoc_biosecurity_test',
        'display_name': 'Approval on Contributions Biosecurity Test',
        'num_demo_participants': 2,
        'app_sequence': ['Biosecurity'],
        'players_per_group': 2,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : True,
		'Papproval' : False,
		'Capproval' : True,
		'pledge_looper' : 5,
		'contribution_looper' : 5,
    },
	#Start of the Full Games
	{
        'name': 'basic_biosecurity_game',
        'display_name': 'Basic Biosecurity Game',
        'num_demo_participants': 4,
        'app_sequence': ['Lottery', 'Biosecurity', 'Results'],
        'players_per_group': 4,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : False,
		'pledge' : False,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 0,
		'contribution_looper' : 0,
    },
	{
        'name': 'freeform_biosecurity_game',
        'display_name': 'Freeform Communication Biosecurity Game',
        'num_demo_participants': 4,
        'app_sequence': ['Lottery', 'Biosecurity', 'Results'],
        'players_per_group': 4,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : True,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : False,
		'pledge' : False,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 0,
		'contribution_looper' : 0,
    },
	{
        'name': 'monitoring_biosecurity_game',
        'display_name': 'Monitoring Biosecurity Game',
        'num_demo_participants': 4,
        'app_sequence': ['Lottery', 'Biosecurity', 'Results'],
        'players_per_group': 4,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : False,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 0,
		'contribution_looper' : 0,
    },
	{
        'name': 'pledging_biosecurity_game',
        'display_name': 'Pledging Biosecurity Game',
        'num_demo_participants': 4,
        'app_sequence': ['Lottery', 'Biosecurity', 'Results'],
        'players_per_group': 4,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : False,
		'pledge' : True,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 5,
		'contribution_looper' : 0,
    },
	{
        'name': 'mon_pledging_biosecurity_game',
        'display_name': 'Monitoring + Pledging Biosecurity Game',
        'num_demo_participants': 4,
        'app_sequence': ['Lottery', 'Biosecurity', 'Results'],
        'players_per_group': 4,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : True,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 5,
		'contribution_looper' : 0,
    },
		{
        'name': 'aop_biosecurity_game',
        'display_name': 'Approval on Pledges Biosecurity Game',
        'num_demo_participants': 4,
        'app_sequence': ['Lottery', 'Biosecurity', 'Results'],
        'players_per_group': 4,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : True,
		'Papproval' : True,
		'Capproval' : False,
		'pledge_looper' : 5,
		'contribution_looper' : 0,
    },
	{
        'name': 'aoc_biosecurity_game',
        'display_name': 'Approval on Contributions Biosecurity Game',
        'num_demo_participants': 4,
        'app_sequence': ['Lottery', 'Biosecurity', 'Results'],
        'players_per_group': 4,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : True,
		'pledge' : True,
		'Papproval' : False,
		'Capproval' : True,
		'pledge_looper' : 5,
		'contribution_looper' : 5,
    },
	{
        'name': 'custom_biosecurity_game',
        'display_name': 'Custom Biosecurity Game',
        'num_demo_participants': 4,
        'app_sequence': ['Lottery', 'Biosecurity', 'Results'],
        'players_per_group': 4,
        'starting_funds' : 25.0,
        'upkeep' : 5.0,
        'revenue' : 25.0,
        'max_protection' : 15.0,
        'player_communication' : False,
        'dynamic_finances' : False,
        'set_leader' : False,
		'calculator' : True,
        'use_browser_bots': False,
		'monitoring' : False,
		'pledge' : False,
		'Papproval' : False,
		'Capproval' : False,
		'pledge_looper' : 0,
		'contribution_looper' : 0,
    },
]

# anything you put after the below line will override
# oTree's default settings. Use with caution.
otree.settings.augment_settings(globals())
BOTS_CHECK_HTML = False

ROOMS = [
	{
		'name' : 'Basic_Biosecurity_Room',
		'display_name' : 'Basic Biosecurity Room',
	}
]
