# Kandu! Entertainment est. 6/30/2018
# Save/load module for Mysteries of Galoo.
#
# Save / reload compatibility boundary
# ------------------------------------
# SAVE_VERSION 2 (current): objects are wrapped in a versioned envelope
#   {'version': 2, 'payload': ...} and a full game is written as one atomic
#   bundle file (character + solar system together) via save_game/load_game,
#   so the two modules can never be reloaded out of sync.
# SAVE_VERSION 1 (legacy): raw pickle streams, originally split between
#   save_file.pkl (character) and solar_system.pkl (map). Both are still
#   readable by reload_object/load_game for backward compatibility, but v1
#   saves carry no version check and no atomicity guarantee: if one of the
#   two files was truncated or written from an older session, the game may
#   load with mismatched character/map state.
# Forward saves (version > SAVE_VERSION) are rejected with SaveVersionError;
# unreadable or structurally invalid files raise SaveCorruptError instead of
# letting pickle crash the game.

import os
import pickle


CHARACTER_FILE = 'save_file.pkl'
SOLAR_SYSTEM_FILE = 'solar_system.pkl'

SAVE_VERSION = 2
LEGACY_VERSION = 1

_VERSION_KEY = 'version'
_PAYLOAD_KEY = 'payload'


class SaveError(Exception):
    pass


class SaveCorruptError(SaveError):
    pass


class SaveVersionError(SaveError):
    pass


def _envelope(payload, version=SAVE_VERSION):
    return {_VERSION_KEY: version, _PAYLOAD_KEY: payload}


def _write_atomic(obj, filename):
    temporary = filename + '.tmp'
    with open(temporary, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
    os.replace(temporary, filename)


def save_object(obj, filename):
    _write_atomic(_envelope(obj), filename)


def save_game(character, solar_system, filename=CHARACTER_FILE):
    payload = {'character': character, 'solar_system': solar_system}
    _write_atomic(_envelope(payload), filename)


def _read(filename):
    try:
        with open(filename, 'rb') as source:
            return pickle.load(source)
    except (OSError, EOFError, pickle.PickleError, AttributeError, ValueError,
            TypeError, ImportError, IndexError, KeyError) as exc:
        raise SaveCorruptError('Save file "%s" is unreadable: %s'
                               % (filename, exc)) from exc


def _unwrap(data):
    if isinstance(data, dict) and _VERSION_KEY in data and _PAYLOAD_KEY in data:
        version = data[_VERSION_KEY]
        if not isinstance(version, int) or isinstance(version, bool):
            raise SaveCorruptError('Save file has an invalid version marker')
        if version > SAVE_VERSION:
            raise SaveVersionError(
                'Save file version %s is newer than supported version %s'
                % (version, SAVE_VERSION))
        return data[_PAYLOAD_KEY], version
    return data, LEGACY_VERSION


def reload_object(filename):
    payload, _ = _unwrap(_read(filename))
    return payload


def load_game(filename=CHARACTER_FILE):
    payload, version = _unwrap(_read(filename))
    if isinstance(payload, dict) and 'character' in payload \
            and 'solar_system' in payload:
        return payload['character'], payload['solar_system']
    if version < SAVE_VERSION:
        legacy_map = os.path.join(os.path.dirname(filename), SOLAR_SYSTEM_FILE)
        solar_system = reload_object(legacy_map)
        return payload, solar_system
    raise SaveCorruptError('Save file "%s" is missing character or map data'
                           % filename)
