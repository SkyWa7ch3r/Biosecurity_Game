from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range, safe_json
)
from django.core.exceptions import ValidationError

import random
import csv

author = 'Trae Shaw'

doc = """
This is the Results models.py, in here are the methods for displaying the final results after the completion of the experiment as well as a survey beforehand. This file also provides
the random lottery ball selection. 
"""


class Constants(BaseConstants):
    """
        The Constants class sets up the constants for each session. It names the game for identification and url purposes as well as specifying how many players there,
        the information from the csv files for the game which are stored in lists and from this how many lottery rounds there will be and how long they will be.
    """
    name_in_url = 'results'
    players_per_group = None

    # open the csv files
    with open('CSV/lottery_data.csv') as f:
        values = list(csv.DictReader(f))
    with open('CSV/lottery_questions.csv') as f:
        lottery_questions = list(csv.DictReader(f))
    with open('CSV/questioner_data.csv') as f:
        questioner_list = list(csv.DictReader(f))

    # lottery_rounds defines how many lottery rounds there are
    lottery_rounds = 1

    # round_lengths defines how many games there are in each lottery round
    round_lengths = [0]

    # read the csv file to find lottery_rounds and round_lengths
    size = 0
    for i in range(0, len(values)):
        if lottery_rounds != int(values[i]['lottery_round']):
            round_lengths.append(size)
            lottery_rounds += 1
        size += 1
    round_lengths.append(size)

    num_rounds = 1

    num_lotery_questions = 5

    # questioner_rounds = int(len(questioner_list) / 10)
    # last_questioner_number = len(questioner_list) % 10


class Subsession(BaseSubsession):
    def before_session_starts(self):
        """
        The Subsession class decides the random round, ball and paying line of the lottery game to calculate the pay each player receives
        based on their choices in the lottery game.
        """
        if self.round_number == 1:
            # Select a random round
            paying_round = random.randint(1, Constants.num_rounds)
            self.session.vars['paying_round'] = paying_round

            # Select a random ball
            ball_number = random.randint(1, 10)
            self.session.vars['ball_number'] = ball_number

            # Select a random game
            paying_line = random.randint(1, Constants.round_lengths[paying_round] - Constants.round_lengths[
                paying_round - 1])
            self.session.vars['paying_line'] = paying_line


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

    
