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
    "de Kock", "Head", "Hasan", "Green", "Mendis", "Perera", "Marsh",
    "Amla", "Dhawan", "Buttler", "Archer", "Boult", "Holder", "Nair",
    "Maxwell", "Starc", "Lyon", "Broad", "Bairstow", "Woakes", "Wood",
    "Rahul", "Jadeja", "Ashwin", "Shami", "Yadav", "Rizwan", "Shaheen",
    "Fakhar", "Imam", "Latham", "Nicholls", "Conway", "Jamieson", "Wagner",
    "Southee", "Bavuma", "Markram", "Ngidi", "Nortje", "Maharaj", "Karunaratne",
    "Mathews", "Chandimal", "Fernando", "Lakmal", "Mushfiqur", "Tamim",
    "Mehidy", "Mustafizur", "Liton", "Hope", "Pooran", "Joseph", "Chase",
    "Hetmyer", "Thomas", "Powell", "Singh", "Carey", "Inglis", "Khawaja",
    "Harris", "Hazlewood", "Crawley", "Pope", "Foakes", "Robinson", "Potts",
    "Gill", "Iyer", "Pant", "Siraj", "Thakur", "Afridi", "Masood", "Nawaz",
    "Phillips", "Mitchell", "Santner",
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
        # Bowling stats
        self.bowling_balls = 0
        self.runs_conceded = 0
        self.wickets_taken = 0

    @property
    def short_name(self):
        return abbreviate_name(self.name)


class Team:
    def __init__(self, name):
        self.name = name
        self.runs = 0
        self.outs = 0
        self.balls = 0
        self.legal_balls = 0
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

    def play_innings(self, team, bowling_team, target=None):
        print(f"\n{'='*40}")
        print(f"{team.name} batting")
        if target is not None:
            print(f"Target: {target} runs")
        print(f"{'='*40}\n")

        print(f"Opening batsmen: {team.striker.short_name} & "
              f"{team.non_striker.short_name}\n")

        max_overs = 20
        max_per_bowler = 4
        bowlers = bowling_team.batsmen[6:11]
        over_number = 1
        target_reached = False
        last_bowler = None

        while not team.is_all_out() and not target_reached and over_number <= max_overs:
            eligible = [b for b in bowlers
                        if b.bowling_balls < max_per_bowler * 6 and b is not last_bowler]
            bowler = random.choice(eligible)
            last_bowler = bowler
            print(f"--- Over {over_number}: {bowler.short_name} bowling ---")

            balls_this_over = 0
            while balls_this_over < 6 and not team.is_all_out():
                input()
                roll = random.randint(0, 9)
                team.balls += 1

                display_name = team.striker.short_name

                if roll in (0, 1, 2, 3, 4):
                    team.runs += roll
                    team.striker.runs += roll
                    team.striker.balls_faced += 1
                    bowler.runs_conceded += roll
                    bowler.bowling_balls += 1
                    team.legal_balls += 1
                    balls_this_over += 1
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
                    bowler.runs_conceded += 6
                    bowler.bowling_balls += 1
                    team.legal_balls += 1
                    balls_this_over += 1
                    desc = "SIX!"
                elif roll in (5, 7):
                    team.striker.balls_faced += 1
                    bowler.bowling_balls += 1
                    team.legal_balls += 1
                    balls_this_over += 1
                    desc = "Dot ball"
                elif roll == 8:
                    team.runs += 1
                    team.striker.runs += 1
                    bowler.runs_conceded += 1
                    desc = "No-ball/Wide (+1 run)"
                elif roll == 9:
                    team.outs += 1
                    team.striker.balls_faced += 1
                    bowler.bowling_balls += 1
                    bowler.wickets_taken += 1
                    team.legal_balls += 1
                    balls_this_over += 1
                    types, weights = zip(*DISMISSALS)
                    how = random.choices(types, weights=weights)[0]
                    team.striker.out = True
                    team.striker.how_out = how
                    desc = f"OUT! ({how})"
                    if team.next_idx < len(team.batsmen):
                        team.striker_idx = team.next_idx
                        team.next_idx += 1
                        new_batsman = team.striker.short_name
                    else:
                        new_batsman = None

                ball_display = f"{over_number}.{balls_this_over}"
                print(f"{ball_display}: [{roll}] {desc} "
                      f"({display_name}*)  |  "
                      f"Score: {team.runs}/{team.outs}")

                if roll == 9 and not team.is_all_out():
                    print(f"  New batsman: {new_batsman}")

                if target is not None and team.runs >= target:
                    print(f"\n{team.name} reached the target!")
                    target_reached = True
                    break

            # End of over: swap strike
            if not target_reached and not team.is_all_out():
                team.striker_idx, team.non_striker_idx = (
                    team.non_striker_idx, team.striker_idx)

            over_number += 1

        if team.is_all_out():
            print(f"\n{team.name} all out!")
        elif not target_reached:
            print(f"\n{team.name} innings complete ({max_overs} overs)")

        overs_display = self._format_overs(team.legal_balls)
        print(f"\n{team.name} final score: {team.runs}/{team.outs} "
              f"({overs_display} overs)")

        self._print_scorecard(team, bowling_team)

    @staticmethod
    def _format_overs(legal_balls):
        overs = legal_balls // 6
        remaining = legal_balls % 6
        if remaining == 0:
            return str(overs)
        return f"{overs}.{remaining}"

    def _print_scorecard(self, team, bowling_team):
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

        active_bowlers = [b for b in bowling_team.batsmen if b.bowling_balls > 0]
        active_bowlers.sort(key=lambda b: (-b.wickets_taken, b.runs_conceded))
        print(f"\n--- Bowling ---")
        for b in active_bowlers:
            overs_display = self._format_overs(b.bowling_balls)
            print(f"  {b.short_name:<18} {overs_display:<6} "
                  f"{b.wickets_taken}/{b.runs_conceded}")

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

        print(f"\n--- Top Bowlers ---")
        for team, bowling_team in ((self.team1, self.team2),
                                   (self.team2, self.team1)):
            print(f"{bowling_team.name} (bowling vs {team.name}):")
            active = [b for b in bowling_team.batsmen if b.bowling_balls > 0]
            top3 = sorted(active, key=lambda b: (-b.wickets_taken, b.runs_conceded))[:3]
            for i, b in enumerate(top3, 1):
                overs = self._format_overs(b.bowling_balls)
                print(f"  {i}. {b.short_name}   {b.wickets_taken}/{b.runs_conceded} ({overs} ov)")

    def play(self):
        self.play_innings(self.team1, self.team2)
        target = self.team1.runs + 1
        self.play_innings(self.team2, self.team1, target=target)
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
