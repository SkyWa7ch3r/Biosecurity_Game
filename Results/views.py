from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class Results(Page):
    pass

class ResultsSummary(Page):
    def vars_for_template(self):
        return {
            'total_payoff': self.participant.vars['lotPayoff'],
            'paying_round': self.session.vars['paying_round'],
            'ball_number': self.session.vars['ball_number'],
            'paying_line': self.session.vars['paying_line'],
            'bio_funds': self.player.participant.vars['funds'],
            'name': self.player.participant.vars['name'],
        }


class Questioner(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    form_model = models.Player

    def get_form_fields(self):
        return ['questioner_{}'.format(i) for i in range(1, 17)]
    
page_sequence = [
    Questioner,
    ResultsSummary,
    
]
