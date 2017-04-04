from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants

# html template for the Introduction
class Introduction(Page):
	# Display this page only once
	form_model = models.Player
	form_fields = ['participant_label']
	def before_next_page(self):
		self.player.set_participation_label()
	def is_displayed(self):
		return self.subsession.round_number == 1

	# Pass the variables to the html template
	def vars_for_template(self):
		return{
			'communication': self.session.config['player_communication'],
		}
		
# html template for the lottery instructions
class LotteryInstructions(Page):
	# Display this page only once
	def is_displayed(self):
		return self.subsession.round_number == 1
	
# html template for Lottery Questions
class LotteryQuestions(Page):
	# Display this page only once
	def is_displayed(self):
		return self.subsession.round_number == 1

	form_model = models.Player
	
	# create the pre lottery questions form fields
	def get_form_fields(self):
		return ['lottery_question_{}'.format(i) for i in range(1, Constants.num_lotery_questions + 1)]

# Passes the variables to the html template
class Round(Page):
	form_model = models.Player
	form_fields = ['submitted_answer']

	# create the lottery form fields
	def get_form_fields(self):
		return ['submitted_answer_{}'.format(i) for i in range(1,
															   Constants.round_lengths[self.subsession.round_number] -
															   Constants.round_lengths[
																   self.subsession.round_number - 1] + 1)]
	# call the model methods to do the game and player processing
	def before_next_page(self):
		self.player.set_submits()
		self.player.set_payoff()
		player_in_all_rounds = self.player.in_all_rounds()
		self.participant.vars['lotPayoff'] = sum([p.payoff for p in player_in_all_rounds])

	# Pass the variables to the html template
	def vars_for_template(self):
	
		# read the indices for the values list for the corresponding lottery round
		index_l = Constants.round_lengths[self.subsession.round_number - 1]
		index_h = Constants.round_lengths[self.subsession.round_number]
		game_number = [Constants.values[i]['game_number'] for i in range(index_l, index_h)]

		# use the above index to pass appropriate values
		return {
			'number_of_games': range(1, index_h - index_l + 1),
			'balls_a_r': "%s" % (Constants.values[index_l]['a_best_ball_range']),
			'balls_a_w': "%s" % (Constants.values[index_l]['a_worst_ball_range']),
			'balls_b_r': "%s" % (Constants.values[index_l]['b_best_ball_range']),
			'balls_b_w': "%s" % (Constants.values[index_l]['b_worst_ball_range']),
			'game_number': game_number,
			'a_values_r': [Constants.values[i]['a_best'] for i in range(index_l, index_h)],
			'a_values_w': [Constants.values[i]['a_worst'].replace('-','') for i in range(index_l, index_h)],
			'b_values_r': [Constants.values[i]['b_best'] for i in range(index_l, index_h)],
			'b_values_w': [Constants.values[i]['b_worst'].replace('-','') for i in range(index_l, index_h)],
			'start_game': game_number[0],
			'end_game': game_number[-1],
		}


# A wait page displayed when required 
class ResultsWaitPage(WaitPage):
	def is_displayed(self):
		return self.subsession.round_number == 1

	# A wait page displayed when required 
class EndGame(WaitPage):
	def is_displayed(self):
		return self.subsession.round_number == Constants.num_rounds

# Specify the sequence of the app
page_sequence = [
	Introduction,
	LotteryInstructions,
	ResultsWaitPage,
	LotteryQuestions,
	ResultsWaitPage,
	Round,
	EndGame,
]
