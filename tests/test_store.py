import unittest

from helpers import fresh_hero

import setup
from game_items import get_inventory_item
from store import Store


class NegativeInventoryTest(unittest.TestCase):
    def setUp(self):
        self.hero = fresh_hero()
        self.store = Store(self.hero._type)

    def test_buy_negative_quantity_rejected(self):
        gold_before = self.hero._inventory['Gold']
        self.store.buy_inventory_item(get_inventory_item(1), -5)
        self.assertEqual(self.hero._inventory['Gold'], gold_before)
        self.assertGreaterEqual(self.hero._inventory.get('Health Potion', 0), 0)

    def test_buy_zero_quantity_rejected(self):
        gold_before = self.hero._inventory['Gold']
        self.store.buy_inventory_item(get_inventory_item(1), 0)
        self.assertEqual(self.hero._inventory['Gold'], gold_before)
        self.assertNotIn('Health Potion', self.hero._inventory)

    def test_sell_more_than_owned_rejected(self):
        self.hero.add_to_inventory({'Health Potion': 1})
        gold_before = self.hero._inventory['Gold']
        removed = self.hero.remove_inventory_item('Health Potion', 5)
        if removed:
            self.store.sell_inventory_item(get_inventory_item(1), 5)
        self.assertEqual(self.hero._inventory['Gold'], gold_before)
        self.assertEqual(self.hero._inventory['Health Potion'], 1)

    def test_sell_valid_quantity_pays_gold(self):
        self.hero.add_to_inventory({'Health Potion': 3})
        gold_before = self.hero._inventory['Gold']
        removed = self.hero.remove_inventory_item('Health Potion', 2)
        self.assertTrue(removed)
        self.store.sell_inventory_item(get_inventory_item(1), 2)
        self.assertEqual(self.hero._inventory['Gold'], gold_before + 6)
        self.assertEqual(self.hero._inventory['Health Potion'], 1)


class EquipmentFullTest(unittest.TestCase):
    def setUp(self):
        self.hero = fresh_hero()
        self.store = Store(self.hero._type)

    def test_buy_with_no_matching_slot_does_not_crash_or_charge(self):
        weapon = {'Test Sword': {'Health': 1, 'Energy': 1, 'Strength': 1,
                                 'Defense': 1, 'Type': 'Weapon', 'Worth': 1}}
        self.hero._equipment = [dict(weapon) for _ in range(7)]
        chestplate = {'Test Chestplate': {'Health': 1, 'Energy': 1, 'Strength': 1,
                                          'Defense': 1, 'Type': 'Chestplate', 'Worth': 1}}
        gold_before = self.hero._inventory['Gold']
        equipment_before = [dict(e) for e in self.hero._equipment]
        self.store.buy_armor_item(chestplate)
        self.assertEqual(self.hero._inventory['Gold'], gold_before)
        self.assertEqual(self.hero._equipment, equipment_before)

    def test_buy_with_matching_slot_still_works(self):
        chestplate = {'Test Chestplate': {'Health': 1, 'Energy': 1, 'Strength': 1,
                                          'Defense': 1, 'Type': 'Chestplate', 'Worth': 1}}
        gold_before = self.hero._inventory['Gold']
        self.store.buy_armor_item(chestplate)
        self.assertEqual(len(self.hero._equipment), 7)
        names = [list(e.keys())[0] for e in self.hero._equipment]
        self.assertIn('Test Chestplate', names)
        self.assertLess(self.hero._inventory['Gold'], gold_before + 100)


if __name__ == '__main__':
    unittest.main()
