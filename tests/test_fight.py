import unittest
from unittest import mock

import fight
from character import Goblin
from tests.helpers import ATTRS, make_character


class TestFightSettlement(unittest.TestCase):
    def setUp(self):
        self.hero = make_character('Hero')
        self.enemy = Goblin(dict(ATTRS), 'Baddie')
        self.enemy.add_to_inventory({'Gold': 3, 'Dirty Clothes': 1})

    def test_loot_granted_exactly_once(self):
        with mock.patch.object(fight, 'sleep', lambda *_: None):
            self.assertTrue(fight.settle_victory(self.hero, self.enemy))
            self.assertFalse(fight.settle_victory(self.hero, self.enemy))
        self.assertEqual(self.hero._inventory.get('Gold'), 3)
        self.assertEqual(self.hero._inventory.get('Dirty Clothes'), 1)

    def test_experience_granted_once(self):
        with mock.patch.object(fight, 'sleep', lambda *_: None):
            fight.settle_victory(self.hero, self.enemy)
            fight.settle_victory(self.hero, self.enemy)
        self.assertEqual(self.hero._experience_points, 500)


if __name__ == '__main__':
    unittest.main()
