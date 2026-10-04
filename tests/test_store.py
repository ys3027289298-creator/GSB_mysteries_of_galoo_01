import unittest

import setup
from game_items import get_inventory_item
from store import Store
from tests.helpers import make_character, make_equipment_item


class TestStoreInventory(unittest.TestCase):
    def setUp(self):
        setup.starting_character = make_character()
        setup.starting_character.add_to_inventory({'Gold': 100, 'Health Potion': 2})
        self.store = Store('Gorilla')

    def gold(self):
        return setup.starting_character._inventory['Gold']

    def test_cannot_buy_negative_quantity(self):
        self.store.buy_inventory_item(get_inventory_item(1), -5)
        self.assertEqual(self.gold(), 100)
        self.assertNotIn('Energy Potion', setup.starting_character._inventory)

    def test_cannot_buy_more_than_store_stock(self):
        stock = self.store._stock['Health Potion']
        self.store.buy_inventory_item(get_inventory_item(1), stock + 1)
        self.assertEqual(self.gold(), 100)
        self.assertEqual(setup.starting_character._inventory['Health Potion'], 2)
        self.assertEqual(self.store._stock['Health Potion'], stock)

    def test_stock_never_goes_negative(self):
        stock = self.store._stock['Health Potion']
        self.store.buy_inventory_item(get_inventory_item(1), stock)
        self.assertEqual(self.store._stock['Health Potion'], 0)
        self.store.buy_inventory_item(get_inventory_item(1), 1)
        self.assertEqual(self.store._stock['Health Potion'], 0)
        self.assertEqual(self.gold(), 100 - stock * 3)

    def test_cannot_sell_more_than_owned(self):
        result = self.store.sell_inventory_item(get_inventory_item(1), 5)
        self.assertFalse(result)
        self.assertEqual(setup.starting_character._inventory['Health Potion'], 2)
        self.assertEqual(self.gold(), 100)

    def test_cannot_sell_negative_quantity(self):
        result = self.store.sell_inventory_item(get_inventory_item(1), -3)
        self.assertFalse(result)
        self.assertEqual(self.gold(), 100)

    def test_sell_moves_stock_back_to_store(self):
        self.assertTrue(self.store.sell_inventory_item(get_inventory_item(1), 2))
        self.assertNotIn('Health Potion', setup.starting_character._inventory)
        self.assertEqual(self.gold(), 100 + 2 * 3)


class TestEquipmentSlots(unittest.TestCase):
    def setUp(self):
        setup.starting_character = make_character()
        setup.starting_character.add_to_inventory({'Gold': 1000})
        self.hero = setup.starting_character
        for index in range(7):
            self.assertTrue(self.hero.equip(make_equipment_item(
                'Chestplate %d' % index, 'Chestplate'), index))
        self.store = Store('Gorilla')

    def test_equip_adds_exactly_one_item(self):
        hero = make_character()
        hero.equip(make_equipment_item('Sword', 'Weapon'), 0)
        self.assertEqual(len(hero._equipment), 1)

    def test_eighth_item_rejected_when_slots_full(self):
        self.assertEqual(len(self.hero._equipment), 7)
        result = self.hero.equip(make_equipment_item('Extra', 'Weapon'), 7)
        self.assertFalse(result)
        self.assertEqual(len(self.hero._equipment), 7)

    def test_buy_with_full_equipment_and_no_matching_slot(self):
        item = {'Shiny Sword': {'Health': 1, 'Energy': 1, 'Strength': 1,
                                'Defense': 1, 'Type': 'Weapon', 'Worth': 5}}
        result = self.store.buy_armor_item(item)
        self.assertFalse(result)
        self.assertEqual(self.hero._inventory['Gold'], 1000)
        self.assertEqual(len(self.hero._equipment), 7)


if __name__ == '__main__':
    unittest.main()
