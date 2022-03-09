from otree.api import (
	models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
	Currency as c, currency_range, safe_json
)
from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal
import otree
import math
import random
import csv
from statistics import median
from otree import widgets
author = 'UWA 2016 CITS3200 Group I: Joel Dunstan, Willem Meyer, Trae Shaw, Justin Chong'

"""
Changes made after 1/12/2016 were all made by Joel Dunstan as per the git logs
"""

doc = '''
This is the Biosecurity Game in which participants have 15 rounds of play. Each round participants must decide
their biosecurity effort against biosecurity threats, the round may also include pledging the amount of effort they wish
to contribute, showing their approval of other participant's efforts or pledges. The default is 4 players per group, anymore than this
will increase the difficulty of the game due to joint probability. Please refer to the Administration Instructions and the Test Documentation
for more information on adjusting variables, and how an outbreak is calculated.
'''

"""
This is the Biosecurity Game models.py, in here are the methods for calculating the probability, cost and profit for each round in the Biosecurity
Game.

The Constants Class contains constant variables used with the Game.
players_per_group : Set as None, here grouping is done in subsession.
num_rounds : The Number of Rounds to be played

The Subsession class is used at the start of each round, and the start of a session. Here grouping is done for testing environments for the biosecurity
game. The Subsession class has many others tasks too such as assigning each participant's anonymous names and storing them for the game to store and use
in the data later. Many of the participant variables used throughout the games for pledging and the like are also initialized here for later use. Thus no
variables are really declared here.

The Group class is responsible for all functions that apply to the entire group, where the group is a subset of participants from the session who are playing,
you can have multiple groups per session, anything that should be done to all participants in a session should be done inside the Subsession class.
It is here where we store values such as:
incursion - Is True if there was an incursion/outbreak
incursion_count - The number of outbreaks so far.
GroupTargetProbability - The groups pledge/target for the next 'pledge_looper' rounds
chance_of_incursion - This is the chance of an outbreak this round as calculated and determined by the groups actions
contribution - Is True when there is an approval by contribution taking place that round
pledge - Is True when there is a pledge for the next 'pledge_looper' rounds from participants taking place that round
In the Group Class we also calculate the group target from players in that group which is the median of what everyone thinks
the group target should be. The average approval of player's is also done here, whether those approval is on pledges or contributions.

The Player Class is responsible for handling all the functions and variables associated with each player is a game.
Its here I will draw a distinction between player and participant, a participant is an instance in the context of a session, a player belongs to a group
which a group is a subset of all the participants in a session. In essence, yes a participant is a player, however is depends on the context as to which
word you use. Within a group, use the word Player, within a session use the word participant, if you're not sure use the word participant.
funds_at_rounds_end - The amount of funds a player has at the end of the round.
protection - The amount of biosecurity effort from a player that round in the form of probability that they're not the source of the outbreak.
groupTarget - This is target the player thinks the group should aspire to when pledging is activated.
individualPledge - The individual pledge from a player that they wish to pledge for the next 'pledge_looper' rounds
cost - The amount of biosecurity effort in the form of cost in monetary value.
Group_Approval - The groups approval of that players contribution/pledge.
name_1-20 - The names of every player in the group, storing for the excel spreadsheets
approval_1-20 - The same as names_1-20 except it storing approvals
In this class we do the conversion between cost -> protection and we also get the biosecurity questions here too.

Some of the functions for the Biosecurity quiz were obtained from the lottery quiz, and thus have the same names.
"""

#check_correct is used for validating that the user selected the correct answer for the pre lottery quiz
def check_correct(correct_value):
	def compare(selected_value):
		if not (correct_value == selected_value):
			raise ValidationError('Incorrect')

	return compare

class Constants(BaseConstants):

	players_per_group = None
	name_in_url = 'Biosecurity'
	num_rounds = 15
	
	#Define all the player decisions for approval, No longer used, HTML drop down is responsible for passing through the values
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
	
	#Retrieve the Biosecurity Control Questions
	with open('CSV/bio_questions.csv') as f:
		bio_questions = list(csv.DictReader(f))
		
	#Store how many questions there are
	num_bio_questions = len(bio_questions)
	
	#Do the values for the Cost and Probability Calculations
	max_probability = 0.9999
	
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
		#Do the group matching for the tests
		else:
			# GROUP LOGIC STARTS HERE
			# ppg = player_per_group
			ppg = self.session.config['players_per_group']
			# list_of_groups is the the list of each group list e.g. [ [p1, p2], [p3, p4] ] if ppg == 2 and np == 4
			list_of_groups = []
			# The list of players is list of all the player ID's in the session
			list_of_players = []
			for p in self.get_players():
				list_of_players.append(p)
			# np = number of players
			np = len(list_of_players)
			i = 0
			while i < np:
				# get a list of the players going from the ith index to i + ppg - 1 and add that to the list of the groups
				list_of_groups.append(list_of_players[i: i + ppg])
				# iterate the i
				i = i + ppg
			num_groups = len(list_of_groups)
			# If the number of players is not a multiple of player per group
			if np % ppg != 0:
				# iterate through the list of groups
				for i in range(num_groups):
					# if the last group is full, do not continue
					if len(list_of_groups[-1]) == ppg:
						break
					# Get the player to remove
					player = list_of_groups[i][-1]
					# remove the player
					del list_of_groups[i][-1]
					# add the player to the last group
					list_of_groups[-1].append(player)
			# finalise the group matchings ready for game and store the matrix
			self.set_group_matrix(list_of_groups)
			#GROUP LOGIC ENDS HERE
		if(self.round_number == 1):
			names = []
			#Read names from csv and store in array	   
			with open('CSV/names.csv') as filestream:
				file = csv.DictReader(filestream)
				for row in file:
					names.append(row['Names'])
					
			for g in self.get_groups():
				#Start the pledge counter, displays how many rounds till next pledge
				g.get_player_by_id(1).participant.vars["Rounds_Till_Pledge"] = self.session.config["pledge_looper"]
				#Start the Contribution Counter, displays how many rounds till next Contribution Approval
				g.get_player_by_id(1).participant.vars["Rounds_Till_Contribution"] = self.session.config["contribution_looper"] - 1
				#Start the incursion counter
				g.get_player_by_id(1).participant.vars['incursion_count'] = 0
				#Have a boolean so the game knows its a pledging round
				g.get_player_by_id(1).participant.vars['pledge_round'] = False
				#Define All the Participant Variables needed for the group, even if they're not used.
				g.get_player_by_id(1).participant.vars["approval_means"] = [0.00] * 20
			
				#Generate random numbers until we get an index that hasn't been chosen before
				been_before = [1000]
				namesChosen = []
				#For every player inside this group...
				for p in g.get_players():
					#Start the random number process at 1000 to start the loop below
					num = 1000
					while num in been_before:
						num = random.randint(0,len(names) - 1)
					#Record this number so no one else gets the name inside the group
					been_before.append(num)
					#Apply the name via the index chosen by num
					p.participant.vars['name'] = names[num]
					#record the name as chosen in names chosen so we can apply this to the name_x in the player class
					namesChosen.append(names[num])
					
					#Start each player with the required funds and participant variables.
					#Apply starting funds
					p.participant.vars['funds'] = self.session.config['starting_funds']
					# Recent_Pledge[1] =  Current Pledge, Recent_Pledge[0] = Previous Pledge
					p.participant.vars["Recent_Pledge"] = [0,0]
					# Group_Targets[1] =  Current Group Target, Group_Targets[0] = Previous Group Target
					p.participant.vars["Group_Targets_Prob"] = [0, 0]
					#For Approval By Contribution may come in handy later, a list for costs done by every player per ["pledge_looper"] rounds
					p.participant.vars["Protection_Provided"] = []
				
				#Add the required amount to namesChosen to fill name_1 to name_20
				for _ in range(21):
					namesChosen.append(None)
				#Apply the names chosen from name_1 to name_20 while storing the list as a participant variable so we can keep recording the name throughout the game.
				for p in g.get_players():
					p.participant.vars['namesChosen'] = list(namesChosen)
					p.name_1 = p.participant.vars['namesChosen'][0]
					p.name_2 = p.participant.vars['namesChosen'][1]
					p.name_3 = p.participant.vars['namesChosen'][2]
					p.name_4 = p.participant.vars['namesChosen'][3]
					p.name_5 = p.participant.vars['namesChosen'][4]
					p.name_6 = p.participant.vars['namesChosen'][5]
					p.name_7 = p.participant.vars['namesChosen'][6]
					p.name_8 = p.participant.vars['namesChosen'][7]
					p.name_9 = p.participant.vars['namesChosen'][8]
					p.name_10 = p.participant.vars['namesChosen'][9]
					p.name_11 = p.participant.vars['namesChosen'][10]
					p.name_12 = p.participant.vars['namesChosen'][11]
					p.name_13 = p.participant.vars['namesChosen'][12]
					p.name_14 = p.participant.vars['namesChosen'][13]
					p.name_15 = p.participant.vars['namesChosen'][14]
					p.name_16 = p.participant.vars['namesChosen'][15]
					p.name_17 = p.participant.vars['namesChosen'][16]
					p.name_18 = p.participant.vars['namesChosen'][17]
					p.name_19 = p.participant.vars['namesChosen'][18]
					p.name_20 = p.participant.vars['namesChosen'][19]
					
		#This will ensure that every round (other than round 1 which does the above) the game continues to record the name.
		#Really wish you could loop over variables in oTree or Django, like you can with the forms. If you could this could be
		#reduced down to 3-4 lines.
		else:
			for p in self.get_players():
				p.name_1 = p.participant.vars['namesChosen'][0]
				p.name_2 = p.participant.vars['namesChosen'][1]
				p.name_3 = p.participant.vars['namesChosen'][2]
				p.name_4 = p.participant.vars['namesChosen'][3]
				p.name_5 = p.participant.vars['namesChosen'][4]
				p.name_6 = p.participant.vars['namesChosen'][5]
				p.name_7 = p.participant.vars['namesChosen'][6]
				p.name_8 = p.participant.vars['namesChosen'][7]
				p.name_9 = p.participant.vars['namesChosen'][8]
				p.name_10 = p.participant.vars['namesChosen'][9]
				p.name_11 = p.participant.vars['namesChosen'][10]
				p.name_12 = p.participant.vars['namesChosen'][11]
				p.name_13 = p.participant.vars['namesChosen'][12]
				p.name_14 = p.participant.vars['namesChosen'][13]
				p.name_15 = p.participant.vars['namesChosen'][14]
				p.name_16 = p.participant.vars['namesChosen'][15]
				p.name_17 = p.participant.vars['namesChosen'][16]
				p.name_18 = p.participant.vars['namesChosen'][17]
				p.name_19 = p.participant.vars['namesChosen'][18]
				p.name_20 = p.participant.vars['namesChosen'][19]
				
			
class Group(BaseGroup):

	#store incursion state
	incursion = models.NullBooleanField(False)
	incursion_count = models.IntegerField(blank = True, default = 0)
	
	#Median Data for every Pledging Stage and the group Target to see in the Results
	GroupTargetProbability = models.FloatField(default= 0.0)
	
	#Group's averaged protection values
	chance_of_incursion = models.DecimalField(max_digits=4,decimal_places=4, default=0.00)
	
	#Approval by contribution round, True when its a contribution round
	contribution = models.NullBooleanField(False)
	
	#Pledging Round, True when its a Pledging Round
	pledge = models.NullBooleanField(False)
	
	#When the resusts page loads, this function finds net incoms of players
	def calculate_profits(self):
		#Calculate the protection each player provides (0-0.99) representing a percentage (0 = 100% chance of incursion etc.)
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
		#Go Through and change the Group Targets to reflect the changes.
		for p in self.get_players():
			#Put the old target in the previous index
			p.participant.vars["Group_Targets_Prob"][0] = p.participant.vars["Group_Targets_Prob"][1]
			#Save the new target in the current index
			p.participant.vars["Group_Targets_Prob"][1] = self.GroupTargetProbability
	
	def calculate_mean_approval(self):
		"""
		This is going to be messy due to the constraints of oTree and Django, since we are not
		able to do a ListField or DictionaryField and can't dynamically assign approval fields
		we are stuck with the loop below which just goes from 0 to number of players_per_group, and then based
		on the current iteration number i, do the average of approval_i from each player and store the value
		in approval_means. In an ideal world I'd be able to do this loop in about 5 lines and have it much cleaner 
		but well that's life.
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
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 1):
				
				approval_total = 0
				#For each player get approval_2
				for p in self.get_players():
					approval_total += p.approval_2
				#Get the average approval for Player 2
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 2):
				
				approval_total = 0
				#For each player get approval_3
				for p in self.get_players():
					approval_total += p.approval_3
				#Get the average approval for Player 3
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 3):
				
				approval_total = 0
				#For each player get approval_4
				for p in self.get_players():
					approval_total += p.approval_4
				#Get the average approval for Player 4
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 4):
				
				approval_total = 0
				#For each player get approval_5
				for p in self.get_players():
					approval_total += p.approval_5
				#Get the average approval for Player 5
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 5):
				
				approval_total = 0
				#For each player get approval_6
				for p in self.get_players():
					approval_total += p.approval_6
				#Get the average approval for Player 6
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]				
			elif(i is 6):
				
				approval_total = 0
				#For each player get approval_7
				for p in self.get_players():
					approval_total += p.approval_7
				#Get the average approval for Player 7
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 7):
				
				approval_total = 0
				#For each player get approval_8
				for p in self.get_players():
					approval_total += p.approval_8
				#Get the average approval for Player 8
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 8):
				
				approval_total = 0
				#For each player get approval_9
				for p in self.get_players():
					approval_total += p.approval_9
				#Get the average approval for Player 9
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 9):
				
				approval_total = 0
				#For each player get approval_10
				for p in self.get_players():
					approval_total += p.approval_10
				#Get the average approval for Player 10
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 10):
				
				approval_total = 0
				#For each player get approval_11
				for p in self.get_players():
					approval_total += p.approval_11
				#Get the average approval for Player 11
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 11):
				
				approval_total = 0
				#For each player get approval_12
				for p in self.get_players():
					approval_total += p.approval_12
				#Get the average approval for Player 12
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 12):
				
				approval_total = 0
				#For each player get approval_13
				for p in self.get_players():
					approval_total += p.approval_13
				#Get the average approval for Player 13
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 13):
				
				approval_total = 0
				#For each player get approval_14
				for p in self.get_players():
					approval_total += p.approval_14
				#Get the average approval for Player 14
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 14):
				
				approval_total = 0
				#For each player get approval_15
				for p in self.get_players():
					approval_total += p.approval_15
				#Get the average approval for Player 15
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 15):
				
				approval_total = 0
				#For each player get approval_16
				for p in self.get_players():
					approval_total += p.approval_16
				#Get the average approval for Player 16
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 16):
				
				approval_total = 0
				#For each player get approval_17
				for p in self.get_players():
					approval_total += p.approval_17
				#Get the average approval for Player 17
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 17):
				
				approval_total = 0
				#For each player get approval_18
				for p in self.get_players():
					approval_total += p.approval_18
				#Get the average approval for Player 18
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 18):
				
				approval_total = 0
				#For each player get approval_19
				for p in self.get_players():
					approval_total += p.approval_19
				#Get the average approval for Player 19
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
			elif(i is 19):
				
				approval_total = 0
				#For each player get approval_20
				for p in self.get_players():
					approval_total += p.approval_20
				#Get the average approval for Player 20
				approval_means[i] = float(approval_total)/self.session.config["players_per_group"]
				self.get_player_by_id(i + 1).Group_Approval = approval_means[i]
		#Save the List of Approval Means
		self.get_player_by_id(1).participant.vars["approval_means"] = list(approval_means)
	
	
				
class Player(BasePlayer):
	#Save the values to store for the excel or CSV data, names a re self explanatory
	funds_at_rounds_end = otree.models.CurrencyField(default = 0)
	protection = otree.models.DecimalField(max_digits = 5, decimal_places = 4)
	groupTarget = otree.models.IntegerField(widget=otree.widgets.SliderInput(attrs={'step' : '1'}))
	individualPledge = otree.models.CurrencyField(widget=otree.widgets.SliderInput(attrs={'step' : '0.01'}))
	cost = otree.models.CurrencyField(widget=otree.widgets.SliderInput(attrs={'step': '0.01'}))
	Group_Approval = models.FloatField(default=0.0)
	
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
	
	
	# Read the Bio_Questions csv file and load the questions and answers for the form fields in the views.py, qn = question number (id in the csv)
	# read the pre-lottery question of the csv file
	def returnLotteryFormField(qn):
		matrix = []
		for num in range(1, int(Constants.bio_questions[qn]['#choices']) + 1):
			matrix.append(Constants.bio_questions[qn]['choice{}'.format(num)])
		return otree.models.CharField(choices=matrix, verbose_name=Constants.bio_questions[qn]['question'],
								widget=otree.widgets.RadioSelect(),
								validators=[check_correct(Constants.bio_questions[qn]['choice{}'.format(
									int(Constants.bio_questions[qn]['#correct']))])])
	# Add lottery questions here 
	bio_question_1 = returnLotteryFormField(0)
	bio_question_2 = returnLotteryFormField(1)
	bio_question_3 = returnLotteryFormField(2)
	bio_question_4 = returnLotteryFormField(3)
	
	#find protection value using cost entered by player and max_protection which is set my an admin
	def calculate_protection(self):
		#If the finance variables are static, assign cost_factor statically, otherwise assign value appropriate for the round from the dynamic finance array
		if(self.session.config['dynamic_finances'] == True):
			cost_factor = Constants.maxProtection[self.subsession.round_number-1]/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
		else:
			cost_factor = self.session.config['max_protection']/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
		#protection is defined as 1 + probability_coefficient -e^(-cost/cost_factor)
		#cost is defined with -cost_factor*ln(1-protection) - probability_coefficient
		self.protection = 1-math.exp(-self.cost/cost_factor) + self.session.config["probability_coefficient"]
		return self.protection

	#If the lead_player feature is enabled, set the next player in order as the leader
	def role(self):
		if(self.session.config['set_leader']):
			if self.id_in_group == ((self.subsession.round_number-1)%self.session.config['players_per_group'])+1:
				return 'Leader'
				