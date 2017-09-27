from otree.api import (
	models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
	Currency as c, currency_range, safe_json
)
from django.core.exceptions import ValidationError

import random
import csv

author = 'Trae Shaw'

doc = """
This is the Results application which has the end questionnaire and shows the results for the Lottery and Biosecurity Game to the participants.
"""
"""
This is the Results models.py, in here are the methods for displaying the final results after the completion of the experiment as well as a survey beforehand. This file also provides
the random lottery ball selection. 
"""

#Added Comment here to ensure git enforces change to UTF-8 encoding

class Constants(BaseConstants):
	"""
		The Constants class sets up the constants for each session. It names the game for identification and url purposes as well as specifying how many players there,
		the information from the csv files for the game which are stored in lists and from this how many lottery rounds there will be and how long they will be.
	"""
	name_in_url = 'results'
	players_per_group = None

	with open('CSV/questioner_data.csv') as f:
		questioner_list = list(csv.DictReader(f))

	num_rounds = 1
	
	num_questions = len(questioner_list)
	

class Subsession(BaseSubsession):
	pass

class Group(BaseGroup):
	pass

class Player(BasePlayer):
	def returnFormField(qn):
		"""
		The Player class initialises the survey/questionaire and allows for the form entries to be returned.
		"""
		if Constants.questioner_list[qn]['type'] == 'text':
			return models.CharField(verbose_name=Constants.questioner_list[qn]['question'], widget=widgets.TextInput())
		elif Constants.questioner_list[qn]['type'] == 'integer':
			return models.IntegerField(verbose_name=Constants.questioner_list[qn]['question'])
		elif Constants.questioner_list[qn]['type'] == 'age':
			return models.PositiveIntegerField(verbose_name=Constants.questioner_list[qn]['question'],
											   choices=range(10, 150), initial=None)
		else:
			matrix = []
			for num in range(1, int(Constants.questioner_list[qn]['#choices']) + 1):
				matrix.append(Constants.questioner_list[qn]['choice{}'.format(num)])
			return models.CharField(choices=matrix, verbose_name=Constants.questioner_list[qn]['question'],
									widget=widgets.RadioSelect())

	questioner_1 = returnFormField(0)
	questioner_2 = returnFormField(1)
	questioner_3 = returnFormField(2)
	questioner_4 = returnFormField(3)
	questioner_5 = returnFormField(4)
	questioner_6 = returnFormField(5)
	questioner_7 = returnFormField(6)
	questioner_8 = returnFormField(7)
	questioner_9 = returnFormField(8)
	questioner_10 = returnFormField(9)
	questioner_11 = returnFormField(10)
	questioner_12 = returnFormField(11)
	questioner_13 = returnFormField(12)
	questioner_14 = returnFormField(13)
	questioner_15 = returnFormField(14)
	questioner_16 = returnFormField(15)
	questioner_17 = returnFormField(16)
	
