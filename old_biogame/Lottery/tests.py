from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from otree.api import SubmissionMustFail
from .models import Constants
import random
import csv

class PlayerBot(Bot):
	cases = ['random' , 'halfAhalfB' , 'AllB', 'AllA']
	def play_round(self):
		#Choices for the random lottery
		choices = ['A','B']
		#Initialize the value lists
		correct_values = []
		wrong_values = []
		#Populate the correct_values list with the correct answers to the questions
		with open('CSV/lottery_questions.csv') as f:
			values = csv.DictReader(f)
			#For every row in the csv file
			for row in values:
				#Just in case it tries to register an empty row, which it was in my testing
				if row['id'] != '':
					#Get the correct choice integer
					correct_choice = row['#correct']
					#Get the choice string
					cstring = 'choice%s' % correct_choice
					#Initialize wrong string
					wstring = ''
					#If the correct choice isnt 1
					if correct_choice != '1':
						#Load the first choice into the wrong value string
						wstring = 'choice1'
					#if the correct choice is number 1 then
					else:
						#Load the second choice into the wrong value string
						wstring = 'choice2'
					#Add the correct and wrong values
					correct_values.append(row[cstring])
					wrong_values.append(row[wstring])

		if self.subsession.round_number == 1:
			#Load the instruction and Introduction pages
			yield(views.Introduction, {'participant_label' : 'Bot%d' % self.player.id_in_group} )
			yield(views.LotteryInstructions)
			#Test for Lottery Questions Failure, it checks for failures in order of question numbers 1,2,3,... In order for the test to continue these asserts MUST FAIL
			yield SubmissionMustFail(views.LotteryQuestions, {'lottery_question_1': wrong_values[0], 'lottery_question_2': correct_values[1], 'lottery_question_3': correct_values[2],
										   'lottery_question_4': correct_values[3]} )
			yield SubmissionMustFail(views.LotteryQuestions, {'lottery_question_1': correct_values[0], 'lottery_question_2': wrong_values[1], 'lottery_question_3': correct_values[2],
										   'lottery_question_4': correct_values[3]} )
			yield SubmissionMustFail(views.LotteryQuestions, {'lottery_question_1': correct_values[0], 'lottery_question_2': correct_values[1], 'lottery_question_3': wrong_values[2],
										   'lottery_question_4': correct_values[3]} )
			yield SubmissionMustFail(views.LotteryQuestions, {'lottery_question_1': correct_values[0], 'lottery_question_2': correct_values[1], 'lottery_question_3': correct_values[2],
										   'lottery_question_4': wrong_values[3]} )
			#Had the following yield for when it had 5 questions, will leave in here for that possible eventuality
			#yield SubmissionMustFail(views.LotteryQuestions, {'lottery_question_1': correct_values[0], 'lottery_question_2': correct_values[1], 'lottery_question_3': correct_values[2],
			#							   'lottery_question_4': correct_values[3]} )
			#Try the correct options to see if it goes through to the next page
			yield(views.LotteryQuestions, {'lottery_question_1': correct_values[0], 'lottery_question_2': correct_values[1], 'lottery_question_3': correct_values[2],
										   'lottery_question_4': correct_values[3]} )
		#Based on the case, here we are simply testing the forms themselves not entirely how a person will interact with them, since they should choose B, once B has been chosen.	 
		if self.case == 'random':
			#Choice a random choice between A or B as chosen from the choices array above
			yield (views.Round, {'submitted_answer_1': random.choice(choices), 'submitted_answer_2': random.choice(choices), 'submitted_answer_3': random.choice(choices),
								 'submitted_answer_4': random.choice(choices), 'submitted_answer_5': random.choice(choices), 'submitted_answer_6': random.choice(choices),
								 'submitted_answer_7': random.choice(choices), 'submitted_answer_8': random.choice(choices), 'submitted_answer_9': random.choice(choices),
								 'submitted_answer_10': random.choice(choices), 'submitted_answer_11': random.choice(choices), 'submitted_answer_12': random.choice(choices),
								 'submitted_answer_13': random.choice(choices), 'submitted_answer_14': random.choice(choices)})
		elif self.case == 'halfAhalfB':
			#Choose the optimal choice and test it, Half of the choices A, the other half B
			yield (views.Round, {'submitted_answer_1': 'A', 'submitted_answer_2': 'A', 'submitted_answer_3': 'A',
								 'submitted_answer_4': 'A', 'submitted_answer_5': 'A', 'submitted_answer_6': 'B',
								 'submitted_answer_7': 'A', 'submitted_answer_8': 'B', 'submitted_answer_9': 'B',
								 'submitted_answer_10': 'B', 'submitted_answer_11': 'B', 'submitted_answer_12': 'B',
								 'submitted_answer_13': 'B', 'submitted_answer_14': 'B'})
		elif self.case == 'AllA':
			#Choose all the choices as A
			yield (views.Round, {'submitted_answer_1': 'A', 'submitted_answer_2': 'A', 'submitted_answer_3': 'A',
								 'submitted_answer_4': 'A', 'submitted_answer_5': 'A', 'submitted_answer_6': 'A',
								 'submitted_answer_7': 'A', 'submitted_answer_8': 'A', 'submitted_answer_9': 'A',
								 'submitted_answer_10': 'A', 'submitted_answer_11': 'A', 'submitted_answer_12': 'A',
								 'submitted_answer_13': 'A', 'submitted_answer_14': 'A'})
		elif self.case == 'AllB':
			#Choose all the choices as B
			yield (views.Round, {'submitted_answer_1': 'B', 'submitted_answer_2': 'B', 'submitted_answer_3': 'B',
								 'submitted_answer_4': 'B', 'submitted_answer_5': 'B', 'submitted_answer_6': 'B',
								 'submitted_answer_7': 'B', 'submitted_answer_8': 'B', 'submitted_answer_9': 'B',
								 'submitted_answer_10': 'B', 'submitted_answer_11': 'B', 'submitted_answer_12': 'B',
								 'submitted_answer_13': 'B', 'submitted_answer_14': 'B'})