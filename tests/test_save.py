import os
import pickle
import tempfile
import unittest

from tests.helpers import make_character
import save


class TestSerializationRoundTrip(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, 'save_file.pkl')

    def test_character_round_trip(self):
        hero = make_character()
        hero.add_to_inventory({'Gold': 25, 'Dust': 2})
        save.save_object(hero, self.path)
        loaded = save.reload_object(self.path)
        self.assertEqual(loaded._name, hero._name)
        self.assertEqual(loaded._inventory, hero._inventory)
        self.assertEqual(loaded._fight_health, hero._fight_health)
        self.assertEqual(loaded._level, hero._level)

    def test_bundle_round_trip_keeps_character_and_map_together(self):
        hero = make_character()
        map_state = {'world': 1, 'row': 0, 'col': 3}
        save.save_game(hero, map_state, self.path)
        loaded_hero, loaded_map = save.load_game(self.path)
        self.assertEqual(loaded_hero._name, hero._name)
        self.assertEqual(loaded_map, map_state)

    def test_corrupt_file_raises_save_error_not_crash(self):
        with open(self.path, 'wb') as fh:
            fh.write(b'this is not a pickle at all \x00\x01\x02')
        with self.assertRaises(save.SaveCorruptError):
            save.reload_object(self.path)

    def test_truncated_file_raises_save_error_not_crash(self):
        hero = make_character()
        save.save_object(hero, self.path)
        with open(self.path, 'rb') as fh:
            data = fh.read()
        with open(self.path, 'wb') as fh:
            fh.write(data[:len(data) // 2])
        with self.assertRaises(save.SaveCorruptError):
            save.reload_object(self.path)

    def test_missing_file_raises_save_error_not_crash(self):
        with self.assertRaises(save.SaveCorruptError):
            save.reload_object(self.path)

    def test_newer_version_is_rejected(self):
        payload = {'version': save.SAVE_VERSION + 1, 'payload': make_character()}
        with open(self.path, 'wb') as fh:
            pickle.dump(payload, fh, pickle.HIGHEST_PROTOCOL)
        with self.assertRaises(save.SaveVersionError):
            save.reload_object(self.path)

    def test_legacy_raw_pickle_still_loads(self):
        # Compatibility boundary: v1 saves are raw pickles with no envelope.
        hero = make_character()
        with open(self.path, 'wb') as fh:
            pickle.dump(hero, fh, pickle.HIGHEST_PROTOCOL)
        loaded = save.reload_object(self.path)
        self.assertEqual(loaded._name, hero._name)

    def test_legacy_two_file_save_loads_via_load_game(self):
        # v1 boundary: character and map lived in two separate raw pickles.
        hero = make_character()
        map_state = {'world': 2, 'row': 1, 'col': 0}
        with open(self.path, 'wb') as fh:
            pickle.dump(hero, fh, pickle.HIGHEST_PROTOCOL)
        legacy_map = os.path.join(self.tmp.name, 'solar_system.pkl')
        with open(legacy_map, 'wb') as fh:
            pickle.dump(map_state, fh, pickle.HIGHEST_PROTOCOL)
        loaded_hero, loaded_map = save.load_game(self.path)
        self.assertEqual(loaded_hero._name, hero._name)
        self.assertEqual(loaded_map, map_state)

    def test_corrupt_bundle_rejected_atomically(self):
        hero = make_character()
        save.save_game(hero, {'world': 1}, self.path)
        with open(self.path, 'r+b') as fh:
            fh.write(b'\xff' * 8)
        with self.assertRaises(save.SaveCorruptError):
            save.load_game(self.path)


if __name__ == '__main__':
    unittest.main()
