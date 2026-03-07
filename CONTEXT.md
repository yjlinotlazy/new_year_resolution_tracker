# Project Context: daka

## Purpose
`daka` is a simple CLI tracker for daily check-ins on New Year resolutions.

Core UX:
- Numeric input selects an existing resolution/task.
- Non-numeric text input creates a new resolution/task.
- Empty input returns to previous menu.
- `q` exits immediately from any prompt.
- Resolution names are color-coded in interactive, log, and summary views when stdout is a TTY.

## Package Layout
- `src/daka/cli.py`: CLI entrypoint (`argparse`), handles mode flags and dispatch.
- `src/daka/handler.py`: interactive check-in flow and rename flow.
- `src/daka/analytic_handler.py`: log/analytics output (`daka -l/--log`, `daka -s/--summary`).
- `src/daka/color_config.py`: shared ANSI color palette constants.
- `src/daka/data_loader.py`: persistence layer (read/write files under `~/.config/daka`).

## Runtime Data Location
Data is stored in:
- `~/.config/daka/resolutions.json`
  - Stores resolution and task definitions.
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
   - `-l/--log` -> `analytic_handler.summarize_all_checkins()` then exit.
   - `-s/--summary` -> `analytic_handler.summarize_completion()` then exit.
     - Output has two sections: `Yearly Summary` and `Weekly Summary`.
     - Each task line includes ratio + percent + ASCII completion bar.
   - `--rename` -> `handler.rename_entities()` then exit.
   - default/check-in mode -> parse `-d/--date` (default today), then `handler.run(date)`.
3. In check-in mode, user navigates resolution menu -> task menu.
4. Adds are persisted to `resolutions.json`.
5. Successful check-ins are persisted to `data.csv`, and CLI exits immediately.
6. In rename mode, renaming resolution/task updates both `resolutions.json` and `data.csv`.

## Important Behaviors
- Exact `q`/`Q` means quit.
- Words starting with `q` (e.g. `question`) are treated as normal text input.
- Duplicate check-in on same task/date is rejected.
- Summary percentages are based on current year only.
  - Day: `checkin_days_in_year / days_in_year`
  - Week: `weeks_with_at_least_one_checkin / weeks_in_year`, where `weeks_in_year = ceil(days_in_year / 7)`.
- Rename mode validates non-empty names and prevents duplicate names in the same scope.
- Color output is disabled when `NO_COLOR` is set, `TERM=dumb`, or stdout is not a TTY.
- Summary alignment uses terminal display width (CJK-aware) and ignores ANSI escape sequences when padding.

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
daka -l
daka --log
daka -s
daka --summary
daka --rename
```
