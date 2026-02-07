import random

DISMISSALS = [
    ("Caught", 57),
    ("Bowled", 20),
    ("LBW", 15),
    ("Run Out", 4),
    ("Stumped", 3),
    ("Hit Wicket", 1),
]

FIRST_NAMES = [
    "James", "Arun", "Mohammed", "Chris", "David", "Ravi", "Ben", "Sachin",
    "Steve", "Kane", "Rashid", "Tom", "Virat", "Joe", "Mitchell", "Babar",
    "Pat", "Rohit", "Ross", "Kagiso", "Jasprit", "Marnus", "Quinton",
    "Travis", "Shakib",
]

LAST_NAMES = [
    "Smith", "Kumar", "Patel", "Taylor", "Brown", "Khan", "Williamson",
    "Anderson", "Ali", "Sharma", "Root", "Stokes", "Kohli", "Warner",
    "de Villiers", "Azam", "Cummins", "Rabada", "Bumrah", "Labuschagne",
    "de Kock", "Head", "Hasan", "Green", "Mendis",
]


def abbreviate_name(full_name):
    """Format 'James Smith' as 'J. Smith'."""
    parts = full_name.split()
    return f"{parts[0][0]}. {' '.join(parts[1:])}"


class Batsman:
    def __init__(self, name):
        self.name = name
        self.runs = 0
        self.balls_faced = 0
        self.out = False
        self.how_out = None

    @property
    def short_name(self):
        return abbreviate_name(self.name)


class Team:
    def __init__(self, name):
        self.name = name
        self.runs = 0
        self.outs = 0
        self.balls = 0
        self.batsmen = self._generate_batsmen()
        self.striker_idx = 0
        self.non_striker_idx = 1
        self.next_idx = 2

    def _generate_batsmen(self):
        firsts = random.sample(FIRST_NAMES, 11)
        lasts = random.sample(LAST_NAMES, 11)
        return [Batsman(f"{f} {l}") for f, l in zip(firsts, lasts)]

    @property
    def striker(self):
        return self.batsmen[self.striker_idx]

    @property
    def non_striker(self):
        return self.batsmen[self.non_striker_idx]

    def is_all_out(self):
        return self.outs >= 10


class Game:
    def __init__(self, team1_name, team2_name):
        self.team1 = Team(team1_name)
        self.team2 = Team(team2_name)

    def play_innings(self, team, target=None):
        print(f"\n{'='*40}")
        print(f"{team.name} batting")
        if target is not None:
            print(f"Target: {target} runs")
        print(f"{'='*40}\n")

        while not team.is_all_out():
            input()
            roll = random.randint(0, 9)
            team.balls += 1

            display_name = team.striker.short_name

            if roll in (0, 1, 2, 3, 4):
                team.runs += roll
                team.striker.runs += roll
                team.striker.balls_faced += 1
                if roll == 0:
                    desc = "Dot ball"
                else:
                    desc = f"{roll} run{'s' if roll > 1 else ''}"
                    if roll in (1, 3):
                        team.striker_idx, team.non_striker_idx = (
                            team.non_striker_idx, team.striker_idx)
            elif roll == 6:
                team.runs += 6
                team.striker.runs += 6
                team.striker.balls_faced += 1
                desc = "SIX!"
            elif roll in (5, 7):
                team.striker.balls_faced += 1
                desc = "Dot ball"
            elif roll == 8:
                team.runs += 1
                team.striker.runs += 1
                desc = "No-ball/Wide (+1 run)"
            elif roll == 9:
                team.outs += 1
                team.striker.balls_faced += 1
                types, weights = zip(*DISMISSALS)
                how = random.choices(types, weights=weights)[0]
                team.striker.out = True
                team.striker.how_out = how
                desc = f"OUT! ({how})"
                if team.next_idx < len(team.batsmen):
                    team.striker_idx = team.next_idx
                    team.next_idx += 1

            print(f"Ball {team.balls}: [{roll}] {desc} "
                  f"({display_name}*)  |  "
                  f"Score: {team.runs}/{team.outs}")

            if target is not None and team.runs >= target:
                print(f"\n{team.name} reached the target!")
                break

        if team.is_all_out():
            print(f"\n{team.name} all out!")

        print(f"\n{team.name} final score: {team.runs}/{team.outs} "
              f"({team.balls} balls)")

        self._print_scorecard(team)

    def _print_scorecard(self, team):
        print(f"\n--- Scorecard ---")
        for b in team.batsmen:
            if b.out:
                print(f"  {b.short_name:<18} {b.how_out:<12} "
                      f"{b.runs}  ({b.balls_faced} balls)")
            elif b.balls_faced > 0:
                print(f"  {b.short_name:<18} {'not out':<12} "
                      f"{b.runs}* ({b.balls_faced} balls)")
            else:
                print(f"  {b.short_name:<18} did not bat")

        top3 = sorted(team.batsmen, key=lambda b: b.runs, reverse=True)[:3]
        print(f"\n--- Top 3 ---")
        for i, b in enumerate(top3, 1):
            star = "" if b.out else "*"
            print(f"  {i}. {b.short_name}   {b.runs}{star}")

    def declare_winner(self):
        print(f"\n{'='*40}")
        print("RESULT")
        print(f"{'='*40}")
        print(f"{self.team1.name}: {self.team1.runs}/{self.team1.outs}")
        print(f"{self.team2.name}: {self.team2.runs}/{self.team2.outs}")
        print()

        if self.team1.runs > self.team2.runs:
            diff = self.team1.runs - self.team2.runs
            print(f"{self.team1.name} wins by {diff} runs!")
        elif self.team2.runs > self.team1.runs:
            wickets = 10 - self.team2.outs
            print(f"{self.team2.name} wins by {wickets} wickets!")
        else:
            print("It's a tie!")

        print(f"\n--- Top Scorers ---")
        for team in (self.team1, self.team2):
            print(f"{team.name}:")
            top3 = sorted(team.batsmen, key=lambda b: b.runs, reverse=True)[:3]
            for i, b in enumerate(top3, 1):
                star = "" if b.out else "*"
                print(f"  {i}. {b.short_name}   {b.runs}{star}")

    def play(self):
        self.play_innings(self.team1)
        target = self.team1.runs + 1
        self.play_innings(self.team2, target=target)
        self.declare_winner()


def main():
    print("Calculator Cricket")
    print("==================\n")

    name1 = input("Enter Team 1 name (default: Team 1): ").strip()
    name2 = input("Enter Team 2 name (default: Team 2): ").strip()

    if not name1:
        name1 = "Team 1"
    if not name2:
        name2 = "Team 2"

    game = Game(name1, name2)
    game.play()


if __name__ == "__main__":
    main()
