# Calculator Cricket

A simple cricket simulation game using random number generation.

## Game Rules
- Generate random numbers 0-9 for each ball
- 0-4, 6 = runs scored
- 5, 7 = nothing (dot ball)
- 8 = no-ball/wide (1 run, no out possible)
- 9 = out
- Each team bats until 10 outs
- Team with most runs wins

## Implementation
- CLI-based game
- Two teams play in turn
- Display ball-by-ball results
- Show running total and outs
- Declare winner at end

## Files
- `calculator_cricket.py` - main game logic
- Team and Game classes
- Simple random.randint(0,9) for generation
