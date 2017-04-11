from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants

class ResultsSummary(Page):
	def vars_for_template(self):
		neg = False
		if(self.player.participant.vars['funds'] < 0):
			neg = True
		return {
			'total_payoff': self.participant.vars['lotPayoff'],
			'paying_round': self.session.vars['paying_round'],
			'ball_number': self.session.vars['ball_number'],
			'paying_line': self.session.vars['paying_line'],
			'bio_funds': abs(self.player.participant.vars['funds']),
			'name': self.player.participant.vars['name'],
			'neg' : neg,
		}


class Questioner(Page):
	def is_displayed(self):
		return self.subsession.round_number == Constants.num_rounds

	form_model = models.Player

	def get_form_fields(self):
		return ['questioner_{}'.format(i) for i in range(1, Constants.num_questions - 1)]
	
page_sequence = [
	Questioner,
	ResultsSummary,
	
]
