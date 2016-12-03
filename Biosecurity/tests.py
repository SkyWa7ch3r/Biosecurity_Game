from otree.api import Currency as c, currency_range
from . import views
from ._builtin import Bot
from .models import Constants
import random
import csv
import math

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

class PlayerBot(Bot):
    cases = ['random', 'quarter', 'half' , 'threequarters', 'full', 'twoselfishtwogood', 'bankrupt']
    def play_round(self):
        #Get the max participants 
        max_p = self.session.config['max_protection']
        #Get the cost factor
        cost_factor = self.session.config['max_protection']/-math.log(0.01)
        #Display the Instructions
        if self.subsession.round_number == 1:
            yield(views.BioInstructions)
        #Display the ChatBox 
        if (self.subsession.round_number == 1 or self.subsession.round_number == 6 or self.subsession.round_number == 11) and self.session.config['player_communication'] == True:
            yield (views.ChatBox)

        #Check if the One Player Feature has been enabled, so one player goes before all the others
        if self.session.config['set_leader'] == False:

            #Test with random variable protection, protection equation is tested, incursion unpredictable
            if self.case == 'random':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
                #Get the current funds in the players disposal
                current_funds = self.player.participant.vars['funds']
                #Assign random protection cost    
                yield (views.Round, {'cost': round(random.uniform(0.0, max_p),2)})
                #Goto the Results Page
                yield (views.Results)
                cost_for_test = self.player.cost
                #Test the profit equation
                assert self.player.protection == c(1-math.exp(-cost_for_test/cost_factor))

                #If there was an incursion
                if self.group.incursion:
                    #Then assert that it just took off the cost of protection and the upkeep
                    assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
                else:
                    #Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
                    assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value

            #Test with doing 1/4 of whatever the max protection is set to, protection equation tested, incursion unpredictable
            elif self.case == 'quarter':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
                #Get the current funds in the players disposal
                current_funds = self.player.participant.vars['funds']
                yield (views.Round, {'cost': round(0.25*max_p, 2)})
                yield (views.Results)
                cost_for_test = self.player.cost
                assert self.player.protection == c(1-math.exp(-cost_for_test/cost_factor))

                #If there was an incursion
                if self.group.incursion:
                    #Then assert that it just took off the cost of protection and the upkeep
                    assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
                else:
                    #Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
                    assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value

            #Test with doing 1/2 of whatever the max protection is set to, protection equation tested, incursion unpredictable
            elif self.case == 'half':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
                #Get the current funds in the players disposal
                current_funds = self.player.participant.vars['funds']
                yield (views.Round, {'cost': round(0.5*max_p, 2)})
                yield (views.Results)
                cost_for_test = self.player.cost
                assert self.player.protection == c(1-math.exp(-cost_for_test/cost_factor))
                
                #If there was an incursion
                if self.group.incursion:
                    #Then assert that it just took off the cost of protection and the upkeep
                    assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
                else:
                    #Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
                    assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value

            #Test with doing 3/4 of whatever the max protection is set to, protection equation tested, incursion somewhat predictable, entering point of diminishing returns for protection   
            elif self.case == 'threequarters':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
                #Get the current funds in the players disposal
                current_funds = self.player.participant.vars['funds']
                yield (views.Round, {'cost': round(0.75*max_p, 2)})
                yield (views.Results)
                cost_for_test = self.player.cost
                assert self.player.protection == c(1-math.exp(-0.75*max_p/cost_factor))

                #If there was an incursion
                if self.group.incursion:
                    #Then assert that it just took off the cost of protection and the upkeep
                    assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
                else:
                    #Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
                    assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value

            #Test with doing whatever the max protection is set to, protection equation tested, incursion mostly predictable.
            elif self.case == 'full':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
                #Get the current funds in the players disposal
                current_funds = self.player.participant.vars['funds']
                yield (views.Round, {'cost': round(max_p, 2)})
                yield (views.Results)
                cost_for_test = self.player.cost
                assert self.player.protection == c(1-math.exp(-cost_for_test/cost_factor))

                #If there was an incursion
                if self.group.incursion:
                    #Then assert that it just took off the cost of protection and the upkeep
                    assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
                else:
                    #Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
                    assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value

            #Test with any player's id that are even as 0 protection cost, odd are using full protection cost.
            elif self.case == 'twoselfishtwogood':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
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
                    assert self.player.protection == c(1-math.exp(0/cost_factor))
                else:
                    assert self.player.protection == c(1-math.exp(-max_p/cost_factor))
                    cost_for_test = max_p

                #If there was an incursion
                if self.group.incursion:
                    #Then assert that it just took off the cost of protection and the upkeep
                    assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value
                else:
                    #Else if no incursion ,then assert that it just took off the cost of protection and the upkeep and ADD on the revenue to give profit
                    assert self.player.participant.vars['funds'] == current_funds + revenue_value - cost_for_test - upkeep_value

            #Test with doing 0 protection cost, protection equation tested, incursion completely predictable, guranteed incursion all the time
            elif self.case == 'bankrupt':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
                #Get the current funds in the players disposal
                current_funds = self.player.participant.vars['funds']
                yield (views.Round, {'cost': round(0, 2)})
                yield (views.Results)
                #Should return 0 == 0 == True
                assert self.player.protection == c(1-math.exp(0/cost_factor))
                #Incursion is ALWAYS TRUE
                assert self.group.incursion == True
                cost_for_test = self.player.cost
                #Since there's always an incursion it will never add the revenue, ensure that it doesn't
                assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value

        #The set_leader option was set to true upon creating test session, now do scenario where one player does their protection first and everyone else gets to see it
        else:
            #It will go through the cases exactly as before with minor changes
            if self.case == 'random':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
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

            elif self.case == 'quarter':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
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

            elif self.case == 'half':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
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

            elif self.case == 'threequarters':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
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

            elif self.case == 'full':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
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

            elif self.case == 'twoselfishtwogood':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
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

            elif self.case == 'bankrupt':
                #Get the revenue
                revenue_value = self.session.config['revenue']
                #Get the upkeep
                upkeep_value = self.session.config['upkeep']
                #Check if the dynamic finances has been applied and adjust the revenue and upkeep values accordingly
                if self.session.config['dynamic_finances'] == True:
                    revenue_value = revenue[self.subsession.round_number - 1]
                    upkeep_value = upkeep[self.subsession.round_number - 1]
                    max_p = protection_array[self.subsession.round_number - 1]
                    cost_factor = max_p/-math.log(0.01)
                #Get the current funds in the players disposal
                current_funds = self.player.participant.vars['funds']
                #It will need to check for the leader, if it is the leader then...
                if self.player.id_in_group == self.group.get_player_by_role('Leader').id_in_group:
                    yield (views.SoloRound, {'cost': round(0, 2)})
                #If it isn't the leader then...
                else:
                    yield (views.OthersRound, {'cost': round(0, 2)})
                yield(views.Results)
                #Incursion is ALWAYS TRUE
                assert self.group.incursion == True
                cost_for_test = self.player.cost
                #Since there's always an incursion it will never add the revenue, ensure that it doesn't
                assert self.player.participant.vars['funds'] == current_funds - cost_for_test - upkeep_value