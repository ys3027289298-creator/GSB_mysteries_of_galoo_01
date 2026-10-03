import unittest

from map_creator import create_dungeon


class DuplicateRoomTest(unittest.TestCase):
    def test_each_map_gets_independent_grid(self):
        grids = [create_dungeon() for _ in range(30)]
        self.assertEqual(len({id(g) for g in grids}), len(grids))
        first_row_ids = {id(row) for row in grids[0]}
        for grid in grids[1:]:
            self.assertFalse(first_row_ids & {id(row) for row in grid})

    def test_mutating_one_map_does_not_leak_to_others(self):
        grids = [create_dungeon() for _ in range(30)]
        grids[0][0][0] = 'MUTATED  '
        for grid in grids[1:]:
            self.assertNotEqual(grid[0][0], 'MUTATED  ')


if __name__ == '__main__':
    unittest.main()
