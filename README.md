# Mysteries-of-Galoo
Text-Based RPG written in Python 3

See Wiki for more information

## Save / reload compatibility

- Saves are written as a versioned pickle envelope (`save.SAVE_VERSION`,
  currently 2). A playthrough writes two files (`save_file.pkl` for the
  character, `solar_system.pkl` for the map/world progress) sharing one
  `save_id`, so a pair from different playthroughs can never be reloaded
  together.
- Writes are atomic (temp file + replace); a crash while saving cannot leave
  a truncated file in place.
- `reload_object` / `load_game` accept version 2 saves and legacy version 1
  saves (the old raw pickled objects with no envelope). Two legacy files can
  still be reloaded as a pair, but pairing cannot be verified for them;
  mixing a version 1 file with a version 2 file is rejected.
- Saves tagged with any other version raise `save.SaveVersionError`.
- Corrupt or truncated files raise `save.SaveCorruptError` instead of
  crashing; a mismatched character/map pair raises `save.SaveMismatchError`.
  All of those inherit from `save.SaveError`, which the continue-game flow
  handles by returning to the menu.
- Compatibility boundary: `reload_object` / `load_game` only read the current
  version and legacy version 1. Older/newer format versions are never
  migrated implicitly, and an object's class must still exist in the code
  modules (standard pickle requirement).
