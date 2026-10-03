import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import setup
import game
from armory import get_weapon, get_armor, get_amulet


def fresh_hero(name='TestHero', classtype='Gorilla'):
    import character
    setup.init()
    hero_cls = getattr(character, classtype)
    hero = hero_cls(game.dusty_hero, name)
    setup.starting_character = hero
    setup.armor_locator = 0
    hero.equip(get_weapon(hero._type), 0)
    for slot in range(1, 6):
        hero.equip(get_armor(hero._type), slot)
    hero.equip(get_amulet(hero._type), 6)
    hero.add_to_inventory({'Gold': 100})
    for slot in range(7):
        setattr(setup, 'new_equipment_%d' % (slot + 1), hero._equipment[slot])
    return hero
