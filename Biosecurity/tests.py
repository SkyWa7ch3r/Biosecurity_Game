from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from .models import Constants
import random
import csv
import math
from statistics import median
from decimal import *
from otree.api import SubmissionMustFail
import otree

#Dynamic value arrays
revenue = []
upkeep = []
protection_array = []
with open('CSV/dynamic_finances.csv') as filestream:
	file = csv.DictReader(filestream)
	for row in file:
		revenue.append(float(row['revenue']))
		upkeep.append(float(row['upkeep']))
		protection_array.append(float(row['protection']))
'''
There is more details in the first random case, the rest of the cases follow the same format
just with changes to the cost and assert checks
'''
class PlayerBot(Bot):
	cases = ['random', 'quarter', 'half' , 'threequarters', 'full', 'half0halffull', 'bankrupt']
	
	def calculate_protection_for_test(self, max_protection, cost):
		#Convert to the currency format to ensure there are no precision errors
		cost_as_currency = c(cost)
		#Calculate the cost_factor, this allows for Dynamic Values for Max protection
		cost_factor = max_protection/-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
		#Return the calculated protection
		return round(Decimal(1 + self.session.config["probability_coefficient"] - math.exp(-cost_as_currency/cost_factor)), 4)
	
	def play_round(self):
		if self.session.config["controlling_the_cases_for_bots"]:
			self.case = self.session.config["case"]
		#Get the max participants 
		max_p = self.session.config['max_protection']
		#Calculate the minimum probability of a person not being the source of the incursion
		min_prob = int(self.session.config['probability_coefficient'] * 100)
		#Display the Instructions and the questions
		if self.subsession.round_number == 1:
			yield(views.BioInstructions)
			#Initialize the value lists
			correct_values = []
			wrong_values = []
			#Populate the correct_values list with the correct answers to the questions
			with open('CSV/bio_questions.csv') as f:
				values = csv.DictReader(f)
				#For every row in the csv file
				for row in values:
					#Just in case it tries to register an empty row, which it was in my testing
					if row['id'] != '':
						#Get the correct choice integer
						correct_choice = row['#correct']
						#Get the choice string
						cstring = 'choice%s' % correct_choice
						#Initialize wrong string
						wstring = ''
						#If the correct choice isnt 1
						if correct_choice != '1':
							#Load the first choice into the wrong value string
							wstring = 'choice1'
						#if the correct choice is number 1 then
						else:
							#Load the second choice into the wrong value string
							wstring = 'choice2'
						#Add the correct and wrong values
						correct_values.append(row[cstring])
						wrong_values.append(row[wstring])
			
			#Test for Bio Questions Failure, it checks for failures in order of question numbers 1,2,3,... In order for the test to continue these asserts MUST FAIL
			yield SubmissionMustFail(views.BioQuestions, {'bio_question_1': wrong_values[0], 'bio_question_2': correct_values[1], 'bio_question_3': correct_values[2],
										   'bio_question_4': correct_values[3]} )
			yield SubmissionMustFail(views.BioQuestions, {'bio_question_1': correct_values[0], 'bio_question_2': wrong_values[1], 'bio_question_3': correct_values[2],
										   'bio_question_4': correct_values[3]} )
			yield SubmissionMustFail(views.BioQuestions, {'bio_question_1': correct_values[0], 'bio_question_2': correct_values[1], 'bio_question_3': wrong_values[2],
										   'bio_question_4': correct_values[3]} )
			yield SubmissionMustFail(views.BioQuestions, {'bio_question_1': correct_values[0], 'bio_question_2': correct_values[1], 'bio_question_3': correct_values[2],
										   'bio_question_4': wrong_values[3]} )
										   
			#Had the following yield for when it had 5 questions, will leave in here for that possible eventuality
			#yield SubmissionMustFail(views.BioQuestions, {'bio_question_1': correct_values[0], 'bio_question_2': correct_values[1], 'bio_question_3': correct_values[2],
			#							   'bio_question_4': correct_values[3]} )
			
			#Try the correct options to see if it goes through to the next page
			yield(views.BioQuestions, {'bio_question_1': correct_values[0], 'bio_question_2': correct_values[1], 'bio_question_3': correct_values[2],
										   'bio_question_4': correct_values[3]} )
			
			if(self.player.id_in_group == 1):
				print("Beginning test for %s"%self.session.config["display_name"])
			
		#Check if the One Player Feature has been enabled, so one player goes before all the others
		if self.session.config['set_leader'] == False:

			#Test with random variable protection, protection equation is tested, incursion unpredictable
			if self.case == 'random':
				#Do the pledging pages if pledging is on
				if(self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 1 or self.subsession.round_number == 1)):
					#Start the Group Pledging, choses a random Target
					yield (views.GroupPledging, {'groupTarget' : random.randint(min_prob, 100)})
					#Work out the Group Target
					targets = []
					for p in self.group.get_players():
						targets.append(p.groupTarget)
					targets.sort()
					#Assert that the Group Target is indeed what it should be
					assert self.group.GroupTargetProbability == median(targets)
					#Does a random Individual Pledging, no assert tests associated with this its there for user benefit rather than for use by the program
					yield (views.IndiPledging, {'individualPledge' : round(random.uniform(0.0, max_p),2)})
					#If Approval of Pledges is on then do a random value between -6 and 6 as an integer
					if(self.session.config["Papproval"] == True):
						#We will check approval_1
						yield(views.PledgingApproval , {'approval_1' : random.randint(-6, 6), 
														'approval_2' : random.randint(-6, 6), 
														'approval_3' : random.randint(-6, 6), 
														'approval_4' : random.randint(-6, 6), 
														'approval_5' : random.randint(-6, 6), 
														'approval_6' : random.randint(-6, 6), 
														'approval_7' : random.randint(-6, 6), 
														'approval_8' : random.randint(-6, 6), 
														'approval_9' : random.randint(-6, 6), 
														'approval_10' : random.randint(-6, 6), 
														'approval_11' : random.randint(-6, 6), 
														'approval_12' : random.randint(-6, 6), 
														'approval_13' : random.randint(-6, 6), 
														'approval_14' : random.randint(-6, 6), 
														'approval_15' : random.randint(-6, 6), 
														'approval_16' : random.randint(-6, 6), 
														'approval_17' : random.randint(-6, 6), 
														'approval_18' : random.randint(-6, 6), 
														'approval_19' : random.randint(-6, 6), 
														'approval_20' : random.randint(-6, 6)})
						#Check the value of approval_1								
						approval_for_testing = 0.0
						approval_total = 0
						number_of_players = len(self.group.get_players())
						#Get the average approval of player 1
						for p in self.group.get_players():
							approval_total += p.approval_1
						approval_for_testing = approval_total/number_of_players
						#Assert that the value calculated here for the group approval of player 1 is indeed the approval of player 1
						assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == approval_for_testing
				
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
					
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#Assign random protection cost	  
				yield (views.Round, {'cost': round(random.uniform(0.0, max_p),2)})

				cost_for_test = self.player.cost
				#Goto the Results Page
				yield (views.Results)
				#Test the profit equation
				assert self.player.protection == self.calculate_protection_for_test(max_p, cost_for_test)

				#If there was an incursion
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				#If Approval on Contribution is on then choose a random value for approval of each player, just like approval by pledging we check the group approval of player 1
				if(self.session.config["Capproval"] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0):
					yield(views.ActionApproval , {'approval_1' : random.randint(-6, 6), 
												  'approval_2' : random.randint(-6, 6), 
												  'approval_3' : random.randint(-6, 6), 
												  'approval_4' : random.randint(-6, 6), 
												  'approval_5' : random.randint(-6, 6), 
												  'approval_6' : random.randint(-6, 6), 
												  'approval_7' : random.randint(-6, 6), 
												  'approval_8' : random.randint(-6, 6), 
												  'approval_9' : random.randint(-6, 6), 
												  'approval_10' : random.randint(-6, 6), 
												  'approval_11' : random.randint(-6, 6), 
												  'approval_12' : random.randint(-6, 6), 
												  'approval_13' : random.randint(-6, 6), 
												  'approval_14' : random.randint(-6, 6), 
												  'approval_15' : random.randint(-6, 6), 
												  'approval_16' : random.randint(-6, 6), 
												  'approval_17' : random.randint(-6, 6), 
												  'approval_18' : random.randint(-6, 6), 
												  'approval_19' : random.randint(-6, 6), 
												  'approval_20' : random.randint(-6, 6)})
					#Check the value of approval_1								
					approval_for_testing = 0.0
					approval_total = 0
					number_of_players = len(self.group.get_players())
					#Get the average approval of player 1
					for p in self.group.get_players():
						approval_total += p.approval_1
					approval_for_testing = approval_total/number_of_players
					#Assert that the value calculated here for the group approval of player 1 is indeed the approval of player 1
					assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == approval_for_testing
				#Show the incursion count for testing and recording purposes
				print("Incursion Count: %d"%self.group.get_player_by_id(1).participant.vars['incursion_count'])
				#Show the funds of each player at round 5 and round 15 for reecording purposes
				if(self.subsession.round_number == 5 or self.subsession.round_number == 15):
					for p in self.group.get_players():
						#Show the funds
						print("Player %d: Funds %f"%(p.id_in_group, p.participant.vars["funds"]))
						#Show the cost
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				#It always shows the cost each player put in
				else:
					for p in self.group.get_players():
						#Show the cost
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			#Test with doing 1/4 of whatever the max protection is set to, protection equation tested, incursion unpredictable
			elif self.case == 'quarter':
				#Do the pledging pages if pledging is on
				if(self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 1 or self.subsession.round_number == 1)):
					
					yield (views.GroupPledging, {'groupTarget' : random.randint(min_prob, 100)})
					targets = []
					for p in self.group.get_players():
						targets.append(p.groupTarget)
					targets.sort()
					assert self.group.GroupTargetProbability == median(targets)
					yield (views.IndiPledging, {'individualPledge' : round(random.uniform(0.0, max_p),2)})
					if(self.session.config["Papproval"] == True):
						yield(views.PledgingApproval , {'approval_1' : -6, 
														'approval_2' : -6, 
														'approval_3' : -6, 
														'approval_4' : -6, 
														'approval_5' : -6, 
														'approval_6' : -6, 
														'approval_7' : -6, 
														'approval_8' : -6, 
														'approval_9' : -6, 
														'approval_10' : -6, 
														'approval_11' : -6, 
														'approval_12' : -6, 
														'approval_13' : -6, 
														'approval_14' : -6, 
														'approval_15' : -6, 
														'approval_16' : -6, 
														'approval_17' : -6, 
														'approval_18' : -6, 
														'approval_19' : -6, 
														'approval_20' : -6})
						assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == -6								
														
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
					cost_factor = max_p//-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				yield (views.Round, {'cost': round(0.25*max_p, 2)})
				yield (views.Results)
				cost_for_test = self.player.cost
				assert self.player.protection == self.calculate_protection_for_test(max_p, cost_for_test)

				#If there was an incursion
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
					
				if(self.session.config["Capproval"] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0):
					yield(views.ActionApproval , {'approval_1' : -6, 
												  'approval_2' : -6, 
												  'approval_3' : -6, 
												  'approval_4' : -6, 
												  'approval_5' : -6, 
												  'approval_6' : -6, 
												  'approval_7' : -6, 
												  'approval_8' : -6, 
												  'approval_9' : -6, 
												  'approval_10' : -6, 
												  'approval_11' : -6, 
												  'approval_12' : -6, 
												  'approval_13' : -6, 
												  'approval_14' : -6, 
												  'approval_15' : -6, 
												  'approval_16' : -6, 
												  'approval_17' : -6, 
												  'approval_18' : -6, 
												  'approval_19' : -6, 
												  'approval_20' : -6})
					assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == -6							  
				print("Incursion Count: %d"%self.group.get_player_by_id(1).participant.vars['incursion_count'])
				if(self.subsession.round_number == 5 or self.subsession.round_number == 15):
					for p in self.group.get_players():
						print("Player %d: Funds %f"%(p.id_in_group, p.participant.vars["funds"]))
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				else:
					for p in self.group.get_players():
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			#Test with doing 1/2 of whatever the max protection is set to, protection equation tested, incursion unpredictable
			elif self.case == 'half':
				#Do the pledging pages if pledging is on
				if(self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 1 or self.subsession.round_number == 1)):
					
					yield (views.GroupPledging, {'groupTarget' : random.randint(min_prob, 100)})
					targets = []
					for p in self.group.get_players():
						targets.append(p.groupTarget)
					targets.sort()
					assert self.group.GroupTargetProbability == median(targets)
					yield (views.IndiPledging, {'individualPledge' : round(random.uniform(0.0, max_p),2)})
					if(self.session.config["Papproval"] == True):
						yield(views.PledgingApproval , {'approval_1' : 3, 
														'approval_2' : 3, 
														'approval_3' : 3, 
														'approval_4' : 3, 
														'approval_5' : 3, 
														'approval_6' : 3, 
														'approval_7' : 3, 
														'approval_8' : 3, 
														'approval_9' : 3, 
														'approval_10' : 3, 
														'approval_11' : 3, 
														'approval_12' : 3, 
														'approval_13' : 3, 
														'approval_14' : 3, 
														'approval_15' : 3, 
														'approval_16' : 3, 
														'approval_17' : 3, 
														'approval_18' : 3, 
														'approval_19' : 3, 
														'approval_20' : 3})
						assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == 3
						
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
					cost_factor = max_p//-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				yield (views.Round, {'cost': round(0.5*max_p, 2)})
				yield (views.Results)
				cost_for_test = self.player.cost
				assert self.player.protection == self.calculate_protection_for_test(max_p, cost_for_test)
				
				#If there was an incursion
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				
				if(self.session.config["Capproval"] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0):
					yield(views.ActionApproval , {'approval_1' : 3, 
												  'approval_2' : 3, 
												  'approval_3' : 3, 
												  'approval_4' : 3, 
												  'approval_5' : 3, 
												  'approval_6' : 3, 
												  'approval_7' : 3, 
												  'approval_8' : 3, 
												  'approval_9' : 3, 
												  'approval_10' : 3, 
												  'approval_11' : 3, 
												  'approval_12' : 3, 
												  'approval_13' : 3, 
												  'approval_14' : 3, 
												  'approval_15' : 3, 
												  'approval_16' : 3, 
												  'approval_17' : 3, 
												  'approval_18' : 3, 
												  'approval_19' : 3, 
												  'approval_20' : 3})
					assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == 3							  
				print("Incursion Count: %d"%self.group.get_player_by_id(1).participant.vars['incursion_count'])
				if(self.subsession.round_number == 5 or self.subsession.round_number == 15):
					for p in self.group.get_players():
						print("Player %d: Funds %f"%(p.id_in_group, p.participant.vars["funds"]))
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				else:
					for p in self.group.get_players():
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			#Test with doing 3/4 of whatever the max protection is set to, protection equation tested, incursion somewhat predictable, entering point of diminishing returns for protection	  
			elif self.case == 'threequarters':
				#Do the pledging pages if pledging is on
				if(self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 1 or self.subsession.round_number == 1)):
					
					yield (views.GroupPledging, {'groupTarget' : random.randint(min_prob, 100)})
					targets = []
					for p in self.group.get_players():
						targets.append(p.groupTarget)
					targets.sort()
					assert self.group.GroupTargetProbability == median(targets)
					yield (views.IndiPledging, {'individualPledge' : round(random.uniform(0.0, max_p),2)})
					if(self.session.config["Papproval"] == True):
						yield(views.PledgingApproval , {'approval_1' : 6, 
														'approval_2' : 6, 
														'approval_3' : 6, 
														'approval_4' : 6, 
														'approval_5' : 6, 
														'approval_6' : 6, 
														'approval_7' : 6, 
														'approval_8' : 6, 
														'approval_9' : 6, 
														'approval_10' : 6, 
														'approval_11' : 6, 
														'approval_12' : 6, 
														'approval_13' : 6, 
														'approval_14' : 6, 
														'approval_15' : 6, 
														'approval_16' : 6, 
														'approval_17' : 6, 
														'approval_18' : 6, 
														'approval_19' : 6, 
														'approval_20' : 6})
						assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == 6								
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
					cost_factor = max_p//-math.log(1 - Constants.max_probability + self.session.config["probability_coefficient"])
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				yield (views.Round, {'cost': round(0.75*max_p, 2)})
				yield (views.Results)
				cost_for_test = self.player.cost
				assert self.player.protection == self.calculate_protection_for_test(max_p, cost_for_test)

				#If there was an incursion
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				
				if(self.session.config["Capproval"] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0):
					yield(views.ActionApproval , {'approval_1' : 6, 
												  'approval_2' : 6, 
												  'approval_3' : 6, 
												  'approval_4' : 6, 
												  'approval_5' : 6, 
												  'approval_6' : 6, 
												  'approval_7' : 6, 
												  'approval_8' : 6, 
												  'approval_9' : 6, 
												  'approval_10' : 6, 
												  'approval_11' : 6, 
												  'approval_12' : 6, 
												  'approval_13' : 6, 
												  'approval_14' : 6, 
												  'approval_15' : 6, 
												  'approval_16' : 6, 
												  'approval_17' : 6, 
												  'approval_18' : 6, 
												  'approval_19' : 6, 
												  'approval_20' : 6})
					assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == 6
				print("Incursion Count: %d"%self.group.get_player_by_id(1).participant.vars['incursion_count'])
				if(self.subsession.round_number == 5 or self.subsession.round_number == 15):
					for p in self.group.get_players():
						print("Player %d: Funds %f"%(p.id_in_group, p.participant.vars["funds"]))
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				else:
					for p in self.group.get_players():
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			#Test with doing whatever the max protection is set to, protection equation tested, incursion mostly predictable.
			elif self.case == 'full':
				#Do the pledging pages if pledging is on
				if(self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 1 or self.subsession.round_number == 1)):
					
					yield (views.GroupPledging, {'groupTarget' : random.randint(min_prob, 100)})
					targets = []
					for p in self.group.get_players():
						targets.append(p.groupTarget)
					targets.sort()
					assert self.group.GroupTargetProbability == median(targets)
					yield (views.IndiPledging, {'individualPledge' : round(random.uniform(0.0, max_p),2)})
					if(self.session.config["Papproval"] == True):
						yield(views.PledgingApproval , {'approval_1' : 0, 
														'approval_2' : 0, 
														'approval_3' : 0, 
														'approval_4' : 0, 
														'approval_5' : 0, 
														'approval_6' : 0, 
														'approval_7' : 0, 
														'approval_8' : 0, 
														'approval_9' : 0, 
														'approval_10' : 0, 
														'approval_11' : 0, 
														'approval_12' : 0, 
														'approval_13' : 0, 
														'approval_14' : 0, 
														'approval_15' : 0, 
														'approval_16' : 0, 
														'approval_17' : 0, 
														'approval_18' : 0, 
														'approval_19' : 0, 
														'approval_20' : 0})
					assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == 0
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				yield (views.Round, {'cost': round(max_p, 2)})
				yield (views.Results)
				cost_for_test = self.player.cost
				assert self.player.protection == self.calculate_protection_for_test(max_p, max_p)

				#If there was an incursion
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				
				if(self.session.config["Capproval"] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0):
					yield(views.ActionApproval , {'approval_1' : 0, 
												  'approval_2' : 0, 
												  'approval_3' : 0, 
												  'approval_4' : 0, 
												  'approval_5' : 0, 
												  'approval_6' : 0, 
												  'approval_7' : 0, 
												  'approval_8' : 0, 
												  'approval_9' : 0, 
												  'approval_10' : 0, 
												  'approval_11' : 0, 
												  'approval_12' : 0, 
												  'approval_13' : 0, 
												  'approval_14' : 0, 
												  'approval_15' : 0, 
												  'approval_16' : 0, 
												  'approval_17' : 0, 
												  'approval_18' : 0, 
												  'approval_19' : 0, 
												  'approval_20' : 0})
					assert self.group.get_player_by_id(1).participant.vars["approval_means"][0] == 0
				print("Incursion Count: %d"%self.group.get_player_by_id(1).participant.vars['incursion_count'])
				if(self.subsession.round_number == 5 or self.subsession.round_number == 15):
					for p in self.group.get_players():
						print("Player %d: Funds %f"%(p.id_in_group, p.participant.vars["funds"]))
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				else:
					for p in self.group.get_players():
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)		
			#Test with any player's id that are even as 0 protection cost, odd are using full protection cost.
			elif self.case == 'half0halffull':
				#Do the pledging pages if pledging is on
				if(self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 1 or self.subsession.round_number == 1)):
					
					yield (views.GroupPledging, {'groupTarget' : random.randint(min_prob, 100)})
					targets = []
					for p in self.group.get_players():
						targets.append(p.groupTarget)
					targets.sort()
					assert self.group.GroupTargetProbability == median(targets)
					yield (views.IndiPledging, {'individualPledge' : round(random.uniform(0.0, max_p),2)})
					if(self.session.config["Papproval"] == True):
						yield(views.PledgingApproval , {'approval_1' : random.randint(-6, 6), 
														'approval_2' : random.randint(-6, 6), 
														'approval_3' : random.randint(-6, 6), 
														'approval_4' : random.randint(-6, 6), 
														'approval_5' : random.randint(-6, 6), 
														'approval_6' : random.randint(-6, 6), 
														'approval_7' : random.randint(-6, 6), 
														'approval_8' : random.randint(-6, 6), 
														'approval_9' : random.randint(-6, 6), 
														'approval_10' : random.randint(-6, 6), 
														'approval_11' : random.randint(-6, 6), 
														'approval_12' : random.randint(-6, 6), 
														'approval_13' : random.randint(-6, 6), 
														'approval_14' : random.randint(-6, 6), 
														'approval_15' : random.randint(-6, 6), 
														'approval_16' : random.randint(-6, 6), 
														'approval_17' : random.randint(-6, 6), 
														'approval_18' : random.randint(-6, 6), 
														'approval_19' : random.randint(-6, 6), 
														'approval_20' : random.randint(-6, 6)})
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#If Player ID is even
				if self.player.id % 2 == 0:
					yield (views.Round, {'cost': round(0,2)})
				#If Player ID is odd
				else:
					yield (views.Round, {'cost': round(max_p,2)})
				yield (views.Results)
				cost_for_test = 0
				#The protection equation will be tested based on the raw value for the cost, based on the Player ID being odd or even
				if self.player.id % 2 == 0:
					assert self.player.protection == self.calculate_protection_for_test(max_p, 0)
				else:
					assert self.player.protection == self.calculate_protection_for_test(max_p, max_p)
					cost_for_test = max_p

				#If there was an incursion
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				
				if(self.session.config["Capproval"] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0):
					yield(views.ActionApproval , {'approval_1' : random.randint(-6, 6), 
												  'approval_2' : random.randint(-6, 6), 
												  'approval_3' : random.randint(-6, 6), 
												  'approval_4' : random.randint(-6, 6), 
												  'approval_5' : random.randint(-6, 6), 
												  'approval_6' : random.randint(-6, 6), 
												  'approval_7' : random.randint(-6, 6), 
												  'approval_8' : random.randint(-6, 6), 
												  'approval_9' : random.randint(-6, 6), 
												  'approval_10' : random.randint(-6, 6), 
												  'approval_11' : random.randint(-6, 6), 
												  'approval_12' : random.randint(-6, 6), 
												  'approval_13' : random.randint(-6, 6), 
												  'approval_14' : random.randint(-6, 6), 
												  'approval_15' : random.randint(-6, 6), 
												  'approval_16' : random.randint(-6, 6), 
												  'approval_17' : random.randint(-6, 6), 
												  'approval_18' : random.randint(-6, 6), 
												  'approval_19' : random.randint(-6, 6), 
												  'approval_20' : random.randint(-6, 6)})
				print("Incursion Count: %d"%self.group.get_player_by_id(1).participant.vars['incursion_count'])
				if(self.subsession.round_number == 5 or self.subsession.round_number == 15):
					for p in self.group.get_players():
						print("Player %d: Funds %f"%(p.id_in_group, p.participant.vars["funds"]))
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				else:
					for p in self.group.get_players():
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)		
			#Test with doing 0 protection cost, protection equation tested, incursion completely predictable, guranteed incursion all the time
			elif self.case == 'bankrupt':
				#Do the pledging pages if pledging is on
				if(self.session.config['pledge'] == True and (self.subsession.round_number % self.session.config["pledge_looper"] == 1 or self.subsession.round_number == 1)):
					
					yield (views.GroupPledging, {'groupTarget' : random.randint(min_prob, 100)})
					targets = []
					for p in self.group.get_players():
						targets.append(p.groupTarget)
					targets.sort()
					assert self.group.GroupTargetProbability == median(targets)
					yield (views.IndiPledging, {'individualPledge' : round(random.uniform(0.0, max_p),2)})
					if(self.session.config["Papproval"] == True):
						yield(views.PledgingApproval , {'approval_1' : random.randint(-6, 6), 
														'approval_2' : random.randint(-6, 6), 
														'approval_3' : random.randint(-6, 6), 
														'approval_4' : random.randint(-6, 6), 
														'approval_5' : random.randint(-6, 6), 
														'approval_6' : random.randint(-6, 6), 
														'approval_7' : random.randint(-6, 6), 
														'approval_8' : random.randint(-6, 6), 
														'approval_9' : random.randint(-6, 6), 
														'approval_10' : random.randint(-6, 6), 
														'approval_11' : random.randint(-6, 6), 
														'approval_12' : random.randint(-6, 6), 
														'approval_13' : random.randint(-6, 6), 
														'approval_14' : random.randint(-6, 6), 
														'approval_15' : random.randint(-6, 6), 
														'approval_16' : random.randint(-6, 6), 
														'approval_17' : random.randint(-6, 6), 
														'approval_18' : random.randint(-6, 6), 
														'approval_19' : random.randint(-6, 6), 
														'approval_20' : random.randint(-6, 6)})
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				yield (views.Round, {'cost': round(0, 2)})
				yield (views.Results)
				#Should return 0 == 0 == True
				assert self.player.protection == self.calculate_protection_for_test(max_p, 0)
				cost_for_test = self.player.cost
				#If there was an incursion
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
					
				if(self.session.config["Capproval"] == True and self.subsession.round_number % self.session.config["contribution_looper"] == 0):
					yield(views.ActionApproval , {'approval_1' : random.randint(-6, 6), 
												  'approval_2' : random.randint(-6, 6), 
												  'approval_3' : random.randint(-6, 6), 
												  'approval_4' : random.randint(-6, 6), 
												  'approval_5' : random.randint(-6, 6), 
												  'approval_6' : random.randint(-6, 6), 
												  'approval_7' : random.randint(-6, 6), 
												  'approval_8' : random.randint(-6, 6), 
												  'approval_9' : random.randint(-6, 6), 
												  'approval_10' : random.randint(-6, 6), 
												  'approval_11' : random.randint(-6, 6), 
												  'approval_12' : random.randint(-6, 6), 
												  'approval_13' : random.randint(-6, 6), 
												  'approval_14' : random.randint(-6, 6), 
												  'approval_15' : random.randint(-6, 6), 
												  'approval_16' : random.randint(-6, 6), 
												  'approval_17' : random.randint(-6, 6), 
												  'approval_18' : random.randint(-6, 6), 
												  'approval_19' : random.randint(-6, 6), 
												  'approval_20' : random.randint(-6, 6)})
				print("Incursion Count: %d"%self.group.get_player_by_id(1).participant.vars['incursion_count'])
				if(self.subsession.round_number == 5 or self.subsession.round_number == 15):
					for p in self.group.get_players():
						print("Player %d: Funds %f"%(p.id_in_group, p.participant.vars["funds"]))
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				else:
					for p in self.group.get_players():
						print("Player %d: Cost %f"%(p.id_in_group, p.cost))
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)		
		#The set_leader option was set to true upon creating test session, now do scenario where one player does their protection first and everyone else gets to see it
		else:
			#It will go through the cases exactly as before with minor changes
			if self.case == 'random':
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#It will need to check for the leader, if it is the leader then...
				if self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group:
					yield(views.SoloRound, {'cost': round(random.uniform(0.0, max_p),2)})
				#If it isn't the leader then...
				else:
					yield(views.OthersRound, {'cost': round(random.uniform(0.0, max_p),2)})
				#Display Results
				yield(views.Results)
				
				cost_for_test = self.player.cost
				#If there was an incursion, the functions should be the same, we have tested the protection equation completely works quite well, not testing here
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			elif self.case == 'quarter':
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#It will need to check for the leader, if it is the leader then...
				if self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group:
					yield (views.SoloRound, {'cost': round(0.25*max_p, 2)})
				#If it isn't the leader then...
				else:
					yield (views.OthersRound, {'cost': round(0.25*max_p, 2)})
				yield(views.Results)

				cost_for_test = self.player.cost
				#If there was an incursion, the functions should be the same, we have tested the protection equation completely works quite well, not testing here
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			elif self.case == 'half':
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#It will need to check for the leader, if it is the leader then...
				if self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group:
					yield (views.SoloRound, {'cost': round(0.5*max_p,2)})
				#If it isn't the leader then...
				else:
					yield (views.OthersRound, {'cost': round(0.5*max_p,2)})
				yield(views.Results)

				cost_for_test = self.player.cost
				#If there was an incursion, the functions should be the same, we have tested the protection equation completely works quite well, not testing here
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			elif self.case == 'threequarters':
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#It will need to check for the leader, if it is the leader then...
				if self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group:
					yield (views.SoloRound, {'cost': round(0.75*max_p,2)})
				#If it isn't the leader then...
				else:
					yield (views.OthersRound, {'cost': round(0.75*max_p,2)})
				yield(views.Results)

				cost_for_test = self.player.cost
				#If there was an incursion, the functions should be the same, we have tested the protection equation completely works quite well, not testing here
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			elif self.case == 'full':
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#It will need to check for the leader, if it is the leader then...
				if self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group:
					yield (views.SoloRound, {'cost': round(max_p, 2)})
				#If it isn't the leader then...
				else:
					yield (views.OthersRound, {'cost': round(max_p, 2)})
				yield(views.Results)

				cost_for_test = self.player.cost
				#If there was an incursion, the functions should be the same, we have tested the protection equation completely works quite well, not testing here
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			elif self.case == 'half0halffull':
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#Check if the player is the leader first
				if self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group:
					#Then check the player's ID to apply which cost they do, same as before even = 0, odd = max_p
					if self.player.id % 2 == 0:
						yield (views.SoloRound, {'cost': round(0,2)})
					else:
						yield (views.SoloRound, {'cost': round(max_p,2)})
				#If the Player isn't the Leader
				else:
					if self.player.id % 2 == 0:
						yield (views.OthersRound, {'cost': round(0,2)})
					else:
						yield (views.OthersRound, {'cost': round(max_p,2)})
				yield(views.Results)
				
				cost_for_test = self.player.cost
				#If there was an incursion, the functions should be the same, we have tested the protection equation completely works quite well, not testing here
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)
			elif self.case == 'bankrupt':
				#Display the Chat 
				if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
					yield (views.Chat)
				#Get the revenue
				revenue_value = self.session.config['revenue']
				#Get the upkeep
				upkeep_value = self.session.config['upkeep']
				#Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
				if self.session.config['dynamic_finances'] == True:
					revenue_value = revenue[self.subsession.round_number - 1]
					upkeep_value = upkeep[self.subsession.round_number - 1]
					max_p = protection_array[self.subsession.round_number - 1]
				#Get the current funds in the players disposal
				current_funds = self.player.participant.vars['funds']
				#It will need to check for the leader, if it is the leader then...
				if self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group:
					yield (views.SoloRound, {'cost': round(0, 2)})
				#If it isn't the leader then...
				else:
					yield (views.OthersRound, {'cost': round(0, 2)})
				yield(views.Results)
				cost_for_test = self.player.cost
				#If there was an incursion
				if self.group.incursion:
					#Then assert that it just took off the cost of protection and the upkeep
					assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
				else:
					#Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
					assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value
				if(self.subsession.round_number == 15):
					print("Completed %s"%self.case)