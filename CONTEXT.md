# Project Context: daka

## Purpose
`daka` is a simple CLI tracker for daily check-ins on New Year resolutions.

Core UX:
- Numeric input selects an existing resolution/item.
- Non-numeric text input creates a new resolution/item.
- Empty input returns to previous menu.
- `q` exits immediately from any prompt.
- Resolution names are color-coded in interactive and summary views when stdout is a TTY.

## Package Layout
- `src/daka/cli.py`: CLI entrypoint (`argparse`), handles mode flags and dispatch.
- `src/daka/handler.py`: interactive check-in flow and rename flow.
- `src/daka/analytic_handler.py`: summary/analytics output (`daka -s`).
- `src/daka/color_config.py`: shared ANSI color palette constants.
- `src/daka/data_loader.py`: persistence layer (read/write files under `~/.config/daka`).

## Runtime Data Location
Data is stored in:
- `~/.config/daka/resolutions.json`
  - Stores resolution and item definitions.
- `~/.config/daka/data.csv`
  - Stores check-in records as rows: `resolution,item,date`.

## Data Model (in-memory)
```python
{
  "resolutions": [
    {
      "name": str,
      "items": [
        {
          "name": str,
          "checkins": ["YYYY-MM-DD", ...]
        }
      ]
    }
  ]
}
```

## Execution Flow
1. `cli.main()` parses flags/options.
2. Mode dispatch:
   - `-s/--summary` -> `analytic_handler.summarize_all_checkins()` then exit.
   - `--rename` -> `handler.rename_entities()` then exit.
   - default/check-in mode -> parse `-d/--date` (default today), then `handler.run(date)`.
3. In check-in mode, user navigates resolution menu -> item menu.
4. Adds are persisted to `resolutions.json`.
5. Successful check-ins are persisted to `data.csv`.
6. In rename mode, renaming resolution/item updates both `resolutions.json` and `data.csv`.

## Important Behaviors
- Exact `q`/`Q` means quit.
- Words starting with `q` (e.g. `question`) are treated as normal text input.
- Duplicate check-in on same item/date is rejected.
- Rename mode validates non-empty names and prevents duplicate names in the same scope.
- Color output is disabled when `NO_COLOR` is set, `TERM=dumb`, or stdout is not a TTY.

## Tests
- Test files:
  - `tests/test_cli.py`
  - `tests/test_analytic_handler.py`
  - `tests/test_handler.py`
  - `tests/test_data_loader.py`
- Run tests:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Installation / Run
```bash
python -m pip install -e . --user
daka -d 2026-03-04
daka -s
daka --rename
```
