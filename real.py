from colorfight import Colorfight
import time
import random
from colorfight.constants import BLD_GOLD_MINE, BLD_ENERGY_WELL, BLD_FORTRESS, BLD_HOME

game = Colorfight()
game.connect(room = 'groupd')

if game.register(username = 'kg', \
        password = 'colorclash'):
    while True:
        cmd_list = []
        my_attack_list = []
        # update_turn() is required to get the latest information from the
        # server. This will halt the program until it receives the updated
        # information. 
        # After update_turn(), game object will be updated.   
        game.update_turn()

        # Check if you exist in the game. If not, wait for the next round.
        # You may not appear immediately after you join. But you should be 
        # in the game after one round.
        if game.me == None:
            continue

        me = game.me

        # game.me.cells is a dict, where the keys are Position and the values
        # are MapCell. Get all my cells.
        newlist = list()
        for i in game.me.cells.values():
            newlist.append(i)
        haveHome = 0
        for cell in newlist:
            if cell.is_home:
                haveHome = 1
        for cell in reversed(newlist):
            if haveHome == 0:
                cmd_list.append(game.build(cell.position, BLD_HOME))
                haveHome += 1
            if cell.owner == me.uid and cell.building.is_empty and me.gold >= 100:
                # building = random.choice([BLD_GOLD_MINE])
                if game.turn < 200:
                    cmd_list.append(game.build(cell.position, BLD_ENERGY_WELL))
                else:
                    cmd_list.append(game.build(cell.position, BLD_GOLD_MINE))
                # print("We build {} on ({}, {})".format(building, cell.position.x, cell.position.y))
                me.gold -= 100
            if cell.building.can_upgrade and \
                    (cell.building.is_home or cell.building.level < me.tech_level) and \
                    cell.building.upgrade_gold < me.gold and \
                    cell.building.upgrade_energy < me.energy: # and cell.building.name != "energy_well"
                cmd_list.append(game.upgrade(cell.position))
                print("We upgraded ({}, {})".format(cell.position.x, cell.position.y))
                me.gold   -= cell.building.upgrade_gold
                me.energy -= cell.building.upgrade_energy
            # Check the surrounding position
            for pos in cell.position.get_surrounding_cardinals():
                # Get the MapCell object of that position
                c = game.game_map[pos]
                # print(haveHome)
                # Attack if the cost is less than what I have, and the owner
                # is not mine, and I have not attacked it in this round already
                # We also try to keep our cell number under 100 to avoid tax
                if c.attack_cost < me.energy and c.owner != game.uid \
                        and c.position not in my_attack_list and game.turn < 400 and c.owner == 0:
                    cmd_list.append(game.attack(pos, c.attack_cost))
                    print("We are attacking ({}, {}) with {} energy".format(pos.x, pos.y, c.attack_cost))
                    game.me.energy -= c.attack_cost
                    my_attack_list.append(c.position)
                elif c.attack_cost < me.energy and c.owner != game.uid \
                        and c.position not in my_attack_list and game.turn < 400:
                    # Add the attack command in the command list
                    # Subtract the attack cost manually so I can keep track
                    # of the energy I have.
                    # Add the position to the attack list so I won't attack
                    # the same cell
                    cmd_list.append(game.attack(pos, c.attack_cost))
                    print("We are attacking ({}, {}) with {} energy".format(pos.x, pos.y, c.attack_cost))
                    game.me.energy -= c.attack_cost
                    my_attack_list.append(c.position)

            # If we can upgrade the building, upgrade it.
            # Notice can_update only checks for upper bound. You need to check
            # tech_level by yourself. 
            # if cell.building.can_upgrade and \
            #         (cell.building.is_home or cell.building.level < me.tech_level) and \
            #         cell.building.upgrade_gold < me.gold and \
            #         cell.building.upgrade_energy < me.energy:
            #     cmd_list.append(game.upgrade(cell.position))
            #     print("We upgraded ({}, {})".format(cell.position.x, cell.position.y))
            #     me.gold   -= cell.building.upgrade_gold
            #     me.energy -= cell.building.upgrade_energy
                
            # Build a random building if we have enough gold
            # if cell.owner == me.uid and cell.building.is_empty and me.gold >= 100:
            #     # building = random.choice([BLD_GOLD_MINE])
            #     if game.turn < 200:
            #         cmd_list.append(game.build(cell.position, BLD_ENERGY_WELL))
            #     else:
            #         cmd_list.append(game.build(cell.position, BLD_GOLD_MINE))
            #     # print("We build {} on ({}, {})".format(building, cell.position.x, cell.position.y))
            #     me.gold -= 100

        
        # Send the command list to the server
        result = game.send_cmd(cmd_list)
        print(result)
