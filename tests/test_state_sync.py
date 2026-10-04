import os
import tempfile
import unittest

import map_creator
import save
from tests.helpers import make_character


class TestCrossModuleStateSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, 'save_file.pkl')

    def build_world(self):
        used = set()
        maps = [map_creator.Map(map_creator.create_unique_dungeon(used), 2, 2, n, 1)
                for n in (1, 2)]
        for game_map in maps:
            used.add(tuple(tuple(row) for row in game_map._grid))
        return map_creator.SolarSystem([[maps[0], maps[1]]])

    def test_quest_and_map_state_survive_reload(self):
        hero = make_character()
        solar = self.build_world()
        # Clear one dungeon and advance quest progress before saving.
        solar._solar_system[0][0]._grid[0][2] = map_creator.empty
        solar._col = 1
        save.save_game(hero, solar, self.path)

        loaded_hero, loaded_solar = save.load_game(self.path)
        self.assertEqual(loaded_hero._name, hero._name)
        self.assertEqual(loaded_solar._col, 1)
        self.assertEqual(loaded_solar._solar_system[0][0]._grid,
                         solar._solar_system[0][0]._grid)
        self.assertEqual(loaded_solar._solar_system[0][1]._grid,
                         solar._solar_system[0][1]._grid)

    def test_partial_save_cannot_desync_modules(self):
        # The bundle is a single atomic file: either both modules load or neither.
        hero = make_character()
        solar = self.build_world()
        save.save_game(hero, solar, self.path)
        with open(self.path, 'r+b') as fh:
            fh.truncate(os.path.getsize(self.path) // 2)
        with self.assertRaises(save.SaveCorruptError):
            save.load_game(self.path)


if __name__ == '__main__':
    unittest.main()
