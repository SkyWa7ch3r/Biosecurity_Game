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
	def vars_for_template(self):
		return {
		'name' : self.player.participant.vars['name'],
		'monitoring' : self.session.config["monitoring"],
		'chat' : self.session.config["player_communication"],
		'pledge' : self.session.config["pledge"],
		'Papproval' : self.session.config["Papproval"],
		'Capproval' : self.session.config["Capproval"],
		'calc' : self.session.config["calculator"],
		'leader' : self.session.config["set_leader"],
		'dynamic_finances' : self.session.config["dynamic_finances"],
		'plooper' : self.session.config["pledge_looper"],
		'clooper' : self.session.config["contribution_looper"],
		'max_protection' : self.session.config["max_protection"],
		'upkeep' : self.session.config["upkeep"],
		'revenue' : self.session.config["revenue"],
		'starting_funds' : self.session.config["starting_funds"],
		}

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
				self.player.cost= random.uniform(0.00,Constants.maxProtection[self.subsession.round_number-1])

	#Output protection and cost_factor values to results
	def vars_for_template(self):
		if(self.session.config['dynamic_finances'] == False):
			max_protection = self.session.config['max_protection']
		else:
			max_protection = Constants.maxProtection[self.subsession.round_number-1]
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
				self.player.cost= random.uniform(0.00,Constants.maxProtection[self.subsession.round_number-1])

	#Output protection and cost_factor values to results
	def vars_for_template(self):
		names = []
		pledge_results = []
		average = []
		abovec = False
		contribution = False
		#Getting average approval p.participant.vars["approval_means"][p.id_in_group - 1]
		if(self.subsession.round_number > self.session.config["contribution_looper"]):
			abovec = True
		for p in self.group.get_players():
			names.append(p.participant.vars["name"])
			pledge_results.append(p.participant.vars["Recent_Pledge"][1])
			if(self.session.config["Papproval"]):
				average.append(p.participant.vars["approval_means"][p.id_in_group - 1])
			elif(self.session.config["Capproval"] and abovec):
				average.append(p.participant.vars["approval_means"][p.id_in_group - 1])
			else:
				average.append(None)
		if(self.session.config['dynamic_finances'] == False):
			max_protection = self.session.config['max_protection']
		else:
			max_protection = Constants.maxProtection[self.subsession.round_number-1]
		if(self.group.get_player_by_id(1).participant.vars["pledge_round"] == True):
			if(self.subsession.round_number == 1):
				self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] = self.session.config["pledge_looper"] - 1
			else:
				self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] = self.session.config["pledge_looper"]
		if(self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] == 0):
			self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] = self.session.config["contribution_looper"]
			contribution = True
		cost_factor = max_protection/-math.log(1 + 0.4 - 0.99)
		
		return {
			'max_protection': max_protection,
			'cost_factor': cost_factor,
			'funds': self.player.participant.vars['funds'],
			'calc': self.session.config['calculator'],
			'list' : zip(names, pledge_results, average),
			'pledge' : self.session.config['pledge'],
			'Group_Target_Prob' : self.participant.vars["Group_Targets_Prob"][1],
			'Group_Target_Cost' : self.participant.vars["Group_Targets_Cost"][1],
			'next_pledge' : self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"],
			'next_cont' : self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"],
			'cont_TF' : contribution,
			'Capproval' : self.session.config["Capproval"],
			'Papproval' : self.session.config["Papproval"],
			'player_name' : self.player.participant.vars["name"],
			'abovec' : abovec,
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
				self.player.cost= random.uniform(0.00,Constants.maxProtection[self.subsession.round_number-1])
	 #Output protection and cost_factor values to results
	def vars_for_template(self):
		if(self.session.config['dynamic_finances'] == False):
			max_protection = self.session.config['max_protection']
		else:
			max_protection = Constants.maxProtection[self.subsession.round_number-1]
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
		names = []
		costs = []
		for p in self.group.get_players():
			names.append(p.participant.vars["name"])
			costs.append(p.cost)
		if(self.session.config['dynamic_finances'] == False):
			revenue = self.session.config['revenue']
			upkeep = self.session.config['upkeep']
		else:
			revenue = Constants.revenue[self.subsession.round_number-1]
			upkeep = Constants.upkeep[self.subsession.round_number-1]
		if(self.player.participant.vars['funds'] < 0.00):
			negative = True
			currentFunds = currentFunds * -1.00
		return {
			'results': zip(names, costs),
			'funds': currentFunds,
			'name': self.player.participant.vars['name'],
			'upkeep': c(upkeep),
			'revenue': c(revenue),
			'total_cost': self.player.cost + c(self.session.config['upkeep']),
			'monitoring' : self.session.config['monitoring'],
			'neg' : negative,
		}

#PLEDGING CLASSES BEGIN HERE
class PledgeWait(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
	def after_all_players_arrive(self):
		#This will calculate the Group Target and save it inside a particxpant variable, Group Targets as the most recent in the list
		self.group.get_player_by_id(1).participant.vars['pledge_round'] = True
		self.group.calculate_group_target()

class PledgeWaitCounter(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == True
	def after_all_players_arrive(self):
		self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] -= 1
		self.group.get_player_by_id(1).participant.vars['pledge_round'] = False
		if(self.session.config["Capproval"]):
			self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] -= 1
class AopWait(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.session.config['Papproval'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
	def after_all_players_arrive(self):
		#Calculates the approval averages for each player and stores them in a participant list, with the index matching the id_in_group for each player
		self.group.calculate_mean_approval()
		
class AocWait(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.session.config['Capproval'] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0
	def after_all_players_arrive(self):
		#Calculates the approval averages for each player and stores them in a participant list, with the index matching the id_in_group for each player
		self.group.calculate_mean_approval()
		
class IndiPledging(Page):
	"""
	The IndiPledging class does the logic for the Individual Pledging Page
	"""
	form_model = models.Player
	form_fields = ['individualPledge']
	timeout_seconds = 60
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
	def vars_for_template(self):
		max_protection = self.session.config['max_protection']
		cost_factor = max_protection/-math.log(0.01)
		return {
			'Group_Target_Prob' : self.participant.vars["Group_Targets_Prob"][1],
			'Group_Target_Cost' : self.participant.vars["Group_Targets_Cost"][1],
			'max_protection' : max_protection,
			'cost_factor' : cost_factor,
		}

class IndiPledgingWait(WaitPage):
	def after_all_players_arrive(self):
		for p in self.group.get_players():
			p.participant.vars["Recent_Pledge"][0] = p.participant.vars["Recent_Pledge"][1]
			p.participant.vars["Recent_Pledge"][1] = p.individualPledge
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
		
class GroupPledging(Page):
	"""
	The GroupPledging class does the logic for the Group Pledging Page
	"""
	timeout_seconds = 60
	form_model = models.Player
	form_fields = ['groupTarget']
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
	def vars_for_template(self):
		return {
			'player_name' : self.player.participant.vars["name"],
		}
		
class PledgingApproval(Page):
	"""
	The PledgingApproval class does the logic for the Pledging Approval page
	"""
	timeout_seconds = 90
	form_model= models.Player
	def get_form_fields(self):
		approval = ['approval_{}'.format(i) for i in range(1, self.session.config["players_per_group"] + 1)]
		return approval
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.session.config['Papproval'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
	def vars_for_template(self):
		names = []
		ids = []
		pledge_results = []
		for p in self.group.get_players():
			names.append(p.participant.vars['name'])
			ids.append(p.id_in_group)
			pledge_results.append(p.participant.vars["Recent_Pledge"][1])
		return {
			'list' : zip(ids, names, pledge_results),
			'Group_Target_Prob' : self.participant.vars["Group_Targets_Prob"][1],
			'Group_Target_Cost' : self.participant.vars["Group_Targets_Cost"][1],
			'player_name' : self.player.participant.vars["name"],
			'pledge_looper' : self.session.config["pledge_looper"],
		}
		
class ActionApproval(Page):
	"""
	The ActionApproval class does the logic for the Action Approval page, essentially the same as the pledging approval
	class just some small changes to reflect for it to come up on a different time compared to the approval for pledges.
	This class will also replace the results page in the case of approval by contributions.
	"""
	timeout_seconds = 90
	form_model= models.Player
	def get_form_fields(self):
		approval = ['approval_{}'.format(i) for i in range(1, self.session.config["players_per_group"] + 1)]
		return approval
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.session.config['Capproval'] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0
	def vars_for_template(self):
		#List of names
		names = []
		#List of ID's in the player's respective groups
		ids = []
		#The Pledge that was made over the last ["pledge_looper"] rounds
		pledge_results = []
		#This will be a list of lists of the protection provided from each player from the last ["pledge_looper"] rounds
		results = []
		#List of Round Numbers from Current Round to Current Round -  ["Pledge_Looper"]
		round_numbers = []
		for p in self.group.get_players():
			names.append(p.participant.vars['name'])
			ids.append(p.id_in_group)
			pledge_results.append(p.participant.vars["Recent_Pledge"][0])
			results.append(p.participant.vars["Protection_Provided"])
		for i in range(self.subsession.round_number - self.session.config["contribution_looper"] + 1, self.subsession.round_number + 1):
			round_numbers.append(i)
		return {
			'list_for_table' : zip(names, ids, pledge_results, results),
			'round_numbers' : round_numbers,
			'Group_Target_Prob' : self.participant.vars["Group_Targets_Prob"][0],
			'Group_Target_Cost' : self.participant.vars["Group_Targets_Cost"][0],
			'player_name': self.player.participant.vars['name'],
			'contribution_looper' : self.session.config["contribution_looper"],
		}	
"""
	page_sequence determines the order in which pages are displayed.
"""

page_sequence = [
	BioInstructions,
	WaitforEveryone,
	GroupPledging,
	PledgeWait,
	IndiPledging,
	IndiPledgingWait,
	ChatBox,
	WaitforEveryone,
	PledgingApproval,
	AopWait,
	SoloRound,
	WaitforEveryone,
	OthersRound,
	Round,
	ResultsWaitPage,
	Results,
	WaitforEveryone,
	ActionApproval,
	AocWait,
	PledgeWaitCounter,
]


