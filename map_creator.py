# Kandu! Entertainment est. 6/30/2018
# This is the map module. This module will setup the map class
# for all the maps in the game plus the worlds about 1600 rooms to
# explore

import fight as f
import setup
import encounters
from map_creator import *
from store import *
import random
import save
import sys

empty = 'Empty    '
room = 'Dungeon  '
zero = '0        '
player = 'Player   '


def create_dungeon():
    return _random_layout()


def _random_layout(room_count=8):
    grid = [[zero for _ in range(5)] for _ in range(5)]
    grid[2][2] = player
    frontier = [(2, 2)]
    placed = 0
    while placed < room_count and frontier:
        row, col = random.choice(frontier)
        neighbors = [(row + dr, col + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                     if 0 <= row + dr < 5 and 0 <= col + dc < 5
                     and grid[row + dr][col + dc] == zero]
        if not neighbors:
            frontier.remove((row, col))
            continue
        new_row, new_col = random.choice(neighbors)
        grid[new_row][new_col] = room
        frontier.append((new_row, new_col))
        placed += 1
    return grid


def _layout_signature(grid):
    return tuple(tuple(row) for row in grid)


def create_unique_dungeon(used_signatures):
    for _ in range(1000):
        grid = _random_layout()
        if _layout_signature(grid) not in used_signatures:
            return grid
    return _random_layout()


class Map:
    def __init__(self, grid, x, y, map_number, world_number):
        self._grid = grid
        self._start_x = x
        self._start_y = y
        self._map_number = map_number
        self._world_number = world_number
        self._played_intro = False

    def choose_different_room(self):
        print()
        print("Next time pick a space that has a Dungeon!!!")
        print()

    def up(self):

        self._start_y -= 1
        if self._grid[self._start_y][self._start_x] == room:
            if self.dungeon_selector():
                pass
            else:
                self._start_y += 1
                return
        if self._grid[self._start_y][self._start_x] == zero:
            self.choose_different_room()
            self._start_y += 1
            return
        self._grid[self._start_y][self._start_x] = player
        self._start_y += 1
        self._grid[self._start_y][self._start_x] = empty
        self._start_y -= 1

    def down(self):

        self._start_y += 1
        if self._grid[self._start_y][self._start_x] == room:
            if self.dungeon_selector():
                pass
            else:
                self._start_y -= 1
                return
        if self._grid[self._start_y][self._start_x] == zero:
            self.choose_different_room()
            self._start_y -= 1
            return
        self._grid[self._start_y][self._start_x] = player
        self._start_y -= 1
        self._grid[self._start_y][self._start_x] = empty
        self._start_y += 1

    def right(self):

        self._start_x += 1
        if self._grid[self._start_y][self._start_x] == room:
            if self.dungeon_selector():
                pass
            else:
                self._start_x -= 1
                return
        if self._grid[self._start_y][self._start_x] == zero:
            self.choose_different_room()
            self._start_x -= 1
            return
        self._grid[self._start_y][self._start_x] = player
        self._start_x -= 1
        self._grid[self._start_y][self._start_x] = empty
        self._start_x += 1

    def left(self):

        self._start_x -= 1
        if self._grid[self._start_y][self._start_x] == room:
            if self.dungeon_selector():
                pass
            else:
                self._start_x += 1
                return
        if self._grid[self._start_y][self._start_x] == zero:
            self.choose_different_room()
            self._start_x += 1
            return
        self._grid[self._start_y][self._start_x] = player
        self._start_x += 1
        self._grid[self._start_y][self._start_x] = empty
        self._start_x -= 1

    def dungeon_selector(self):

        if self._world_number == 1:
            defeated_enemy = f.fight(setup.starting_character, encounters.lvl_1_random_enemy())
            return defeated_enemy
        if self._world_number == 2:
            defeated_enemy = f.fight(setup.starting_character, encounters.lvl_2_random_enemy())
            return defeated_enemy
        if self._world_number == 3:
            defeated_enemy = f.fight(setup.starting_character, encounters.lvl_3_random_enemy())
            return defeated_enemy
        if self._world_number == 4:
            defeated_enemy = f.fight(setup.starting_character, encounters.lvl_4_random_enemy())
            return defeated_enemy
        if self._world_number == 5:
            defeated_enemy = f.fight(setup.starting_character, encounters.lvl_5_random_enemy())
            return defeated_enemy
        if self._world_number == 6:
            defeated_enemy = f.fight(setup.starting_character, encounters.lvl_6_random_enemy())
            return defeated_enemy
        if self._world_number == 7:
            defeated_enemy = f.fight(setup.starting_character, encounters.lvl_7_random_enemy())
            return defeated_enemy
        if self._world_number == 8:
            defeated_enemy = f.fight(setup.starting_character, encounters.lvl_8_random_enemy())
            return defeated_enemy

    def display_map(self):
        print()
        print("World Level: ", self._world_number)
        print("Map Level: ", self._map_number)
        for i in range(len(self._grid)):
            for j in range(len(self._grid[i])):
                print(self._grid[i][j], end='|')
            print()

    def map_engine(self):
        print()
        while True:
            self.display_map()
            choice = str(input("UP:1 Down:2 Left:3 Right:4 New Map:5 Store:6 Save:7 Quit:8 : "))
            if choice == '1':
                self.up()
                continue
            if choice == '2':
                self.down()
                continue
            if choice == '3':
                self.left()
                continue
            if choice == '4':
                self.right()
                continue
            if choice == '5':
                dungeon = 0
                for row in self._grid:
                    for col in row:
                        if col == room:
                            dungeon += 1
                        else:
                            continue
                if dungeon > 0:
                    print("You need to complete all the dungeons in order to move to a new map")
                else:
                    return
            if choice == '6':
                store = Store(setup.starting_character._type)
                store.display()
                setup.starting_character.playerinfo()
            elif choice == '7':
                save.save_game(setup.starting_character, setup.solar_system,
                                save.CHARACTER_FILE)
                print("Game Save Successful!")
            elif choice == '8':
                print("Leaving the world of galoo....")
                sys.exit()


class SolarSystem:

    def __init__(self, solar_system):
        self._solar_system = solar_system
        self._world = 0
        self._row = 0
        self._col = 0

    def play_solar_system(self):

        for world in enumerate(self._solar_system):
            index = world[0]
            world_obj = world[1]
            if index == self._world:
                for row in enumerate(world_obj):
                    index_row = row[0]
                    world_row = row[1]
                    if index_row == self._row:
                        for col in enumerate(world_row):
                            index_col = col[0]
                            world_col = col[1]
                            if index_col == self._col:
                                world_col.map_engine()
                                self._col += 1
                            else:
                                continue
                        self._col = 0
                        self._row += 1
                    else:
                        continue
                self._row = 0
                self._world += 1
            else:
                continue
        print("Congratulations you have completed the Mysteries of Galoo...")

def _build_world(world_number):
    used_signatures = set()
    world = []
    map_number = 1
    for _ in range(5):
        world_row = []
        for _ in range(5):
            grid = create_dungeon()
            signature = _layout_signature(grid)
            if signature in used_signatures:
                grid = create_unique_dungeon(used_signatures)
                signature = _layout_signature(grid)
            used_signatures.add(signature)
            world_row.append(Map(grid, 2, 2, map_number, world_number))
            map_number += 1
        world.append(world_row)
    return world


world_1 = _build_world(1)
world_2 = _build_world(2)
world_3 = _build_world(3)
world_4 = _build_world(4)
world_5 = _build_world(5)
world_6 = _build_world(6)
world_7 = _build_world(7)
world_8 = _build_world(8)

solar_system = [world_1, world_2, world_3, world_4, world_5, world_6, world_7, world_8]
