from os import environ


SESSION_CONFIGS = [
    dict(
        name='bargaining',
        display_name="Bargaining",
        app_sequence=['bargaining'],
        num_demo_participants=2,
    ),
    dict(
        name='bertrand',
        display_name="Bertrand",
        app_sequence=['bertrand'],
        num_demo_participants=2,
    ),
    dict(
        name='common_auction',
        display_name="Common Value Auction",
        app_sequence=['common_value_auction'],
        num_demo_participants=2,
    ),
    dict(
        name='cournot',
        display_name="Cournot",
        app_sequence=['cournot'],
        num_demo_participants=2,
    ),
    dict(
        name='dictator',
        display_name="Dictator",
        app_sequence=['dictator'],
        num_demo_participants=2,
    ),
    dict(
        name='survey',
        display_name='Example Survey', 
        app_sequence=['survey'], 
        num_demo_participants=1
    ),
    dict(
        name='guess_two_thirds',
        display_name="Guess 2/3 of the Average",
        app_sequence=['guess_two_thirds'],
        num_demo_participants=3,
    ),
    dict(
        name='pennies',
        display_name="Matching Pennies",
        app_sequence=['matching_pennies'],
        num_demo_participants=2,
    ),
    dict(
        name='prisoner',
        display_name="Prisoner's Dilemma",
        app_sequence=['prisoner'],
        num_demo_participants=2,
    ),
    dict(
        name='public_good',
        display_name="Public Goods",
        app_sequence=['public_goods_simple'],
        num_demo_participants=3,
    ),
    dict(
        name='traveler',
        display_name="Traveler's Dilemma",
        app_sequence=['traveler_dilemma'],
        num_demo_participants=2,
    ),
    dict(
        name='trust',
        display_name="Trust",
        app_sequence=['trust'],
        num_demo_participants=2,
    ),
    dict(
        name='volunteer',
        display_name="Volunteer's Dilemma",
        app_sequence=['volunteer_dilemma'],
        num_demo_participants=3,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '5679940727964'

INSTALLED_APPS = ['otree']
