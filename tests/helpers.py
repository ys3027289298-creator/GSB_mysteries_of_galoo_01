import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

ATTRS = {'Health': 100, 'Energy': 50, 'Strength': 5, 'Defense': 5}


def make_character(name='Testy'):
    from character import Gorilla
    return Gorilla(dict(ATTRS), name)


def make_equipment_item(name, item_type, worth=5):
    return {name: {'Health': 1, 'Energy': 1, 'Strength': 1, 'Defense': 1,
                   'Type': item_type, 'Worth': worth}}
