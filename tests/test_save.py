import os
import pickle
import tempfile
import unittest

from helpers import fresh_hero

import save
from map_creator import Map, SolarSystem, create_dungeon


def small_solar_system():
    maps = [[Map(create_dungeon(), 2, 2, 1, 1), Map(create_dungeon(), 2, 2, 2, 1)]]
    return SolarSystem([maps])


class SaveRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.char_file = os.path.join(self.tmp.name, 'save_file.pkl')
        self.solar_file = os.path.join(self.tmp.name, 'solar_system.pkl')

    def tearDown(self):
        self.tmp.cleanup()

    def test_object_round_trip(self):
        hero = fresh_hero()
        save.save_object(hero, self.char_file)
        loaded = save.reload_object(self.char_file)
        self.assertEqual(loaded._name, hero._name)
        self.assertEqual(loaded._inventory, hero._inventory)
        self.assertEqual(loaded._gold, hero._gold)
        self.assertEqual(loaded._equipment, hero._equipment)
        self.assertEqual(loaded._level, hero._level)

    def test_game_round_trip(self):
        hero = fresh_hero()
        solar = small_solar_system()
        save.save_game(hero, solar, self.char_file, self.solar_file)
        loaded_hero, loaded_solar = save.load_game(self.char_file, self.solar_file)
        self.assertEqual(loaded_hero._inventory, hero._inventory)
        self.assertEqual(loaded_solar._world, solar._world)
        original_grids = [[m._grid for m in row] for row in solar._solar_system[0]]
        loaded_grids = [[m._grid for m in row] for row in loaded_solar._solar_system[0]]
        self.assertEqual(loaded_grids, original_grids)


class CorruptedSaveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.char_file = os.path.join(self.tmp.name, 'save_file.pkl')

    def tearDown(self):
        self.tmp.cleanup()

    def test_garbage_bytes_raise_save_error_not_crash(self):
        with open(self.char_file, 'wb') as f:
            f.write(b'this is not a pickle at all')
        with self.assertRaises(save.SaveCorruptError):
            save.reload_object(self.char_file)

    def test_truncated_pickle_raises_save_error_not_crash(self):
        hero = fresh_hero()
        save.save_object(hero, self.char_file)
        with open(self.char_file, 'r+b') as f:
            size = os.path.getsize(self.char_file)
            f.truncate(size // 2)
        with self.assertRaises(save.SaveCorruptError):
            save.reload_object(self.char_file)

    def test_corruption_is_save_error_subclass(self):
        with open(self.char_file, 'wb') as f:
            f.write(b'\x00\x01garbage')
        with self.assertRaises(save.SaveError):
            save.reload_object(self.char_file)


class VersionBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.char_file = os.path.join(self.tmp.name, 'save_file.pkl')
        self.solar_file = os.path.join(self.tmp.name, 'solar_system.pkl')

    def tearDown(self):
        self.tmp.cleanup()

    def test_future_version_rejected(self):
        envelope = {'galoo_save': True, 'version': save.SAVE_VERSION + 1,
                    'save_id': 'x', 'payload': None}
        with open(self.char_file, 'wb') as f:
            pickle.dump(envelope, f)
        with self.assertRaises(save.SaveVersionError):
            save.reload_object(self.char_file)

    def test_legacy_v1_raw_pickle_still_loads(self):
        hero = fresh_hero()
        with open(self.char_file, 'wb') as f:
            pickle.dump(hero, f, pickle.HIGHEST_PROTOCOL)
        loaded = save.reload_object(self.char_file)
        self.assertEqual(loaded._name, hero._name)

    def test_mismatched_pair_rejected(self):
        hero = fresh_hero()
        solar = small_solar_system()
        save.save_game(hero, solar, self.char_file, self.solar_file)
        # simulate a solar_system.pkl from a different playthrough/session
        save.save_object(small_solar_system(), self.solar_file)
        with self.assertRaises(save.SaveMismatchError):
            save.load_game(self.char_file, self.solar_file)


if __name__ == '__main__':
    unittest.main()
