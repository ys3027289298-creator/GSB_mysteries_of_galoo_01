import unittest

from helpers import fresh_hero


class RemoveInventoryItemTest(unittest.TestCase):
    def setUp(self):
        self.hero = fresh_hero()
        self.hero.add_to_inventory({'Health Potion': 3})

    def test_remove_more_than_owned_fails_without_negative(self):
        self.assertFalse(self.hero.remove_inventory_item('Health Potion', 5))
        self.assertEqual(self.hero._inventory['Health Potion'], 3)

    def test_remove_negative_quantity_fails(self):
        self.assertFalse(self.hero.remove_inventory_item('Health Potion', -2))
        self.assertEqual(self.hero._inventory['Health Potion'], 3)

    def test_remove_missing_item_fails(self):
        self.assertFalse(self.hero.remove_inventory_item('Diamond', 1))

    def test_remove_partial_quantity(self):
        self.assertTrue(self.hero.remove_inventory_item('Health Potion', 2))
        self.assertEqual(self.hero._inventory['Health Potion'], 1)

    def test_remove_exact_quantity_deletes_entry(self):
        self.assertTrue(self.hero.remove_inventory_item('Health Potion', 3))
        self.assertNotIn('Health Potion', self.hero._inventory)


if __name__ == '__main__':
    unittest.main()
