from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

	def play_round(self):
		#Go through the Questioner Page
		'''
		yield(views.Questioner, {'questioner_1': 'Strongly Disagree', 
								 'questioner_2': 'Strongly Disagree', 
								 'questioner_3': "Strongly Disagree",
								 'questioner_4': 'Strongly Disagree',
								 'questioner_5': 'Strongly Disagree', 
								 'questioner_6': 'Strongly Disagree', 
								 'questioner_7': 'Strongly Disagree', 
								 'questioner_8': 'Strongly Disagree', 
								 'questioner_9': 'Very Unlikely', 
								 'questioner_10': 'Very Unlikely', 
								 'questioner_11': 'Very Unlikely',
								 'questioner_12': 'Male', 
								 'questioner_13': '21', 
								 'questioner_14': 'UWA 6000',
								 'questioner_15' : '0 – $18,200'
								 })
		'''
		yield(views.Questioner, {'questioner_1': "I thought that other players would not protect, so I didn't see why I should either.", 
								 'questioner_2': '1 - Not at all Concerned', 
								 'questioner_3': '1 - Not at all Concerned',
								 'questioner_4': '1 - A little amount of Trust',
								 'questioner_5': '1 - Strongly Disagree', 
								 'questioner_6': '1 - Strongly Disagree', 
								 'questioner_7': '1 - Strongly Disagree', 
								 'questioner_8': '1 - Strongly Disagree',
								 'questioner_9': '1 - Strongly Disagree', 
								 'questioner_10': '1 - Strongly Disagree', 
								 'questioner_11': '1 - Strongly Disagree', 
								 'questioner_12': '1 - Strongly Disagree',
								 'questioner_13': '1 - Strongly Disagree', 
								 'questioner_14': 'Male', 
								 'questioner_15': '21',
								 'questioner_16': 'UWA 6009',
								 'questioner_17': "$18,201 - $37,000",
								 'questioner_18': '1 - Strongly Disagree', 
								 'questioner_19': '1 - Strongly Disagree', 
								 'questioner_20': '1 - Strongly Disagree'
								 })
		
		#Display The end Reuslts page
		yield(views.ResultsSummary)
