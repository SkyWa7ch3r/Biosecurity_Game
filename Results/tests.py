from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):
        #Go through the Questioner Page
        yield(views.Questioner, {'questioner_1': 'Male', 
								 'questioner_2': '21', 
								 'questioner_3': "I thought that other players would not protect, so I didn't see why I should either.",
								 'questioner_4': 'Yes',
                                 'questioner_5': '1 - Not at all Concerned', 
								 'questioner_6': '1 - Not at all Concerned', 
								 'questioner_7': '1 - A little amount of Trust', 
								 'questioner_8': '1 - Strongly Disagree',
                                 'questioner_9': '1 - Strongly Disagree', 
								 'questioner_10': '1 - Strongly Disagree', 
								 'questioner_11': '1 - Strongly Disagree', 
								 'questioner_12': '1 - Strongly Disagree',
                                 'questioner_13': '1 - Strongly Disagree', 
								 'questioner_14': '1 - Strongly Disagree', 
								 'questioner_15': '1 - Strongly Disagree',
								 'questioner_16': '1 - Strongly Disagree',
								 'questioner_17': '1 - Strongly Disagree',
								 'questioner_18': '1 - Strongly Disagree', 
								 'questioner_19': '1 - Strongly Disagree', 
								 'questioner_20': '1 - Strongly Disagree'})
        #Display The end Reuslts page
        yield(views.ResultsSummary)
