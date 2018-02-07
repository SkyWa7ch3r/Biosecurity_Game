from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants

class ResultsSummary(Page):
	'''
		The final page of the entire experiment which shows the result for the entire game.
	'''
	def vars_for_template(self):
		#Have booleans to ensure negatives appear properly
		bioneg = False
		lotneg = False
		if(self.player.participant.vars['funds'] < 0):
			bioneg = True
		if(self.participant.vars['lotPayoff'] < 0):
			lotneg = True
		return {
			'total_payoff': abs(self.participant.vars['lotPayoff']),
			'paying_round': self.session.vars['paying_round'],
			'ball_number': self.session.vars['ball_number'],
			'paying_line': self.session.vars['paying_line'],
			'bio_funds': abs(self.player.participant.vars['funds']),
			'name': self.player.participant.vars['name'],
			'bioneg' : bioneg,
			'lotneg' : lotneg,
		}


class Questioner(Page):
	'''
		This is the survey which asks participants questions about their experience with the game, general trust and economic questions
		as well as questions relating to their socio-economic background.
	'''
	form_model = models.Player

	def get_form_fields(self):
		return ['questioner_{}'.format(i) for i in range(1, Constants.num_questions - 1)]
	
class CheckPayments(WaitPage):
	def after_all_players_arrive(self):
		for p in self.group.get_players():
			#If a participant won money in the Lottery game but lost money in the Biosecurity then...
			if(p.participant.vars['lotPayoff'] > 0 and p.participant.vars['funds'] < 0):
				p.participant.payoff += abs(p.participant.vars['funds']);
			#If a participant lost money in the Lottery game but won money in the Biosecurity then...
			elif(p.participant.vars['lotPayoff'] < 0 and p.participant.vars['funds'] > 0):
				#If the lottery loss is larger than the biosecurity payoff
				if(p.participant.vars['lotPayoff'] > p.participant.vars['funds']):
					p.participant.payoff = 0
			#If a participant loses in both games then...
			elif(p.participant.vars['lotPayoff'] < 0 and p.participant.vars['funds'] < 0):
				p.participant.payoff = 0
			
page_sequence = [
	CheckPayments,
	Questioner,
	ResultsSummary,
	
]
