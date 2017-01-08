from otree.api import (
	models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
	Currency as c, currency_range, safe_json
)
from django.db import models
from decimal import Decimal
import otree
import math
import random
import csv
from statistics import median

author = 'UWA 2016 CITS3200 Group I: Joel Dunstan, Willem Meyer, Trae Shaw, Justin Chong'

"""
Changes made after 1/12/2016 were all made by Joel Dunstan as per the git logs
"""

doc = """
This is the Biosecurity Game models.py, in here are the methods for calculating the probability, cost and profit for each round in the Biosecurity
Game.

The Constants Class contains constant variables used with the Game.
players_per_group : one of the variables required to be defined in theis class. The number of players is set in the Lottery Game
num_rounds : rounds to be played
max_protection : the maximum amount, in in-game money, that can be spent on security. This value is equivilent to 99% protection. Increasing this value makes it more difficult for players to turn a profit . This value can be changed in sessions_config.csv. 10, the recommended value, represents the amount of money a player would have spent for protection in the original z-tree implementation of this experiment.
cost_factor : The constant in the probabillity calculation formula: p = 1-e^(cost/cost_factor)

Subsession initializes players with random names and set starting funds before the start of the session. The names are read from file.
If the admin has dsabled dynamic_finances then the values for revenue, upkeep and max_protection are set upon session creation. 
Otherwise, theses values are sourced from dynamic_finances.csv and passed into arrays, representing a different value for each round

Group is the collection of players playing the game together. It calcuates whether an incursion occurs and the resulting changes in player's finances

Player class contains individual variables for a given player
Protection : 3 decimal place value between 0 and 1. Represents 1-p where p is the probabillity of an outbreak occuring 
cost : the amount in in-game dollars the player has elected to spent on protection in a given round. The minimum is 0 and the max is set by an admin. The value is passed from a HTML slider widget
"""
class Constants(BaseConstants):

	players_per_group = None
	name_in_url = 'Biosecurity'
	num_rounds = 15
	
	#Define all the player decisions
	RATING = [
		[-6, 'Strongly Disapprove (-6)'],
		[-5, '-5'],
		[-4, '-4'],
		[-3, 'Disapprove (-3)'],
		[-2, '-2'],
		[-1, '-1'],
		[0, 'Neutral (0)'],
		[1, '1'],
		[2, '2'],
		[3, 'Approve (3)'],
		[4, '4'],
		[5, '5'],
		[6, 'Strongly approve (6)'],
	]
	
	#Dynamic value arrays
	revenue = []
	upkeep = []
	maxProtection= []
	with open('CSV/dynamic_finances.csv') as filestream:
				file = csv.DictReader(filestream)
				for row in file:
					revenue.append(float(row['revenue']))
					upkeep.append(float(row['upkeep']))
					maxProtection.append(float(row['protection']))

	
class Subsession(BaseSubsession):
	
	#At the start of this app
	def before_session_starts(self):
		#Start the incursion counter
		self.session.vars['incursion_count'] = 0
		#Get the group matching if its the actual game and not just the tests.
		if "game" in self.session.config['name']:
			self.set_group_matrix(self.session.vars['matrix'])
		cost = models.PositiveIntegerField()
		#array for player names
		names = []
		for g in self.get_groups():
			#Start the pledge counter, displays how many rounds till next pledge
			g.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] = self.session.config["pledge_looper"]
			#Start the Contribution Counter, displays how many rounds till next Contribution Approval
			g.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] = self.session.config["contribution_looper"] - 1
			#Start the incursion counter
			g.get_player_by_id(1).participant.vars['incursion_count'] = 0
			#Have a boolean so the game knows its a pledging round
			g.get_player_by_id(1).participant.vars['pledge_round'] = False
		#Read names from csv and store in array    
		with open('CSV/names.csv') as filestream:
			file = csv.DictReader(filestream)
			for row in file:
				names.append(row['Names'])
			been_before = [1000]
		namesChosen = []
		for p in self.get_players():
			num = 1000
			#No generate random numbers until we get an index that hasnt been chosen before
			while num in been_before:
				num = random.randint(0,len(names) - 1)
			#Record this number so no one else ghets the name
			been_before.append(num)
			#Apply starting funds
			p.participant.vars['funds'] = self.session.config['starting_funds']
			#Apply the name via the index chosen by num
			p.participant.vars['name'] = names[num]
			namesChosen.append(names[num])
			#Define All the Participant Variables needed for the session, even if they're not used.
			p.participant.vars["approval_means"] = [0.00] * 20
			# Recent_Pledge[1] =  Current Pledge, Recent_Pledge[0] = Previous Pledge
			p.participant.vars["Recent_Pledge"] = [0,0]
			# Group_Targets[1] =  Current Group Target, Group_Targets[0] = Previous Group Target
			p.participant.vars["Group_Targets_Prob"] = [0, 0]
			p.participant.vars["Group_Targets_Cost"] = [0, 0]
			#For Approval By Contribution may come in handy later, a list for costs done by every player per ["pledge_looper"] rounds
			p.participant.vars["Protection_Provided"] = []
		for _ in range(21 - self.session.config['players_per_group']):
			namesChosen.append(None)
		for p in self.get_players():
			p.name_1 = namesChosen[0]
			p.name_2 = namesChosen[1]
			p.name_3 = namesChosen[2]
			p.name_4 = namesChosen[3]
			p.name_5 = namesChosen[4]
			p.name_6 = namesChosen[5]
			p.name_7 = namesChosen[6]
			p.name_8 = namesChosen[7]
			p.name_9 = namesChosen[8]
			p.name_10 = namesChosen[9]
			p.name_11 = namesChosen[10]
			p.name_12 = namesChosen[11]
			p.name_13 = namesChosen[12]
			p.name_14 = namesChosen[13]
			p.name_15 = namesChosen[14]
			p.name_16 = namesChosen[15]
			p.name_17 = namesChosen[16]
			p.name_18 = namesChosen[17]
			p.name_19 = namesChosen[18]
			p.name_20 = namesChosen[19]	
			
class Group(BaseGroup):

	#store incursion state
	incursion = models.NullBooleanField(False)
	incursion_count = models.IntegerField(blank = True, default = 0)
	
	#Median Data for every Pledging Stage and the group Target to see in the Results
	GroupTargetProbability = models.FloatField(default= 0.0)
	GroupTargetCost = models.FloatField(default= 0.0)
	
	#Group's averaged protection values
	chance_of_incursion = models.DecimalField(max_digits=4,decimal_places=2, default=0.00)
	#When the resusts page loads, this function finds net incoms of players
	def calculate_profits(self):
		if(self.session.config['player_communication']):
			#communication is enabled
			self.communication = True
		#Calucate the protection each player provides (0-0.99) representing a percentage (0 = 100% chance of incursion etc.)
		for p in self.get_players():
				p.participant.vars["Protection_Provided"].append(Decimal(p.cost))
				p.protection = p.calculate_protection()
		#Work out the joint probability of the entire group, where the multiplication of everyone's probability is the chance of no incursion for the group
		jointprob = 1
		for p in self.get_players():
			jointprob = jointprob * p.protection
		#1 - the chance of no incursion for the group = the chance of incursion
		self.chance_of_incursion = 1 - jointprob
		#Calculate the outbreak using Psuedo-random number generator (seeded with system clock), if the number is lower the chance_of_incursion then there is an incursion
		if(random.random()<self.chance_of_incursion):
			#An incursion occured
			self.incursion = True
			self.get_player_by_id(1).participant.vars['incursion_count'] +=1
			#Set updated funds for all players
			for p in self.get_players():
			  
				if(self.session.config['dynamic_finances'] == False):
				#static finacial value
					p.payoff = - p.cost - c(self.session.config['upkeep'])
				#dynamic finacial values  
				else:
					p.payoff = - p.cost - c(Constants.upkeep[self.subsession.round_number-1]) 
				p.participant.vars['funds'] += p.payoff
				p.funds_at_rounds_end  = p.participant.vars['funds']
				if self.subsession.round_number == 1:
					p.payoff += self.session.config['starting_funds']
		   
		else:
			#An incursion did not occur
			#self.incursion = False
			#Set updated funds for all players
			for p in self.get_players():
				if(self.session.config['dynamic_finances'] == False):
					#static finacial values
					p.payoff = c(self.session.config['revenue']) - c(self.session.config['upkeep']) - p.cost
				else:
					#dynamic finacial values
					p.payoff = c(Constants.revenue[self.subsession.round_number-1]) - c(Constants.upkeep[self.subsession.round_number-1]) - p.cost
				#Set funds of player as value calculated above
				p.participant.vars['funds'] += p.payoff
				p.funds_at_rounds_end  = p.participant.vars['funds']
				if self.subsession.round_number == 1:
					p.payoff += self.session.config['starting_funds']
		self.incursion_count = self.get_player_by_id(1).participant.vars['incursion_count']
		
	def calculate_group_target(self):
		targets = []
		#Grab all the group targets as set by the players in the Group Target Stage
		for p in self.get_players():
			targets.append(p.groupTarget)
		#Use the python sort function
		targets.sort()
		#Get the median
		self.GroupTargetProbability = median(targets)
		#Get The Cost_Factor
		cost_factor = self.session.config['max_protection']/-math.log(0.01)
		#Get the Group Target cost as an inverse of Player.calculate_protection
		if(self.GroupTargetProbability == 100):
			self.GroupTargetCost = self.session.config["max_protection"]
		else:
			self.GroupTargetCost = round(-cost_factor*math.log(1 - self.GroupTargetProbability/100), 2)
		if(self.GroupTargetCost == -0.0):
			self.GroupTargetCost = self.GroupTargetCost * -1.0
		#Go Through and change the Group Targets to reflect the changes.
		for p in self.get_players():
			p.participant.vars["Group_Targets_Prob"][0] = p.participant.vars["Group_Targets_Prob"][1]
			p.participant.vars["Group_Targets_Cost"][0] = p.participant.vars["Group_Targets_Cost"][1]
			p.participant.vars["Group_Targets_Prob"][1] = self.GroupTargetProbability
			p.participant.vars["Group_Targets_Cost"][1] = self.GroupTargetCost
	
	def calculate_mean_approval(self):
		"""
		This is going to be messy due to the constraints of oTree and Django, since we are not
		able to do a ListField or DictionaryField and can't dynamically assign approval fields
		we are stuck with the loop below which just goes from 0 to number of players_per_group, and then based
		on the current iteration number i, do the average of approval_i from each player and store the value
		in approval_means. In an ideal world I'd be able to do this loop in about 5 lines but well that's life.
		"""
		#Mean Approval List for the Group to store everyone's average approval rating per player, approval_means[n - 1] = average of the approval_n in each player, approval_n = approval of name_n or Player n.
		approval_means = [0.00] * 21
		for i in range(0, self.session.config["players_per_group"]):
			if(i is 0):
				approval_total = 0
				#For each player get approval_1
				for p in self.get_players():
					approval_total = approval_total + p.approval_1
				#Get the average approval for Player 1
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 1):
				
				approval_total = 0
				#For each player get approval_2
				for p in self.get_players():
					approval_total += p.approval_2
				#Get the average approval for Player 2
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 2):
				
				approval_total = 0
				#For each player get approval_3
				for p in self.get_players():
					approval_total += p.approval_3
				#Get the average approval for Player 3
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 3):
				
				approval_total = 0
				#For each player get approval_4
				for p in self.get_players():
					approval_total += p.approval_4
				#Get the average approval for Player 4
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 4):
				
				approval_total = 0
				#For each player get approval_5
				for p in self.get_players():
					approval_total += p.approval_5
				#Get the average approval for Player 5
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 5):
				
				approval_total = 0
				#For each player get approval_6
				for p in self.get_players():
					approval_total += p.approval_6
				#Get the average approval for Player 6
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]	
			elif(i is 6):
				
				approval_total = 0
				#For each player get approval_7
				for p in self.get_players():
					approval_total += p.approval_7
				#Get the average approval for Player 7
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 7):
				
				approval_total = 0
				#For each player get approval_8
				for p in self.get_players():
					approval_total += p.approval_8
				#Get the average approval for Player 8
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 8):
				
				approval_total = 0
				#For each player get approval_9
				for p in self.get_players():
					approval_total += p.approval_9
				#Get the average approval for Player 9
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 9):
				
				approval_total = 0
				#For each player get approval_10
				for p in self.get_players():
					approval_total += p.approval_10
				#Get the average approval for Player 10
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 10):
				
				approval_total = 0
				#For each player get approval_11
				for p in self.get_players():
					approval_total += p.approval_11
				#Get the average approval for Player 11
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 11):
				
				approval_total = 0
				#For each player get approval_12
				for p in self.get_players():
					approval_total += p.approval_12
				#Get the average approval for Player 12
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 12):
				
				approval_total = 0
				#For each player get approval_13
				for p in self.get_players():
					approval_total += p.approval_13
				#Get the average approval for Player 13
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 13):
				
				approval_total = 0
				#For each player get approval_14
				for p in self.get_players():
					approval_total += p.approval_14
				#Get the average approval for Player 14
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 14):
				
				approval_total = 0
				#For each player get approval_15
				for p in self.get_players():
					approval_total += p.approval_15
				#Get the average approval for Player 15
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 15):
				
				approval_total = 0
				#For each player get approval_16
				for p in self.get_players():
					approval_total += p.approval_16
				#Get the average approval for Player 16
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 16):
				
				approval_total = 0
				#For each player get approval_17
				for p in self.get_players():
					approval_total += p.approval_17
				#Get the average approval for Player 17
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 17):
				
				approval_total = 0
				#For each player get approval_18
				for p in self.get_players():
					approval_total += p.approval_18
				#Get the average approval for Player 18
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 18):
				
				approval_total = 0
				#For each player get approval_19
				for p in self.get_players():
					approval_total += p.approval_19
				#Get the average approval for Player 19
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
			elif(i is 19):
				
				approval_total = 0
				#For each player get approval_20
				for p in self.get_players():
					approval_total += p.approval_20
				#Get the average approval for Player 20
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
		for p in self.get_players():
			p.participant.vars["approval_means"] = list(approval_means)
			'''
			Since the list won't matter in the Approval based on Pledging, only in Approval by Contribution
			we'll reset every list here of Protection_Provided to make sure in ActionApproval that no overlap takes place
			'''
			p.participant.vars["Protection_Provided"] = []
class Player(BasePlayer):
	funds_at_rounds_end = otree.models.CurrencyField(default = 0)
	protection = otree.models.DecimalField(max_digits = 3, decimal_places = 2)
	groupTarget = otree.models.IntegerField(widget=otree.widgets.SliderInput(attrs={'step' : '1'}))
	individualPledge = otree.models.CurrencyField(widget=otree.widgets.SliderInput(attrs={'step' : '0.01'}))
	cost = otree.models.CurrencyField(widget=otree.widgets.SliderInput(attrs={'step': '0.01'}))
	
	
	#All the names to put alongside the approval, n corresponds to n, e.g. name_1 corresponds to approval_1 
	name_1 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_2 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_3 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_4 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_5 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_6 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_7 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_8 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_9 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_10 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_11 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_12 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_13 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_14 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_15 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_16 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_17 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_18 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_19 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	name_20 = otree.models.CharField(default=None, widget=otree.widgets.HiddenInput(), verbose_name='')
	
	#Number of Approvals, this will indicate a maximum amount of players per group
	approval_1 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_2 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_3 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_4 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_5 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_6 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_7 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_8 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_9 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_10 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_11 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_12 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_13 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_14 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_15 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_16 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_17 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_18 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_19 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	approval_20 = otree.models.IntegerField(default=0, choices=Constants.RATING, verbose_name='')
	
	#find protection value using cost entered by player and max_protection which is set my an admin
	def calculate_protection(self):
		#If the finance variables are static, assign cost_factor statically, otherwise assign value appropriate for the round from the dynamic finance array
		if(self.session.config['dynamic_finances'] == False):
			cost_factor = self.session.config['max_protection']/-math.log(0.01)
		else:
			cost_factor = Constants.maxProtection[self.subsession.round_number-1]/-math.log(0.01)

		#protection is defined as 1-e^(-cost/cost_factor)
		#cost is defined with -cost_factor*ln(1-cost)
		self.protection = 1-math.exp(-self.cost/cost_factor)
		return self.protection

	#If the lead_player feature is enabled, set the next player in order as the leader
	def role(self):
		if(self.session.config['set_leader']):
			if self.id_in_group == ((self.subsession.round_number-1)%self.session.config['players_per_group'])+1:
				return 'Leader'
				