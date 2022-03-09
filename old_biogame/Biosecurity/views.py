from otree.api import Currency as c, currency_range, widgets
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
		loss = -self.session.config["upkeep"] - self.session.config["max_protection"]
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
		'loss' : abs(loss),
		}

class SoloRound(Page):
	doc="""
	The SoloRound page only displays to the "leader" player (if lead_player is enabled only).
	Gets cost from player and outputs protection and cost_factor to SoloRounds.html.
	
	THIS PAGE HASN"T BEEN FULLY TESTED AS IT WILL NOT BE USED FOR EXPERIMENTATION.
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
	Round.html page. It also initializes the forms used each round and uses timeout_seconds
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
			#DYNAMIC FINANCEWS HASN"T BEEN TESTED AS THIS WILL NOT BE USED IN EXPERIMENTATION
			if(self.session.config['dynamic_finances'] == False):
				self.player.cost= random.uniform(0.00, self.session.config['max_protection'])
			else:
				self.player.cost= random.uniform(0.00,Constants.maxProtection[self.subsession.round_number-1])

	#Output protection and cost_factor values to results
	def vars_for_template(self):
		#Lists to pass to the template
		#Holds the names
		names = []
		#Allows us to highlight player's name in a table
		name_true = []
		#This holds the pledges needed
		pledge_protection = []
		pledge_prob = []
		total_pledge = 0
		overall_pledge = 1
		#This holds the group approvals for players
		average = []
		#The below list will contain either black, red or green as a string for html styling.
		colours = []
		#If True, round number > contribution_looper
		abovec = False
		#Calculate the cost factor
		cost_factor = self.session.config['max_protection']/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
		#Check if a approval by contribution has taken place, if so change abovec to True
		if(self.subsession.round_number > self.session.config["contribution_looper"]):
			abovec = True
		#Get the data for the lists to pass them to the template
		for p in self.group.get_players():
			#Get the Player's name
			names.append(p.participant.vars["name"])
			#Add a boolean to name_true, True if the current player in the loop matches the player who submitted the form.
			if p.participant.vars["name"] == self.player.participant.vars["name"]:
				name_true.append(True)
			else:
				name_true.append(False)
			if self.session.config["pledge"] == True:
				#Get their latest Individual pledge for display
				pledge_protection.append(p.participant.vars["Recent_Pledge"][1])
				probability = 1-math.exp(-p.participant.vars["Recent_Pledge"][1]/cost_factor) + self.session.config["probability_coefficient"]
				pledge_prob.append(round(probability * 100, 2))
				#Update overall group values
				total_pledge += p.participant.vars["Recent_Pledge"][1]
				overall_pledge *= probability
				#If Approval by Pledging or approval contribution on, get the approval data
				if(self.session.config["Papproval"] or (self.session.config["Capproval"] and abovec)):
					average.append(self.group.get_player_by_id(1).participant.vars["approval_means"][p.id_in_group - 1])
					#Round the average number so participants only see whole numbers or integers
					average[-1] = int(round(average[-1], 0))
					#Add a colour to the colours based on the approval value.
					if average[-1] > 0:
						colours.append("green")
					elif average[-1] < 0:
						colours.append("red")
					else:
						colours.append("black")
				else:
					#For the zipping to work, all the lists need to be of equal length, thus adding Nones
					#to ensure that these lists when not used are the same length as the pledge_protection or names.
					average.append(None)
					colours.append(None)
				
		#Get the max protection for display
		if(self.session.config['dynamic_finances'] == False):
			max_protection = self.session.config['max_protection']
		else:
			max_protection = Constants.maxProtection[self.subsession.round_number-1]
		#This is the logic for the counters till the next contribution or pledge
		if(self.group.pledge == True):
			#Reset the counter if its a round where a pledge took place
			self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] = self.session.config["pledge_looper"]
		#Reset the counter if contribution taking place this round
		if(self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] == 0):
			self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] = self.session.config["contribution_looper"]
			#Tell the game a contribution is happening and to save it in the data
			self.group.contribution = True
		#By default this is false, until we reach the last pledge of the game, which this becomes true to prevent the pledge countdown appearing
		pledge_counter = True
		if(Constants.num_rounds - self.subsession.round_number < self.session.config["pledge_looper"]):
			pledge_counter = False
		#Now 'fix' the overall pledge protection values
		if(self.session.config['pledge'] == True):
			overall_pledge = round(overall_pledge * 100, 2)
		#Due to a change of appearance we need to change the contribution counter
		if not abovec:
			next_cont = self.session.config["contribution_looper"] - self.subsession.round_number + 1
		else:
			next_cont = self.group.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"]
		return {
			'max_protection': max_protection,
			'cost_factor': cost_factor,
			'funds': self.player.participant.vars['funds'],
			'calc': self.session.config['calculator'],
			'list' : zip(names, pledge_protection, pledge_prob, average, colours, name_true),
			'pledge' : self.session.config['pledge'],
			'Group_Target_Prob' : self.participant.vars["Group_Targets_Prob"][1],
			'next_pledge' : self.group.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"],
			'next_cont' : next_cont,
			'cont_TF' : self.group.contribution,
			'Capproval' : self.session.config["Capproval"],
			'Papproval' : self.session.config["Papproval"],
			'player_name' : self.player.participant.vars["name"],
			'abovec' : abovec,
			'prob_coeff' : self.session.config["probability_coefficient"],
			'revenue' : self.session.config["revenue"],
			'upkeep' : self.session.config["upkeep"],
			'pledge_counter' : pledge_counter,
			'total_pledge' : total_pledge,
			'overall_pledge' : overall_pledge,
			'advisory_column_length' : self.session.config["players_per_group"] + 4,
		}

class OthersRound(Page):

	"""
	The OthersRound class is responsible for determining when and how to display the
	OthersRound.html page. It also initialises the forms used each round and uses timeout_seconds
	to automatically push the experiment forward. This page displays only if the lead_player feature is active and only for non-leader players
	
	HASN"T BEEN FULLY TESTED AS IT WILL NOT BE USED IN EXPERIMENTATION
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
	

class Chat(Page):
	"""
	The ChatBox class is responsible for determining when and how to display the
	ChatBox.html page. Displays the chat box only if player communication is
	enabled and every fifth round. Uses timeout_seconds to limit communication and
	continue the experiment.
	"""
	timeout_seconds = 90
	def is_displayed(self):
		return self.session.config['player_communication'] == True and (self.round_number == 1 or self.round_number == 6 or self.round_number == 11)
	def vars_for_template(self):
		return {
			#'groupNum': self.group.id,
			'name': self.player.participant.vars['name'],
			#'session_id': self.subsession.session.id,
		}


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
	timeout_seconds = 60
	def vars_for_template(self):
		#List that holds all the results for display
		results = []
		#A boolean used to determine if the income is negative or not to ensure the negative is used properly on the page
		negative = False
		currentFunds = self.player.participant.vars['funds']
		#Holds the names for display
		names = []
		#Holds the costs for display
		costs = []
		#Holds the protection values (%) for display
		probabilities = []
		#Holds the pledges ($) for display
		pledges = []
		#Holds the pledge values (%) for display
		pledge_prob = []
		#Initialize the overall variables
		total_protection = 0
		total_pledge = 0
		overall_pledge = 1
		#Allows us to highlight player's name in a table
		name_true = []
		#Calculate the cost factor
		cost_factor = self.session.config['max_protection']/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
		#Grab all the necessary data
		for p in self.group.get_players():
			#Get the names
			names.append(p.participant.vars["name"])
			#To ensure that a player's name is highlighted
			if p.participant.vars["name"] == self.player.participant.vars["name"]:
				name_true.append(True)
			else:
				name_true.append(False)
			#Show most recent pledges if pledging is enabled
			if(self.session.config['pledge'] == True):
				pledges.append(p.participant.vars["Recent_Pledge"][1])
				probability = 1-math.exp(-p.participant.vars["Recent_Pledge"][1]/cost_factor) + self.session.config["probability_coefficient"]
				pledge_prob.append(round(probability * 100, 2))
				total_pledge += p.participant.vars["Recent_Pledge"][1]
				overall_pledge *= probability
			else:
				#To ensure zipping lists works, pledges must be same length as the other lists
				pledges.append(None)
				pledge_prob.append(None)
			costs.append(p.cost)
			total_protection += p.cost
			probabilities.append(round(p.protection * 100, 2))
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
		#Get the current income for the round
		payoff = self.player.payoff
		#if its the first round take off the starting funds otherwise it will display the income for round 1 incorrectly
		if(self.subsession.round_number == 1):
			payoff -= self.session.config['starting_funds']	
		#Now 'fix' the overall pledge protection values
		if(self.session.config['pledge'] == True):
			overall_pledge = round(overall_pledge * 100, 2)
		
		return {
			'results': zip(names, costs, probabilities, pledges, pledge_prob, name_true),
			'funds': currentFunds,
			'name': self.player.participant.vars['name'],
			'upkeep': c(upkeep),
			'revenue': c(revenue),
			'total_cost': self.player.cost + c(self.session.config['upkeep']),
			'monitoring' : self.session.config['monitoring'],
			'neg' : negative,
			'payoff' : abs(payoff),
			'overall' : round((1 - self.group.chance_of_incursion)*100, 2),
			'pledge' : self.session.config['pledge'],
			'total_protection' : total_protection,
			'total_pledge' : total_pledge,
			'overall_pledge' : overall_pledge,
			'group_target': self.participant.vars["Group_Targets_Prob"][1],
		}

#PLEDGING CLASSES BEGIN HERE
class PledgeWait(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.subsession.round_number % self.session.config["pledge_looper"] == 1
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
		return self.session.config['pledge'] == True and self.session.config['Papproval'] == True and self.subsession.round_number % self.session.config["pledge_looper"] == 1
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
		return self.session.config['pledge'] == True and self.subsession.round_number % self.session.config["pledge_looper"] == 1
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
			'pledge_loop' : self.session.config["pledge_looper"],
		}

class IndiPledgingWait(WaitPage):
	def after_all_players_arrive(self):
		for p in self.group.get_players():
			#Adjust the Most Recent Pledge by each player accordingly
			p.participant.vars["Recent_Pledge"][0] = p.participant.vars["Recent_Pledge"][1]
			#Index 1 is the most recent pledge
			p.participant.vars["Recent_Pledge"][1] = p.individualPledge
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.subsession.round_number % self.session.config["pledge_looper"] == 1
		
class GroupPledging(Page):
	"""
	The GroupPledging class does the logic for the Group Pledging Page
	"""
	timeout_seconds = 60
	form_model = models.Player
	form_fields = ['groupTarget']
	#On timeout simply chooses the minimum group target.
	def before_next_page(self):
		if self.timeout_happened:
			self.player.groupTarget = 40
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.subsession.round_number % self.session.config["pledge_looper"] == 1
	def vars_for_template(self):
		return {
			'player_name' : self.player.participant.vars["name"],
			'pledge_loop' : self.session.config["pledge_looper"],
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
		return self.session.config['pledge'] == True and self.session.config['Papproval'] == True and self.subsession.round_number % self.session.config["pledge_looper"] == 1
	def vars_for_template(self):
		names = []
		ids = []
		pledge_results = []
		pledge_prob = []
		#Allows us to highlight player's name in a table
		name_true = []
		#Calculate the cost factor
		cost_factor = self.session.config['max_protection']/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
		#Get the names, ids and individual pledges of each player and store them in the respective lists above
		for p in self.group.get_players():
			names.append(p.participant.vars['name'])
			if p.participant.vars["name"] == self.player.participant.vars["name"]:
				name_true.append(True)
			else:
				name_true.append(False)
			#Uses the ids for the automatic naming of the forms.
			ids.append(p.id_in_group)
			pledge_results.append(p.participant.vars["Recent_Pledge"][1])
			probability = 1-math.exp(-p.participant.vars["Recent_Pledge"][1]/cost_factor) + self.session.config["probability_coefficient"]
			pledge_prob.append(round(probability * 100, 2))
		#Zip the 3 lists together so you have {(Player 1 Name, 1, Player 1 Pledge), (Player 2 Name, 2, Player 2 Pledge), ...,(Player n Name, n, Player n Pledge)}
		return {
			'list' : zip(ids, names, pledge_results, pledge_prob, name_true),
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
		#Allows us to highlight player's name in a table
		name_true = []
		for p in self.group.get_players():
			names.append(p.participant.vars['name'])
			if p.participant.vars["name"] == self.player.participant.vars["name"]:
				name_true.append(True)
			else:
				name_true.append(False)
			ids.append(p.id_in_group)
			'''
			If Pledge looper and contribution are the same, then grab the most recent pledge as its 
			most likely the approval stage will occur before next pledge. If the Pledge Looper is more
			than the Contribution looper, then it will take the previous pledge rather than the most recent.
			If Pledge looper is less, then it will take the most recent.
			'''
			if self.session.config["contribution_looper"] >= self.session.config["pledge_looper"]:
				pledge_results.append(p.participant.vars["Recent_Pledge"][1])
				gtp = self.participant.vars["Group_Targets_Prob"][1]
			elif(self.session.config["contribution_looper"] < self.session.config["pledge_looper"]):
				pledge_results.append(p.participant.vars["Recent_Pledge"][0])
				gtp = self.participant.vars["Group_Targets_Prob"][1]
			#Get the participants contributions from the last contribution_looper rounds
			results.append(p.participant.vars["Protection_Provided"])
		#Get the round numbers for the display	
		for i in range(self.subsession.round_number - self.session.config["contribution_looper"] + 1, self.subsession.round_number + 1):
			round_numbers.append(i)
		return {
			'list_for_table' : zip(names, ids, pledge_results, results, name_true),
			'round_numbers' : round_numbers,
			'Group_Target_Prob' : gtp,
			'player_name': self.player.participant.vars['name'],
			'contribution_looper' : self.session.config["contribution_looper"],
		}
		
class BioQuestions(BioInstructions):
	'''
		This is the Biosecurity Control Questions Page which puts questions in
		to see if participants understand the instructions, it will be very much
		like the lottery questions. In fact the models and views copies that code.
	'''
	# Display this page only once
	def is_displayed(self):
		return self.subsession.round_number == 1

	form_model = models.Player
	
	# create the pre lottery questions form fields
	def get_form_fields(self):
		return ['bio_question_{}'.format(i) for i in range(1, Constants.num_bio_questions + 1)]

class ApprovalReview(Page):
	'''
		This is the page where participants will review their approvals based 
		on their contributions before the next round takes place
	'''
	timeout_seconds = 60
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.session.config['Capproval'] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0
	def vars_for_template(self):
		#List of names
		names = []
		#The Pledge that was made over the last ["pledge_looper"] rounds
		pledge_results = []
		#This will be a list of lists of the protection provided from each player from the last ["pledge_looper"] rounds
		results = []
		#List of Round Numbers from Current Round to Current Round -  ["Pledge_Looper"]
		round_numbers = []
		#Allows us to highlight player's name in a table
		name_true = []
		#This holds the group approvals for players
		average = []
		#The below list will contain either black, red or green as a string for html styling.
		colours = []
		for p in self.group.get_players():
			names.append(p.participant.vars['name'])
			if p.participant.vars["name"] == self.player.participant.vars["name"]:
				name_true.append(True)
			else:
				name_true.append(False)
			'''
			If Pledge looper and contribution are the same, then grab the most recent pledge as its 
			most likely the approval stage will occur before next pledge. If the Pledge Looper is more
			than the Contribution looper, then it will take the previous pledge rather than the most recent.
			If Pledge looper is less, then it will take the most recent.
			'''
			if self.session.config["contribution_looper"] >= self.session.config["pledge_looper"]:
				pledge_results.append(p.participant.vars["Recent_Pledge"][1])
			elif(self.session.config["contribution_looper"] < self.session.config["pledge_looper"]):
				pledge_results.append(p.participant.vars["Recent_Pledge"][0])
			#Get the participants contributions from the last contribution_looper rounds
			results.append(p.participant.vars["Protection_Provided"])
			#Copies the method for getting the averages from the round page
			average.append(self.group.get_player_by_id(1).participant.vars["approval_means"][p.id_in_group - 1])
			average[-1] = int(round(average[-1], 0))
			if average[-1] > 0:
				colours.append("green")
			elif average[-1] < 0:
				colours.append("red")
			else:
				colours.append("black")
		#Get the round numbers for display
		for i in range(self.subsession.round_number - self.session.config["contribution_looper"] + 1, self.subsession.round_number + 1):
			round_numbers.append(i)
		
		return {
				'list_for_table' : zip(names, pledge_results, results, average, colours, name_true),
				'round_numbers' : round_numbers,
				'player_name': self.player.participant.vars['name'],
				'contribution_looper' : self.session.config["contribution_looper"],
		}
		
class ApprovalReviewWait(WaitPage):
	def is_displayed(self):
		return self.session.config['pledge'] == True and self.session.config['Capproval'] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0
	def after_all_players_arrive(self):
		#Reset the protection provided list to then add the next contribution_looper rounds without any extra data to deal with.
		for p in self.group.get_players():
			p.participant.vars["Protection_Provided"] = []
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
	BioQuestions,
	WaitforInstructions,
	GroupPledging,
	PledgeWait,
	IndiPledging,
	IndiPledgingWait,
	PledgingApproval,
	AopWait,
	Chat,
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
	ApprovalReview,
	ApprovalReviewWait,
]


