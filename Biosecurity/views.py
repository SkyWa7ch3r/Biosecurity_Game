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
		cost_factor = self.session.config['max_protection']/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
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
		#Lists to pass to the template
		names = []
		pledge_results = []
		average = []
		#If True, round number > contribution_looper
		abovec = False
		#Check if a apprval by contribution has taken place
		if(self.subsession.round_number > self.session.config["contribution_looper"]):
			abovec = True
		#Get the data for the lists to pass them to the template
		for p in self.group.get_players():
			#Get the Player's name
			names.append(p.participant.vars["name"])
			#Get their latest Individual pledge for display
			pledge_results.append(p.participant.vars["Recent_Pledge"][1])
			#If Approval by Pledging or approval contribution on, get the approval data
			if(self.session.config["Papproval"] or (self.session.config["Capproval"] and abovec)):
				average.append(self.group.get_player_by_id(1).participant.vars["approval_means"][p.id_in_group - 1])
			else:
				average.append(None)
		#Get the max protection for display
		if(self.session.config['dynamic_finances'] == False):
			max_protection = self.session.config['max_protection']
		else:
			max_protection = Constants.maxProtection[self.subsession.round_number-1]
		#This is the logic for the counters till the next contribution or pledge
		if(self.group.pledge == True):
			#Reset the counter if its a round where a pledge took place
			if(self.subsession.round_number == 1):
				#Special case for Round 1 as it happens in one less round than usual.
				self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] = self.session.config["pledge_looper"] - 1
			else:
				self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] = self.session.config["pledge_looper"]
		#Reset the counter if contribution taking place this round
		if(self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] == 0):
			self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] = self.session.config["contribution_looper"]
			#Tell the game a contribution is happening and to save it in the data
			self.group.contribution = True
		#Calculate the cost factor
		cost_factor = self.session.config['max_protection']/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
		
		return {
			'max_protection': max_protection,
			'cost_factor': cost_factor,
			'funds': self.player.participant.vars['funds'],
			'calc': self.session.config['calculator'],
			'list' : zip(names, pledge_results, average),
			'pledge' : self.session.config['pledge'],
			'Group_Target_Prob' : self.participant.vars["Group_Targets_Prob"][1],
			'next_pledge' : self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"],
			'next_cont' : self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"],
			'cont_TF' : self.group.contribution,
			'Capproval' : self.session.config["Capproval"],
			'Papproval' : self.session.config["Papproval"],
			'player_name' : self.player.participant.vars["name"],
			'abovec' : abovec,
			'prob_coeff' : self.session.config["probability_coefficient"],
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
		cost_factor = self.session.config['max_protection']/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
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
	The WaitforEveryone class is responsible for displaying a basic wait page. 
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
		#Grab all the necessary data
		for p in self.group.get_players():
			names.append(p.participant.vars["name"])
			costs.append(p.cost)
		#Get all the values for display
		if(self.session.config['dynamic_finances'] == False):
			revenue = self.session.config['revenue']
			upkeep = self.session.config['upkeep']
		else:
			revenue = Constants.revenue[self.subsession.round_number-1]
			upkeep = Constants.upkeep[self.subsession.round_number-1]
		#Do a check so that the template knows to display negative currency properly
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
		#Put in the data that it was a pledging round
		self.group.pledge = True
		#This will calculate the Group Target and save it inside a participant variable, Group Targets as the most recent in the list
		self.group.calculate_group_target()

class PledgeWaitCounter(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == True
	def after_all_players_arrive(self):
		#Take 1 off the pledge counter to adjust its display
		self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] -= 1
		#If contribution is on, take 1 off the counter and calculate the mean approvals if its a contribution round
		if(self.session.config["Capproval"]):
			self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] -= 1
			if(self.subsession.round_number % self.session.config["contribution_looper"] == 0):
				self.group.calculate_mean_approval()
		
class AopWait(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.session.config['Papproval'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
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
	#Displays on a pledging round
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
	def vars_for_template(self):
		#Get the max protection and cost factor the slider calculations
		max_protection = self.session.config['max_protection']
		cost_factor = self.session.config['max_protection']/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
		return {
			'Group_Target_Prob' : self.participant.vars["Group_Targets_Prob"][1],
			'max_protection' : max_protection,
			'cost_factor' : cost_factor,
			'prob_coeff' : self.session.config["probability_coefficient"],
			'player_name' : self.player.participant.vars["name"],
		}

class IndiPledgingWait(WaitPage):
	def after_all_players_arrive(self):
		for p in self.group.get_players():
			#Adjust the Most Recent Pledge by each player accordingly
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
	#Set the minimum for minimum amount of chance that someone is not the source of incursion in the case of timeout
	def before_next_page(self):
		if self.timeout_happened:
			self.player.groupTarget = self.session.config["probability_coefficient"] * 100
	def is_displayed(self):
		return self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
	def vars_for_template(self):
		return {
			'player_name' : self.player.participant.vars["name"],
			'prob_coeff' : self.session.config['probability_coefficient'] * 100,
		}
		
class PledgingApproval(Page):
	"""
	The PledgingApproval class does the logic for the Pledging Approval page
	"""
	timeout_seconds = 90
	form_model= models.Player
	#Upto 20 players for 20 approvals, gets sent to the Player class
	def get_form_fields(self):
		approval = ['approval_{}'.format(i) for i in range(1, self.session.config["players_per_group"] + 1)]
		return approval
	#Display if its a pledging round and Approval of Pledges is on
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.session.config['Papproval'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 0 or self.subsession.round_number == 1)
	def vars_for_template(self):
		names = []
		ids = []
		pledge_results = []
		#Get the names, ids and individual pledges of each player and store them in the respective lists above
		for p in self.group.get_players():
			names.append(p.participant.vars['name'])
			ids.append(p.id_in_group)
			pledge_results.append(p.participant.vars["Recent_Pledge"][1])
		#Zip the 3 lists together so you have {(Player 1 Name, 1, Player 1 Pledge), (Player 2 Name, 2, Player 2 Pledge), ...,(Player n Name, n, Player n Pledge)}
		return {
			'list' : zip(ids, names, pledge_results),
			'Group_Target_Prob' : self.participant.vars["Group_Targets_Prob"][1],
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
	#Upto 20 players for 20 approvals, gets sent to the Player class
	def get_form_fields(self):
		approval = ['approval_{}'.format(i) for i in range(1, self.session.config["players_per_group"] + 1)]
		return approval
	#Display if its a contribution round and Approval of Contribution is on is on
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
			'''
			If the contribution_looper is not 1 and is same as pledge_looper then get previous pledge, as pledge and contribution happening on same round
			ELSE
			In the case that contribution_looper = pledge_looper and both are 1 then pledging and contribution is happening every round,
			then each pledge will affect contribution for every round.
			OR
			In the case when contribution_looper < pledge_looper, then grab the most recent pledges
			'''
			if(self.session.config["contribution_looper"] == self.session.config["pledge_looper"] and self.session.config["contribution_looper"] != 1):
				pledge_results.append(p.participant.vars["Recent_Pledge"][0])
			elif((self.session.config["contribution_looper"] == 1 and self.session.config["contribution_looper"] == self.session.config["pledge_looper"]) or (self.session.config["contribution_looper"] < self.session.config["pledge_looper"])):
				pledge_results.append(p.participant.vars["Recent_Pledge"][1])	
			results.append(p.participant.vars["Protection_Provided"])
		for i in range(self.subsession.round_number - self.session.config["contribution_looper"] + 1, self.subsession.round_number + 1):
			round_numbers.append(i)
		#Determine What Group_Target_Prob we need, exactly like getting the Recent Pledge
		#By Default, it does when contribution_looper = pledge_looper when contribution_looper != 1, which will mean it chooses the previous pledge
		gtp = self.participant.vars["Group_Targets_Prob"][0]
		'''
		In the case that contribution_looper = pledge_looper and both are 1 then pledging and contribution is happening every round,
		then each pledge will affect contribution for every round.
		OR
		In the case when contribution_looper < pledge_looper, then grab the most recent pledges
		'''
		if((self.session.config["contribution_looper"] == 1 and self.session.config["contribution_looper"] == self.session.config["pledge_looper"]) or (self.session.config["contribution_looper"] < self.session.config["pledge_looper"])):
			gtp = self.participant.vars["Group_Targets_Prob"][1]
		return {
			'list_for_table' : zip(names, ids, pledge_results, results),
			'round_numbers' : round_numbers,
			'Group_Target_Prob' : gtp,
			'player_name': self.player.participant.vars['name'],
			'contribution_looper' : self.session.config["contribution_looper"],
		}
'''
The Below Wait Pages are specifically there to reduce the amount of wait pages
'''
class WaitforChat(WaitPage):
	def is_displayed(self):
		return self.session.config['player_communication']
		
class WaitforInstructions(WaitPage):
	def is_displayed(self):
		return self.subsession.round_number == 1
		
class NoPledgeResultWaitPage(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == False or (self.session.config['Capproval'] and self.session.config['pledge'] == True and self.subsession.round_number % self.session.config['contribution_looper'] == 0)
"""
	page_sequence determines the order in which pages are displayed.
"""

page_sequence = [
	BioInstructions,
	WaitforInstructions,
	GroupPledging,
	PledgeWait,
	IndiPledging,
	IndiPledgingWait,
	PledgingApproval,
	AopWait,
	ChatBox,
	WaitforChat,
	SoloRound,
	WaitforEveryone,
	OthersRound,
	Round,
	ResultsWaitPage,
	Results,
	NoPledgeResultWaitPage,
	ActionApproval,
	PledgeWaitCounter,
]


