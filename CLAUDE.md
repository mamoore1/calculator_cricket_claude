# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Calculator Cricket — a T20 cricket simulation game in Python. Players press keys to "bowl" deliveries (each generates a random 0–9 digit, like the old calculator trick). There are two interfaces: a terminal/CLI version and a PyGame GUI.

## Commands

```bash
# Run the CLI game (interactive, requires terminal input)
python calculator_cricket.py

# Run the PyGame GUI (optional team name args)
python calculator_cricket_gui.py [team1_name] [team2_name]

# Run tests
python -m pytest test_calculator_cricket.py -v

# Run a single test class or method
python -m pytest test_calculator_cricket.py::TestProcessBall -v
python -m pytest test_calculator_cricket.py::TestProcessBall::test_dot_ball -v
```

Uses a venv at `./venv` with Python 3.11. Only external dependency is `pygame` (for the GUI only).

## Architecture

Three source files, no package structure:

- **`calculator_cricket.py`** — Core game engine. Contains `Player`, `Team`, and `Game` classes. `Game._process_ball(team, bowling_team, bowler, roll)` is the central simulation method that maps a digit (0–9) to a cricket outcome (runs, wicket, no-ball, dot). The CLI entry point (`main()`) handles coin toss and two innings interactively via `input()`.

- **`calculator_cricket_gui.py`** — PyGame frontend. `CricketGUI` wraps a `Game` instance and drives it ball-by-ball through a `GamePhase` state machine (TOSS_CALL → TOSS_RESULT → TOSS_CHOICE → INNINGS_READY → WAITING_FOR_BALL → OVER_COMPLETE → INNINGS_COMPLETE → MATCH_RESULT). It calls `Game._process_ball()` directly rather than `play_innings()`, managing overs/bowlers/strike-rotation itself. Draws scorecard, wagon wheel, over visualization, and batsman panel.

- **`test_calculator_cricket.py`** — pytest tests for the core engine only (no GUI tests). Uses `random.seed(42)` for deterministic team generation and `make_roll_fn()` / `noop_input()` helpers to control game flow. Tests cover `_process_ball` for each roll value, dismissal descriptions, strike rotation, full innings, and `declare_winner`.

## Key Design Details

- Roll mapping in `_process_ball`: 0=dot, 1–4=that many runs, 5/7=dot (balls faced but 0 runs), 6=six, 8=no-ball/wide (illegal delivery, +1 run), 9=wicket.
- T20 format constants: `MAX_OVERS=20`, `MAX_PER_BOWLER=4`, `TEAM_SIZE=11`, `MAX_WICKETS=10`.
- Bowlers are players at indices 5–10. Bowler selection avoids the previous over's bowler and respects the 4-over cap.
- The GUI duplicates some innings management logic (over counting, strike swapping, bowler selection) because it steps through deliveries one at a time rather than calling `play_innings()`.
