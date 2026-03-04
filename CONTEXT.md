# Project Context: daka

## Purpose
`daka` is a simple CLI tracker for daily check-ins on New Year resolutions.

Core UX:
- Numeric input selects an existing resolution/item.
- Non-numeric text input creates a new resolution/item.
- Empty input returns to previous menu.
- `q` exits immediately from any prompt.

## Package Layout
- `src/daka/cli.py`: CLI entrypoint (`argparse`), parses `-d/--date`, calls handler.
- `src/daka/handler.py`: interactive flow and business logic.
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
1. `cli.main()` parses date (default: today).
2. `handler.run(date)` loads merged data from `data_loader.load_data()`.
3. User navigates resolution menu, then item menu.
4. Adds are persisted to `resolutions.json`.
5. Successful check-ins are persisted to `data.csv`.

## Important Behaviors
- Exact `q`/`Q` means quit.
- Words starting with `q` (e.g. `question`) are treated as normal text input.
- Duplicate check-in on same item/date is rejected.

## Tests
- Test files:
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
```
