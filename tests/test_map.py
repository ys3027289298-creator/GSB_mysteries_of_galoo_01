import unittest

import map_creator


def signature(grid):
    return tuple(tuple(row) for row in grid)


class TestMapGeneration(unittest.TestCase):
    def test_world_maps_have_unique_layouts(self):
        for world in map_creator.solar_system:
            seen = set()
            for row in world:
                for game_map in row:
                    sig = signature(game_map._grid)
                    self.assertNotIn(sig, seen, 'duplicate room layout in world')
                    seen.add(sig)

    def test_create_unique_dungeon_never_repeats(self):
        used = set()
        for _ in range(25):
            grid = map_creator.create_unique_dungeon(used)
            self.assertNotIn(signature(grid), used)
            used.add(signature(grid))

    def test_generated_rooms_are_reachable(self):
        used = set()
        for _ in range(25):
            grid = map_creator.create_unique_dungeon(used)
            used.add(signature(grid))
            rooms = {(r, c) for r in range(5) for c in range(5)
                     if grid[r][c] == map_creator.room}
            self.assertTrue(rooms, 'map must contain dungeons')
            connected = set()
            frontier = [(2, 2)]
            while frontier:
                r, c = frontier.pop()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cell = (r + dr, c + dc)
                    if cell in rooms and cell not in connected:
                        connected.add(cell)
                        frontier.append(cell)
            self.assertEqual(rooms, connected, 'dungeons must be reachable')


if __name__ == '__main__':
    unittest.main()
