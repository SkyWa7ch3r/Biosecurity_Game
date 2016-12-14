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
	
class Subsession(BaseSubsession):

	#Dynamic value arrays
	revenue = []
	upkeep = []
	maxProtection= []

	#At the start of this app
	def before_session_starts(self):
		#Get the group matching if its the actual game and not just the tests.
		self.session.vars['incursion_count'] = 0
		if self.round_number == 1 and self.session.config['name'] == 'biosecurity_game':
			self.set_group_matrix(self.session.vars['matrix'])
		cost = models.PositiveIntegerField()
		#array for player names
		names = []
		#If dynamic finacial values are active
		if(self.session.config['dynamic_finances'] == True):
			#read financial values from csv and store in arraylists
			with open('CSV/dynamic_finances.csv') as filestream:
				file = csv.DictReader(filestream)
				for row in file:
					self.revenue.append(float(row['revenue']))
					self.upkeep.append(float(row['upkeep']))
					self.maxProtection.append(float(row['protection']))

		#Read names from csv and store in array    
		with open('CSV/names.csv') as filestream:
			file = csv.DictReader(filestream)
			for row in file:
				names.append(row['Names'])
			been_before = [1000]
		#assign a random name to each player
		for p in self.get_players():
			num = 1000
			while num in been_before:
				num = random.randint(0,len(names) - 1)
			been_before.append(num)
			p.participant.vars['funds'] = self.session.config['starting_funds']
			p.participant.vars['name'] = names[num]

class Group(BaseGroup):

	#store incursion state
	incursion = models.NullBooleanField(False)
	incursion_count = models.IntegerField(blank = True, default = 0)
	#Median Data for every Pledging Stage and the group Target to see in the Results
	medians = []
	calculatedGroupTarget = models.FloatField(default = 0.0)

	#Group's averaged protection values
	total_protection = models.DecimalField(max_digits=4,decimal_places=2, default=0.00)
	#When the resusts page loads, this function finds net incoms of players
	def calculate_profits(self):
		if(self.session.config['player_communication']):
			#communication is enabled
			self.communication = True
		#Calucate the protection each player provides (0-0.99) representing a percentage (0 = 100% chance of incursion etc.)
		for p in self.get_players():
				p.protection = p.calculate_protection()
		#Sum and average the protection probabillities of all players within this group
		self.total_protection = sum([p.protection for p in self.get_players()])
		#Calculate the outbreak using Psuedo-random number generator (seeded with system clock)
		if(random.random()>self.total_protection/len(self.get_players())):
			#An incursion occured
			self.incursion = True
			self.session.vars['incursion_count'] +=1
			#Set updated funds for all players
			for p in self.get_players():
			  
				if(self.session.config['dynamic_finances'] == False):
				#static finacial value
					p.payoff = - p.cost - c(self.session.config['upkeep'])
				#dynamic finacial values  
				else:
					p.payoff = - p.cost - c(self.subsession.upkeep[self.subsession.round_number-1]) 
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
					p.payoff = c(self.subsession.revenue[self.subsession.round_number-1]) - c(self.subsession.upkeep[self.subsession.round_number-1]) - p.cost
				#Set funds of player as value calculated above
				p.participant.vars['funds'] += p.payoff
				p.funds_at_rounds_end  = p.participant.vars['funds']
				if self.subsession.round_number == 1:
					p.payoff += self.session.config['starting_funds']
		self.incursion_count = self.session.vars['incursion_count']
		
	def calculate_group_target(self):
		targets = []
		#Grab all the group targets as set by the players in the Group Target Stage
		for p in self.get_players():
			targets.append(p.groupTarget)
		#Use the python sort function
		targets.sort()
		#Put the median as calculatedGroupTarget and add it to the medians list
		self.calculatedGroupTarget = median(targets)
		self.medians.append(median(targets))
		
class Player(BasePlayer):
	funds_at_rounds_end = otree.models.CurrencyField(default = 0)
	protection = otree.models.DecimalField(max_digits = 2, decimal_places = 2)
	groupTarget = otree.models.IntegerField(widget=otree.widgets.SliderInput(attrs={'step' : '1'}))
	individualPledge = otree.models.CurrencyField(widget=otree.widgets.SliderInput(attrs={'step' : '0.01'}))
	cost = otree.models.CurrencyField(verbose_name="How Much protection do you want to do against Biosecurity Threats?", widget=otree.widgets.SliderInput(attrs={'step': '0.01'}))
	papproval = otree.models.IntegerField(choices=[
        [-6, 'Strongly Disapprove (-6)'],
        [-5, '-5'],
        [-4, '-4'],
		[-3, '-3'],
		[-2, '-2'],
		[-1, '-1'],
		[0, 'Neutral (0)'],
		[1, '1'],
		[2, '2'],
		[3, '3'],
		[4, '4'],
		[5, '5'],
		[6, 'Strongly approve (6)'],
    ])
	#find protection value using cost entered by player and max_protection which is set my an admin
	def calculate_protection(self):
		#If the finance variables are static, assign cost_factor statically, otherwise assign value appropriate for the round from the dynamic finance array
		if(self.session.config['dynamic_finances'] == False):
			cost_factor = self.session.config['max_protection']/-math.log(0.01)
		else:
			cost_factor = self.subsession.maxProtection[self.subsession.round_number-1]/-math.log(0.01)

		#protection is defined as 1-e^(-cost/cost_factor)
		self.protection = 1-math.exp(-self.cost/cost_factor)
		return self.protection

	#If the lead_player feature is enabled, set the next player in order as the leader
	def role(self):
		if(self.session.config['set_leader']):
			if self.id_in_group == ((self.subsession.round_number-1)%self.session.config['players_per_group'])+1:
				return 'Leader'

