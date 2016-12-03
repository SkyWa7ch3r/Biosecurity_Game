from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range, safe_json
)
from django.core.exceptions import ValidationError

import random
import csv

author = 'Martin Porebski & Campbell Beck'

doc = """
The Lottery Game.

It begins with the lottery instructions page which contains information regarding how the game is played and how payoffs are made. 
Those instructions are hardcoded in the html template file under template/Lottery/LotteryInstructions.html

The next page is a short quiz which tests participants understanding of the game and will not allow a player to progress, unless all of the questions are answered correctly. This is done to ensure that the instructions have been understood.
Five questions are inputed through a lottery_questions CSV file.

Following from that are the rounds of the lottery game itself. Each round consists of up to 15 games in which the player has to select between two options. 
Any number of rounds and up to 15 games can be imported from the lottery_data CSV file.

Models.py controls the logic of the game. 
The Constants class sets up the constants for each session. It names the game for identification and url purposes as well as specifying how many players there, the information from the csv files for the game which are stored in lists and from this
how many lottery rounds there will be and how long they will be.
name_in_url = url identification
values - stores the lottery_questions.csv file into a list
lottery_questions - stores the lottery_questions.csv file into a list
lottery_instructions_template - will append the LotteryInstructionsShort.html template to each lottery page, to display a summary of lottery instructions
round_lengths - stores how many games there are for each lottery round (read from the lottery_data.csv file)
num_rounds - stores how many of the lottery rounds there are (read from the lottery_data.csv file)
num_lotery_questions - automatically determines the number of questions in the lottery_questions.csv

The Subsession class sets up the variables that differ across each session that is created. These include the size of each group, the round that will be paid out on, the game for that round which will be paid out on and the number of the ball selected (these are caluclated randomly)
paying_round - paying round from which winning game and ball will be selected
paying_line - paying game
ball_number - winning ball

The Group class is empty for the lottery game as the outcomes for the lottery game are independent of other players inputs.

def check_correct is method used for validating that the user selected the correct answer for the pre lottery quiz


The Player class holds the logic for how the various question pages operate along with setting up the individual player variables for each round:

returnLotteryFormField is a mehotd that reads the lottery questions from the lottery_questions that stores CSV values and forms models for the form fields (lottery_question_) that will be displayed in the html template.

lottery_question_1 - lottery_question_5 store the answers to the pre lottery quiz

submitted_answer_0 - submitted_answer_14 store the choice for each lottery game for the player

There is a maximum of 15 games, however it can be any number from 1 to 15 as well as any number of rounds (as specified in the csv file)
Each field is a radio select using A or B as the possible choices
Values specified in the values csv file that determine the winnings from each ball in each game
Subssession.round_number doesn't work, not sure why, if a fix is found the code will be finished

The submits() method puts the submitted_answers values into a list so that the submissions can be indexed when calculating payoff.

player_submits holds selected values in the playing round in a list that can be itterated over

set_payoff() determines the payoff for each player from the lottery by determining the range for the best and worst outcomes for choices A and B for each round using the list created from the csv file titled lottery_data, if the current round is the pre-determined paying round, a comparison is made between the players
selection for the paying line and calculates the payoff from the same list by comparing which range the selected ball number is in for the players choice.
If set_payoff is called in the non paying round, their is no increase in payoff.

Editing the lottery questions: To edit these questions and their respective answers open the file names 'lottery_questions.csv' and change any of the questions as seen fit. if you
want to have a question with more than 5 possible answers, edit the first line of the document by adding choice6 to choiceN after choice5 with N
being the total number of answers you want (don't forget to add commas to the end of the possible choices of the other questions).

Adding quesitons to lottery questions: If you wish to add an additional question to the list, add the question following
the format of the other questions making sure to add commas followed by a blank if the number of possible choices is less
than the max number of possible choices eg; 6, This is a test question.,3,1,3,1,4,,, (the first number is the number of choices
the next number is the index of the correct choice and numbers proceeding it are the values of the choices.
Next search models.py for the section that contains lottery_question_1 - lottery_question_5 and follow the format for every added question
e.g; if adding a 6th question, below lottery_question_5 = returnLotteryFormField(4), add lottery_question_6 = returnLotteryFormField(5)

Editing the lottery values: To edit the range of balls for each round, go to the first row for each round (the first number 1, 2 or 3) and edit each ranges in the columns titled as "a_best_range", "a_worst_range" and similary for B (ranges should not exceed 10).

Similary the pay off for each game in the round can be edited by editing the desired game number's row in the column titled either "a_best", "a_worst" and similarly for B columns
Choosing when payoff occurs: If it is desired that payoff is made of a predetermined round, game, ball number or a combination of all 3 editing of the subsession class must be done. To do so remove the # on any of the lines #paying_round = n, #paying_line = n, #ball_number = n and change the n to the desired value (the range for each is specified above each line)

views.py takes all of the processed variables from the models.py and passes them to the templates to be displayed through the html files. Each class specifies each page (html)
is_displayed methods specify when should the page be displayed in each round
get_form_fields methods pass the form specifications to be displayed

"""


class Constants(BaseConstants):
    name_in_url = 'lottery'
    players_per_group = None
    lottery_instructions_template = 'lottery/LotteryInstructionsShort.html'

    # open the csv files
    with open('CSV/lottery_data.csv') as f:
        values = list(csv.DictReader(f))
    with open('CSV/lottery_questions.csv') as f:
        lottery_questions = list(csv.DictReader(f))

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

    # how many lottery rounds there are
    num_rounds = lottery_rounds
    
    # automatically determines the number of questions in the lottery_questions.csv
    num_lotery_questions = len(lottery_questions)

    # questioner_rounds = int(len(questioner_list) / 10)
    # last_questioner_number = len(questioner_list) % 10


class Subsession(BaseSubsession):
    def before_session_starts(self):
        if self.round_number == 1:
            # Select a random round
            paying_round = random.randint(1, Constants.num_rounds)
            #n must be in the range of 1 to 3
            #paying_round = n
            self.session.vars['paying_round'] = paying_round

            # Select a random ball
            ball_number = random.randint(1, 10)
            #n must be in the range of 1 to 10
            #ball_number = n
            self.session.vars['ball_number'] = ball_number

            # GROUP LOGIC STARTS HERE
            # ppg = player_per_group
            ppg = self.session.config['players_per_group']
            # list_of_groups is the the list of each group list e.g. [ [p1, p2], [p3, p4] ] if ppg == 2 and np == 4
            list_of_groups = []
            # The list of players is list of all the player ID's in the session
            list_of_players = []
            for p in self.get_players():
                list_of_players.append(p.id_in_group)
            # np = number of players
            np = len(self.get_players())
            i = 0
            while i < np:
                # get a list of the players going from the ith index to i + ppg - 1 and add that to the list of the groups
                list_of_groups.append(list_of_players[i: i + ppg])
                # iterate the i
                i = i + ppg
            num_groups = len(list_of_groups)
            # If the number of players is not a multiple of player per group
            if np % ppg != 0:
                # iterate through the list of groups
                for i in range(num_groups):
                    # if the last group is full, do not continue
                    if len(list_of_groups[-1]) == ppg:
                        break
                    # Get the player to remove
                    player = list_of_groups[i][-1]
                    # remove the player
                    del list_of_groups[i][-1]
                    # add the player to the last group
                    list_of_groups[-1].append(player)
            # finalise the group matchings ready for game and store the matrix
            self.set_group_matrix(list_of_groups)
            self.session.vars['matrix'] = list_of_groups

            # Select a random game
            paying_line = random.randint(1, Constants.round_lengths[paying_round] - Constants.round_lengths[
                paying_round - 1])
            #n must be within the range of 1 to 14 for rounds 1 or 2 and in the range of 1 to 5 for round 3
            #paying_line = n
            self.session.vars['paying_line'] = paying_line

class Group(BaseGroup):
    pass

#check_correct is used for validating that the user selected the correct answer for the pre lottery quiz
def check_correct(correct_value):
    def compare(slected_value):
        if not (correct_value == slected_value):
            raise ValidationError('Incorrect')

    return compare


class Player(BasePlayer):
    # read the pre-lottery question of the csv file
    def returnLotteryFormField(qn):
        matrix = []
        for num in range(1, int(Constants.lottery_questions[qn]['#choices']) + 1):
            matrix.append(Constants.lottery_questions[qn]['choice{}'.format(num)])
        return models.CharField(choices=matrix, verbose_name=Constants.lottery_questions[qn]['question'],
                                widget=widgets.RadioSelect(),
                                validators=[check_correct(Constants.lottery_questions[qn]['choice{}'.format(
                                    int(Constants.lottery_questions[qn]['#correct']))])])
    # Add lottery questions here 
    lottery_question_1 = returnLotteryFormField(0)
    lottery_question_2 = returnLotteryFormField(1)
    lottery_question_3 = returnLotteryFormField(2)
    lottery_question_4 = returnLotteryFormField(3)
    lottery_question_5 = returnLotteryFormField(4)

    # stores players responses to the lottery games
    submitted_answer_1 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_2 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_3 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_4 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_5 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_6 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_7 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_8 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_9 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_10 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_11 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_12 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_13 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())
    submitted_answer_14 = models.CharField(choices=['A', 'B'], widget=widgets.RadioSelectHorizontal())

    # player_submits holds selected values in the playing round in a list that can be itterated over
    def set_submits(self):
        if self.subsession.round_number == self.session.vars['paying_round']:
            self.player_submits = []
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_1)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_2)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_3)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_4)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_5)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_6)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_7)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_8)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_9)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_10)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_11)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_12)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_13)
            self.player_submits.append(self.in_round(self.round_number).submitted_answer_14)

    def set_payoff(self):
        lround = self.session.vars['paying_round']
        line = self.session.vars['paying_line'] - 1
        ball = self.session.vars['ball_number']
        
        # read the range of balls for each round
        a_best_ball_range = Constants.values[Constants.round_lengths[1]]['a_best_ball_range']
        a_best_ball_range = a_best_ball_range.split('-')
        a_worst_ball_range = Constants.values[Constants.round_lengths[1]]['a_worst_ball_range']
        a_worst_ball_range = a_worst_ball_range.split('-')
        b_best_ball_range = Constants.values[Constants.round_lengths[1]]['b_best_ball_range']
        b_best_ball_range = b_best_ball_range.split('-')
        b_worst_ball_range = Constants.values[Constants.round_lengths[1]]['b_worst_ball_range']
        b_worst_ball_range = b_worst_ball_range.split('-')

        # read the value selected by the player
        if self.round_number == lround:
            if self.player_submits[line] == 'A':
                if ball >= int(a_best_ball_range[0]) and ball < int(a_worst_ball_range[0]):
                    self.payoff = c(Constants.values[Constants.round_lengths[lround - 1] + line]['a_best'])
                else:
                    self.payoff = c(Constants.values[Constants.round_lengths[lround - 1] + line]['a_worst'])
            else:
                if ball >= int(b_best_ball_range[0]) and ball < int(b_worst_ball_range[0]):
                    self.payoff = c(Constants.values[Constants.round_lengths[lround - 1] + line]['b_best'])
                else:
                    self.payoff = c(Constants.values[Constants.round_lengths[lround - 1] + line]['b_worst'])
        else:
            self.payoff = c(0)
