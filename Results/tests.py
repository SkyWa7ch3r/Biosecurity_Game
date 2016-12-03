from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):
        #Go through the Questioner Page
        yield(views.Questioner, {'questioner_1': 'Strongly disagree', 'questioner_2': 'Somewhat disagree', 'questioner_3': 'Neither agree nor disagree', 'questioner_4': 'Somewhat agree',
                                 'questioner_5': 'Strongly agree', 'questioner_6': 'Strongly disagree', 'questioner_7': 'Strongly disagree', 'questioner_8': 'Strongly disagree',
                                 'questioner_9': 'Very Likely', 'questioner_10': 'Very Likely', 'questioner_11': 'Neutral', 'questioner_12': 'Other',
                                 'questioner_13': '21', 'questioner_14': 'Perth 6000', 'questioner_15': '0 – $18,200'})
        #Display The end Reuslts page
        yield(views.ResultsSummary)
