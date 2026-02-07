import random
from unittest.mock import patch

import pytest

from calculator_cricket import (
    MAX_OVERS, MAX_PER_BOWLER, MAX_WICKETS, TEAM_SIZE,
    BallResult, Game, Player, Team, abbreviate_name,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_roll_fn(rolls):
    """Return a callable that yields values from *rolls* one at a time."""
    it = iter(rolls)
    return lambda: next(it)


def noop_input():
    """Stand-in for input() so tests don't block."""
    pass


def _make_game():
    """Create a Game with deterministic teams for testing."""
    random.seed(42)
    return Game("Team A", "Team B")


# ---------------------------------------------------------------------------
# Unit tests — abbreviate_name
# ---------------------------------------------------------------------------

class TestAbbreviateName:
    def test_simple(self):
        assert abbreviate_name("James Smith") == "J. Smith"

    def test_multi_part_surname(self):
        assert abbreviate_name("AB de Villiers") == "A. de Villiers"

    def test_single_char_first_name(self):
        assert abbreviate_name("K Patel") == "K. Patel"


# ---------------------------------------------------------------------------
# Unit tests — Player
# ---------------------------------------------------------------------------

class TestPlayer:
    def test_initial_state(self):
        p = Player("James Smith")
        assert p.name == "James Smith"
        assert p.runs == 0
        assert p.balls_faced == 0
        assert p.out is False
        assert p.how_out is None
        assert p.bowling_balls == 0
        assert p.runs_conceded == 0
        assert p.wickets_taken == 0

    def test_short_name(self):
        p = Player("Virat Kohli")
        assert p.short_name == "V. Kohli"


# ---------------------------------------------------------------------------
# Unit tests — Game._format_overs
# ---------------------------------------------------------------------------

class TestFormatOvers:
    def test_zero(self):
        assert Game._format_overs(0) == "0"

    def test_partial_over(self):
        assert Game._format_overs(7) == "1.1"

    def test_complete_overs(self):
        assert Game._format_overs(12) == "2"

    def test_one_over(self):
        assert Game._format_overs(6) == "1"

    def test_five_balls(self):
        assert Game._format_overs(5) == "0.5"


# ---------------------------------------------------------------------------
# Unit tests — Team
# ---------------------------------------------------------------------------

class TestTeam:
    def test_is_all_out_false(self):
        t = Team("Test")
        t.outs = 9
        assert t.is_all_out() is False

    def test_is_all_out_true(self):
        t = Team("Test")
        t.outs = 10
        assert t.is_all_out() is True

    def test_team_generation(self):
        t = Team("Test")
        assert len(t.players) == TEAM_SIZE
        names = [p.name for p in t.players]
        assert len(set(names)) == TEAM_SIZE

    def test_captain_and_keeper_assigned(self):
        t = Team("Test")
        assert t.captain in t.players
        assert t.keeper in t.players[:6]


# ---------------------------------------------------------------------------
# State logic tests — _process_ball (controlled rolls)
# ---------------------------------------------------------------------------

class TestProcessBall:
    def _setup(self):
        game = _make_game()
        team = game.team1
        bowling_team = game.team2
        bowler = bowling_team.players[5]
        return game, team, bowling_team, bowler

    def test_dot_ball(self):
        game, team, bowling_team, bowler = self._setup()
        result = game._process_ball(team, bowling_team, bowler, 0)
        assert result.desc == "Dot ball"
        assert result.runs == 0
        assert result.is_wicket is False
        assert result.is_legal is True
        assert team.runs == 0
        assert team.striker.balls_faced == 1

    @pytest.mark.parametrize("roll", [1, 2, 3, 4])
    def test_scoring_runs(self, roll):
        game, team, bowling_team, bowler = self._setup()
        result = game._process_ball(team, bowling_team, bowler, roll)
        assert result.runs == roll
        assert result.is_legal is True
        assert team.runs == roll
        assert bowler.runs_conceded == roll

    def test_six(self):
        game, team, bowling_team, bowler = self._setup()
        result = game._process_ball(team, bowling_team, bowler, 6)
        assert result.desc == "SIX!"
        assert result.runs == 6
        assert team.runs == 6
        assert team.striker.runs == 6
        assert bowler.runs_conceded == 6

    @pytest.mark.parametrize("roll", [5, 7])
    def test_dot_ball_5_7(self, roll):
        game, team, bowling_team, bowler = self._setup()
        result = game._process_ball(team, bowling_team, bowler, roll)
        assert result.desc == "Dot ball"
        assert result.runs == 0
        assert result.is_legal is True
        assert team.striker.balls_faced == 1

    def test_no_ball_wide(self):
        game, team, bowling_team, bowler = self._setup()
        result = game._process_ball(team, bowling_team, bowler, 8)
        assert result.desc == "No-ball/Wide (+1 run)"
        assert result.runs == 1
        assert result.is_legal is False
        assert team.runs == 1
        assert team.striker.balls_faced == 0  # no ball faced on extras
        assert bowler.runs_conceded == 1

    def test_wicket(self):
        game, team, bowling_team, bowler = self._setup()
        striker_before = team.striker
        result = game._process_ball(team, bowling_team, bowler, 9)
        assert result.is_wicket is True
        assert result.is_legal is True
        assert team.outs == 1
        assert striker_before.out is True
        assert bowler.wickets_taken == 1
        assert result.new_batsman is not None

    def test_strike_rotation_odd(self):
        game, team, bowling_team, bowler = self._setup()
        original_striker = team.striker_idx
        original_non_striker = team.non_striker_idx
        game._process_ball(team, bowling_team, bowler, 1)
        assert team.striker_idx == original_non_striker
        assert team.non_striker_idx == original_striker

    def test_strike_rotation_even(self):
        game, team, bowling_team, bowler = self._setup()
        original_striker = team.striker_idx
        original_non_striker = team.non_striker_idx
        game._process_ball(team, bowling_team, bowler, 2)
        assert team.striker_idx == original_striker
        assert team.non_striker_idx == original_non_striker

    def test_three_rotates_strike(self):
        game, team, bowling_team, bowler = self._setup()
        original_striker = team.striker_idx
        original_non_striker = team.non_striker_idx
        game._process_ball(team, bowling_team, bowler, 3)
        assert team.striker_idx == original_non_striker
        assert team.non_striker_idx == original_striker

    def test_four_no_rotation(self):
        game, team, bowling_team, bowler = self._setup()
        original_striker = team.striker_idx
        game._process_ball(team, bowling_team, bowler, 4)
        assert team.striker_idx == original_striker


# ---------------------------------------------------------------------------
# Dismissal description tests
# ---------------------------------------------------------------------------

class TestDismissalDescriptions:
    def _setup(self):
        game = _make_game()
        bowling_team = game.team2
        bowler = bowling_team.players[5]
        return game, bowling_team, bowler

    def test_bowled(self):
        game, bowling_team, bowler = self._setup()
        desc = game._build_dismissal_description("Bowled", bowler, bowling_team)
        assert desc == f"b {bowler.short_name}"

    def test_lbw(self):
        game, bowling_team, bowler = self._setup()
        desc = game._build_dismissal_description("LBW", bowler, bowling_team)
        assert desc == f"lbw b {bowler.short_name}"

    def test_run_out(self):
        game, bowling_team, bowler = self._setup()
        desc = game._build_dismissal_description("Run Out", bowler, bowling_team)
        assert desc == "Run Out"

    def test_hit_wicket(self):
        game, bowling_team, bowler = self._setup()
        desc = game._build_dismissal_description("Hit Wicket", bowler, bowling_team)
        assert desc == f"Hit Wicket b {bowler.short_name}"

    def test_caught(self):
        game, bowling_team, bowler = self._setup()
        desc = game._build_dismissal_description("Caught", bowler, bowling_team)
        assert desc.startswith("c ")
        assert f"b {bowler.short_name}" in desc

    def test_stumped(self):
        game, bowling_team, bowler = self._setup()
        desc = game._build_dismissal_description("Stumped", bowler, bowling_team)
        assert desc.startswith("st ")
        assert f"b {bowler.short_name}" in desc


# ---------------------------------------------------------------------------
# Integration tests — full innings with controlled rolls
# ---------------------------------------------------------------------------

class TestFullInnings:
    def test_full_innings_all_out(self, capsys):
        random.seed(42)
        game = Game("Batting XI", "Bowling XI")
        team = game.team1
        bowling_team = game.team2
        # 10 wickets: need 10 roll-9s, with dot balls between to fill overs
        # Each wicket needs a roll of 9. Intersperse with dots (5) to be safe.
        rolls = []
        for _ in range(MAX_WICKETS):
            rolls.extend([5, 5, 5, 5, 5, 9])  # 5 dots then out each "over"
        game.play_innings(team, bowling_team, roll_fn=make_roll_fn(rolls),
                          input_fn=noop_input)
        assert team.is_all_out()
        assert team.outs == MAX_WICKETS

    def test_chase_target_reached(self, capsys):
        random.seed(42)
        game = Game("Team A", "Team B")
        team = game.team1
        bowling_team = game.team2
        # Chase a target of 10: roll 4s until we reach it (3 fours = 12 >= 10)
        rolls = [4] * 20  # more than enough
        game.play_innings(team, bowling_team, target=10,
                          roll_fn=make_roll_fn(rolls), input_fn=noop_input)
        assert team.runs >= 10
        captured = capsys.readouterr()
        assert "reached the target" in captured.out

    def test_bowler_pool_always_has_eligible(self):
        # 6 bowlers × 4 overs each = 24 overs available ≥ 20 needed
        random.seed(42)
        game = Game("Team A", "Team B")
        bowling_team = game.team2
        bowlers = bowling_team.players[5:TEAM_SIZE]
        assert len(bowlers) == 6
        total_overs = len(bowlers) * MAX_PER_BOWLER
        assert total_overs >= MAX_OVERS


# ---------------------------------------------------------------------------
# Integration tests — declare_winner
# ---------------------------------------------------------------------------

class TestDeclareWinner:
    def _setup_game_with_scores(self, runs1, outs1, runs2, outs2):
        random.seed(42)
        game = Game("Team A", "Team B")
        game.batting_first = game.team1
        game.batting_second = game.team2
        game.team1.runs = runs1
        game.team1.outs = outs1
        game.team2.runs = runs2
        game.team2.outs = outs2
        return game

    def test_batting_first_wins(self, capsys):
        game = self._setup_game_with_scores(150, 10, 120, 10)
        game.declare_winner()
        captured = capsys.readouterr()
        assert "Team A wins by 30 runs!" in captured.out

    def test_batting_second_wins(self, capsys):
        game = self._setup_game_with_scores(100, 10, 101, 3)
        game.declare_winner()
        captured = capsys.readouterr()
        assert "Team B wins by 7 wickets!" in captured.out

    def test_tie(self, capsys):
        game = self._setup_game_with_scores(130, 10, 130, 10)
        game.declare_winner()
        captured = capsys.readouterr()
        assert "It's a tie!" in captured.out
