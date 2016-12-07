from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants

import random
import math
"""
This is the Biosecurity Game views.py, in here are methods which alter how a page or
template is shown based on different factors. This file is also where the page sequence
is stored that determines the order in which templates are shown using their respective
method.
"""


class BioInstructions(Page):
    doc="""
    The BioInstructions class is responsible for determining when and how to display the
    BioInstructions.html page.
    """
    def is_displayed(self):
        return self.subsession.round_number == 1

class SoloRound(Page):
    doc="""
    The SoloRound page only displays to the "leader" player (if lead_player is enabled only).
    Gets cost from player and outputs protection and cost_factor to SoloRounds.html
    """

    def is_displayed(self):
        return self.session.config['set_leader'] and self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group 
    form_model = models.Player
    form_fields = ['cost']
    timeout_seconds = 90
    #In the event of a timeout or move on from admin, it will produce a random integer for protection
    def before_next_page(self):
        if self.timeout_happened:
            if(self.session.config['dynamic_finances'] == False):
                self.player.cost= random.uniform(0.00, self.session.config['max_protection'])
            else:
                self.player.cost= random.uniform(0.00,self.subsession.maxProtection[self.subsession.round_number-1])

    #Output protection and cost_factor values to results
    def vars_for_template(self):
        if(self.session.config['dynamic_finances'] == False):
            max_protection = self.session.config['max_protection']
        else:
            max_protection = self.subsession.maxProtection[self.subsession.round_number-1]
        cost_factor = max_protection/-math.log(0.01)
        return {
            'max_protection': max_protection,
            'cost_factor': cost_factor,
			'funds': self.player.participant.vars['funds'],
        }

class Round(Page):

    doc="""
    The Round class is responsible for determining when and how to display the
    Round.html page. It also initialises the forms used each round and uses timeout_seconds
    to automatically push the experiment forward. This page does not display if the lead_player feature is active
    """

    def is_displayed(self):
        return self.session.config['set_leader'] == False
    form_model = models.Player
    form_fields = ['cost']
    timeout_seconds = 90
    #In the event of a timeout or move on from admin, it will produce a random integer for protection
    def before_next_page(self):
        if self.timeout_happened:
            if(self.session.config['dynamic_finances'] == False):
                self.player.cost= random.uniform(0.00, self.session.config['max_protection'])
            else:
                self.player.cost= random.uniform(0.00,self.subsession.maxProtection[self.subsession.round_number-1])

    #Output protection and cost_factor values to results
    def vars_for_template(self):
        if(self.session.config['dynamic_finances'] == False):
            max_protection = self.session.config['max_protection']
        else:
            max_protection = self.subsession.maxProtection[self.subsession.round_number-1]
        cost_factor = max_protection/-math.log(0.01)
        return {
            'max_protection': max_protection,
            'cost_factor': cost_factor,
			'funds': self.player.participant.vars['funds'],
			'calc': self.session.config['calculator'],
        }

class OthersRound(Page):

    """
    The OthersRound class is responsible for determining when and how to display the
    OthersRound.html page. It also initialises the forms used each round and uses timeout_seconds
    to automatically push the experiment forward. This page displays only if the lead_player feature is active and only for non-leader players
    """
    def is_displayed(self):
        return (self.session.config['set_leader'] and self.player.id_in_group != self.group.get_player_by_role('Leader').id_in_group)
    form_model = models.Player
    form_fields = ['cost']
    timeout_seconds = 90
    #In the event of a timeout or move on from admin, it will produce a random integer for protection
    def before_next_page(self):
        if self.timeout_happened:
            if(self.session.config['dynamic_finances'] == False):
                self.player.cost= random.uniform(0.00, self.session.config['max_protection'])
            else:
                self.player.cost= random.uniform(0.00,self.subsession.maxProtection[self.subsession.round_number-1])
     #Output protection and cost_factor values to results
    def vars_for_template(self):
        if(self.session.config['dynamic_finances'] == False):
            max_protection = self.session.config['max_protection']
        else:
            max_protection = self.subsession.maxProtection[self.subsession.round_number-1]
        cost_factor = max_protection/-math.log(0.01)
        #print leader's contribution to html page
        return {
            'leader' : self.group.get_player_by_role('Leader').participant.vars['name'],
            'leader_protection' : self.group.get_player_by_role('Leader').cost,
            'max_protection': max_protection,
            'cost_factor': cost_factor,
			'funds': self.player.participant.vars['funds'],
        }
    

class ChatBox(Page):
    """
    The ChatBox class is responsible for determining when and how to display the
    ChatBox.html page. Displays the chat box only if player communication is
    enabled and every fifth round. Uses timeout_seconds to limit communication and
    continue the experiment.
    """
    def is_displayed(self):
        return self.session.config['player_communication'] == True and (self.round_number == 1 or self.round_number == 6 or self.round_number == 11)
    def vars_for_template(self):
        return {
            'groupNum': self.group.id,
            'name': self.player.participant.vars['name'],
            'session_id': self.subsession.session.id,
        }
    timeout_seconds = 90


class ResultsWaitPage(WaitPage):
    """
    The ResultsWaitPage class is responsible for determining when to display a
    wait page as well as calculate the profits for its respective round.
    """
    def after_all_players_arrive(self):
         self.group.calculate_profits()


class WaitforEveryone(WaitPage):
    """
    The WaitforEveryone class is responsible for displaying a wait page. 
    """
    pass

class Results(Page):
	"""
    The Results class is responsible for determining when and how to display the
    Results.html page. Displays the outcome for the biosecurity round and determines
    revenue and current funds. Returns the following:
    results_list: Outcome for round
    funds: Current funds
    name: Randomly assigned player name at the start of experiment
    upkeep: Constant cost for producing a product
    revenue: Income gained from no occursion 
    total_cost: Amount of protection used + constant upkeep = cost for the round
    independant of outcome.
	"""
	def vars_for_template(self):
		results = []
		negative = False
		currentFunds = self.player.participant.vars['funds']
		for p in self.group.get_players():
			string = "%s --- Protection: $%.2f" % (p.participant.vars['name'], p.cost)
			results.append(string)
		if(self.session.config['dynamic_finances'] == False):
			revenue = self.session.config['revenue']
			upkeep = self.session.config['upkeep']
		else:
			revenue = self.subsession.revenue[self.subsession.round_number-1]
			upkeep = self.subsession.upkeep[self.subsession.round_number-1]
		if(self.player.participant.vars['funds'] < 0.00):
			negative = True
			currentFunds = currentFunds * -1.00
		return {
			'results_list': results,
			'funds': currentFunds,
			'name': self.player.participant.vars['name'],
			'upkeep': c(upkeep),
			'revenue': c(revenue),
			'total_cost': self.player.cost + c(self.session.config['upkeep']),
			'basic' : self.session.config['basic'],
			'neg' : negative,
		}

class IndiPledging(Page):
	"""
	The IndiPledging class does the logic for the Individual Pledging Page
	"""
	timeout_seconds = 60
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.round_number == 1 or self.round_number == 6 or self.round_number == 11)
	def vars_for_template(self):
		max_protection = self.session.config['max_protection']
		cost_factor = max_protection/-math.log(0.01)
		return {
			'max_protection' : max_protection,
			'cost_factor' : cost_factor,
		}

class GroupPledging(Page):
	"""
	The GroupPledging class does the logic for the Group Pledging Page
	"""
	timeout_seconds = 60
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.round_number == 1 or self.round_number == 6 or self.round_number == 11)
		
class PledgingApproval(Page):
	"""
	The Approval vlass does the logic for the Approval page
	"""
	timeout_seconds = 60
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.round_number == 1 or self.round_number == 6 or self.round_number == 11)

class ActionApproval(Page):
	"""
	The Approval vlass does the logic for the Approval page
	"""
	timeout_seconds = 60
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.round_number == 6 or self.round_number == 11)
"""
    page_sequence determines the order in which pages are displayed.
"""

page_sequence = [
    BioInstructions,
    WaitforEveryone,
	ActionApproval,
	WaitforEveryone,
	GroupPledging,
	WaitforEveryone,
	IndiPledging,
	WaitforEveryone,
    ChatBox,
	WaitforEveryone,
	PledgingApproval,
	WaitforEveryone,
    SoloRound,
    WaitforEveryone,
    OthersRound,
    Round,
    ResultsWaitPage,
    Results,
    WaitforEveryone,
]


