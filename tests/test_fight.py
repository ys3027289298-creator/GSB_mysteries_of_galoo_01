import contextlib
import io
import unittest
from unittest import mock

from helpers import fresh_hero

import encounters
import fight as fight_module
import game


class LootDuplicationTest(unittest.TestCase):
    def run_fight(self, hero, enemy):
        fight_module.sleep = lambda *args: None
        with mock.patch('builtins.input', return_value='1'):
            with contextlib.redirect_stdout(io.StringIO()):
                return fight_module.fight(hero, enemy)

    def test_loot_not_duplicated_when_same_enemy_defeated_twice(self):
        hero = fresh_hero()
        hero._fight_strength = 100000
        hero._fight_health = 100000
        enemy = encounters.troll(game.dusty_enemy)
        enemy._fight_health = 1

        self.assertTrue(self.run_fight(hero, enemy))
        dust_after_first = hero._inventory.get('Dust', 0)
        self.assertEqual(dust_after_first, 2)

        # enemy is reused (its health was restored by the fight module)
        enemy._fight_health = 1
        self.assertTrue(self.run_fight(hero, enemy))
        self.assertEqual(hero._inventory.get('Dust', 0), dust_after_first)


if __name__ == '__main__':
    unittest.main()
