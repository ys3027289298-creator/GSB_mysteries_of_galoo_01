import os
import tempfile
import unittest

from helpers import fresh_hero

import save
from map_creator import Map, SolarSystem, create_dungeon


class CrossModuleStateSyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.char_file = os.path.join(self.tmp.name, 'save_file.pkl')
        self.solar_file = os.path.join(self.tmp.name, 'solar_system.pkl')

    def tearDown(self):
        self.tmp.cleanup()

    def test_character_and_map_state_reload_consistently(self):
        hero = fresh_hero()
        hero.add_to_inventory({'Gold': 42, 'Dust': 3})
        hero._experience_points = 500

        game_map = Map(create_dungeon(), 2, 2, 1, 1)
        game_map._grid[2][1] = 'Empty    '  # simulate a cleared dungeon
        solar = SolarSystem([[[game_map]]])
        solar._col = 1

        save.save_game(hero, solar, self.char_file, self.solar_file)
        loaded_hero, loaded_solar = save.load_game(self.char_file, self.solar_file)

        self.assertEqual(loaded_hero._inventory['Gold'], hero._inventory['Gold'])
        self.assertEqual(loaded_hero._inventory['Dust'], 3)
        self.assertEqual(loaded_hero._experience_points, 500)
        self.assertEqual(loaded_solar._col, 1)
        loaded_map = loaded_solar._solar_system[0][0][0]
        self.assertEqual(loaded_map._grid[2][1], 'Empty    ')

    def test_paired_files_share_save_id(self):
        hero = fresh_hero()
        solar = SolarSystem([[[Map(create_dungeon(), 2, 2, 1, 1)]]])
        save.save_game(hero, solar, self.char_file, self.solar_file)
        char_meta = save.inspect_save(self.char_file)
        solar_meta = save.inspect_save(self.solar_file)
        self.assertEqual(char_meta['version'], save.SAVE_VERSION)
        self.assertIsNotNone(char_meta['save_id'])
        self.assertEqual(char_meta['save_id'], solar_meta['save_id'])


if __name__ == '__main__':
    unittest.main()
