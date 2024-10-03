# Scoring Algorithm
Challenges are scored based on their difficulty level, with a multiplier awarded on some challenges for being one of the first teams to solve.

| Difficulty                 | Base Points | Multiplier Applies? |
|----------------------------|-------------|---------------------|
| 0 (example flags only)     | 100         | ❌                   |
| 1 (default if unspecified) | 500         | ✅                   |
| 2                          | 1000        | ✅                   |
| 3                          | 2500        | ✅                   |
| 4                          | 3500        | ✅                   |
| 5                          | 5000        | ✅                   |

Base points are specified [here in models/challenge.py](https://github.com/NUHack-Newcastle/ctf-platform/blob/9a73d2c124be7f9a1c2024ce9e024424af8d3a2e/models/challenge.py#L65C5-L87C36) -- you can easily modify this or implement a system you prefer in your own fork/local copy of the platform. The allow_multiplier challenge property is also defined [here](https://github.com/NUHack-Newcastle/ctf-platform/blob/9a73d2c124be7f9a1c2024ce9e024424af8d3a2e/models/challenge.py#L85), and you can disable it, change it to a more complex system, or even read per-challenge by rewriting this.

As difficulty 0 is meant only for challenges that serve as the classic "checking you know how to submit a flag" example, multipliers are not awarded for these challenges. Difficulty 0 challenges are not meant to be a test of skill, so awarding significantly more points to a team that can register and copy a string fastest isn't fair.

## Multipliers

Multipliers are specified [here in solve.py](https://github.com/NUHack-Newcastle/ctf-platform/blob/9a73d2c124be7f9a1c2024ce9e024424af8d3a2e/models/solve.py#L52), by default we use the formula `max(-0.5 * solve_position + 3, 1.0)` where `solve_position` is 1 for first, 2 for second etc. This produces the following set of multipliers.

| Solve Position | Multiplier |
|----------------|------------|
| 1st            | 2.5x       |
| 2nd            | 2.0x       |
| 3rd            | 1.5x       |
| 4th+           | 1.0x       |
