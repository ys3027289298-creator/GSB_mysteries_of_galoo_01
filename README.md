# Mysteries-of-Galoo
Text-Based RPG written in Python 3

See Wiki for more information

## Save / Reload Compatibility

- **v2 (current):** saves are versioned pickle envelopes
  `{'version': 2, 'payload': ...}`. A game save writes the character and the
  solar system (map/quest state) together in one atomic bundle
  (`save.save_game` / `save.load_game`, file `save_file.pkl`). The file is
  written to a temp file and swapped into place, and a damaged or truncated
  bundle is rejected as a whole (`save.SaveCorruptError`), so character and
  map state can never be reloaded out of sync. Saves marked with a newer
  version are rejected with `save.SaveVersionError`.
- **v1 (legacy):** older saves are raw pickle streams split between
  `save_file.pkl` (character) and `solar_system.pkl` (map). They are still
  loaded for backward compatibility, but carry no version check and no
  atomicity guarantee; if the two files come from different sessions the
  character and map state may disagree. Re-saving such a game upgrades it to
  v2.
- Individual objects still use `save.save_object` / `save.reload_object`,
  which accept both envelopes and raw v1 pickles.

## Tests

Run the test suite with:

```
python3 -m unittest discover -s tests
```

Tests cover pickle serialization round-trips, corrupt/version-mismatched
save recovery, unique and reachable map generation, store stock and gold
invariants, equipment slot limits, single-grant combat loot, and
cross-module character/map state synchronization after reload.
