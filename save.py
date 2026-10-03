import os
import pickle
import uuid

SAVE_VERSION = 2

CHARACTER_FILE = 'save_file.pkl'
SOLAR_SYSTEM_FILE = 'solar_system.pkl'

_LEGACY_VERSION = 1
_ENVELOPE_MARKER = 'galoo_save'


class SaveError(Exception):
    pass


class SaveCorruptError(SaveError):
    pass


class SaveVersionError(SaveError):
    pass


class SaveMismatchError(SaveError):
    pass


def _envelope(obj, save_id):
    return {_ENVELOPE_MARKER: True,
            'version': SAVE_VERSION,
            'save_id': save_id,
            'payload': obj}


def save_object(obj, filename, save_id=None):
    if save_id is None:
        save_id = uuid.uuid4().hex
    tmp_filename = filename + '.tmp'
    with open(tmp_filename, 'wb') as output:
        pickle.dump(_envelope(obj, save_id), output, pickle.HIGHEST_PROTOCOL)
    os.replace(tmp_filename, filename)
    return save_id


def save_game(character, solar_system,
              character_file=CHARACTER_FILE,
              solar_system_file=SOLAR_SYSTEM_FILE):
    save_id = uuid.uuid4().hex
    save_object(character, character_file, save_id)
    save_object(solar_system, solar_system_file, save_id)
    return save_id


def _read_envelope(filename):
    try:
        with open(filename, 'rb') as source:
            loaded = pickle.load(source)
    except FileNotFoundError:
        raise
    except (pickle.UnpicklingError, EOFError, ValueError,
            AttributeError, ImportError, IndexError) as exc:
        raise SaveCorruptError(filename) from exc

    if isinstance(loaded, dict) and loaded.get(_ENVELOPE_MARKER) is True:
        return loaded
    # legacy v1 save: a raw pickled object with no version envelope
    return {'version': _LEGACY_VERSION, 'save_id': None, 'payload': loaded}


def inspect_save(filename):
    envelope = _read_envelope(filename)
    return {'version': envelope['version'], 'save_id': envelope.get('save_id')}


def reload_object(filename):
    envelope = _read_envelope(filename)
    if envelope['version'] != SAVE_VERSION and envelope['version'] != _LEGACY_VERSION:
        raise SaveVersionError(
            'save version %s is not supported (expected %s)'
            % (envelope['version'], SAVE_VERSION))
    return envelope['payload']


def load_game(character_file=CHARACTER_FILE,
              solar_system_file=SOLAR_SYSTEM_FILE):
    character_envelope = _read_envelope(character_file)
    solar_envelope = _read_envelope(solar_system_file)

    for envelope in (character_envelope, solar_envelope):
        if envelope['version'] != SAVE_VERSION and envelope['version'] != _LEGACY_VERSION:
            raise SaveVersionError(
                'save version %s is not supported (expected %s)'
                % (envelope['version'], SAVE_VERSION))

    # v2 saves are paired by save_id; legacy v1 saves carry no id and cannot
    # be cross-checked, so mixing a v1 file with a v2 file is rejected.
    if character_envelope['version'] == SAVE_VERSION or solar_envelope['version'] == SAVE_VERSION:
        if character_envelope.get('save_id') != solar_envelope.get('save_id'):
            raise SaveMismatchError(
                'character and map saves do not belong to the same playthrough')

    return character_envelope['payload'], solar_envelope['payload']
