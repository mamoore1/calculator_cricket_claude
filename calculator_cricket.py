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
        self.captain = random.choice(self.batsmen)
        self.keeper = random.choice(self.batsmen[:6])
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
        bowlers = bowling_team.batsmen[5:11]
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
                    if how == "Caught":
                        fielder = random.choice(bowling_team.batsmen)
                        team.striker.how_out = f"c {fielder.short_name} b {bowler.short_name}"
                    elif how == "Stumped":
                        team.striker.how_out = f"st \u2020{bowling_team.keeper.short_name} b {bowler.short_name}"
                    elif how == "Bowled":
                        team.striker.how_out = f"b {bowler.short_name}"
                    elif how == "LBW":
                        team.striker.how_out = f"lbw b {bowler.short_name}"
                    elif how == "Run Out":
                        team.striker.how_out = "Run Out"
                    elif how == "Hit Wicket":
                        team.striker.how_out = f"Hit Wicket b {bowler.short_name}"
                    desc = f"OUT! ({how})"
                    if team.next_idx < len(team.batsmen):
                        team.striker_idx = team.next_idx
                        team.next_idx += 1
                        new_batsman = team.striker.short_name
                    else:
                        new_batsman = None

                ball_display = f"{over_number - 1}.{balls_this_over}"
                print(f"{ball_display}: [{roll}] {desc} "
                      f"({display_name}*)  |  "
                      f"Score: {team.runs}/{team.outs}")

                if roll == 9 and not team.is_all_out():
                    print(f"  New batsman: {new_batsman}")

                if target is not None and team.runs >= target:
                    print(f"\n{team.name} reached the target!")
                    target_reached = True
                    break

            # End of over summary
            if not target_reached and not team.is_all_out():
                overs_so_far = self._format_overs(team.legal_balls)
                bowler_overs = self._format_overs(bowler.bowling_balls)
                print(f"\n  End of Over {over_number}: {team.name} {team.runs}/{team.outs} ({overs_so_far} ov)")
                striker = team.striker
                non_striker = team.non_striker
                star_s = "" if striker.out else "*"
                star_ns = "" if non_striker.out else "*"
                print(f"  {striker.short_name} {striker.runs}{star_s} ({striker.balls_faced}b)  |  "
                      f"{non_striker.short_name} {non_striker.runs}{star_ns} ({non_striker.balls_faced}b)")
                print(f"  {bowler.short_name}: {bowler_overs} ov, "
                      f"{bowler.wickets_taken}/{bowler.runs_conceded}")
                if target is not None:
                    remaining = target - team.runs
                    print(f"  Need {remaining} runs from {max_overs * 6 - team.legal_balls} balls")
                print()

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
                print(f"  {b.short_name:<18} {b.how_out:<28} "
                      f"{b.runs}  ({b.balls_faced} balls)")
            elif b.balls_faced > 0:
                print(f"  {b.short_name:<18} {'not out':<28} "
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
        bat_first = self.batting_first
        bat_second = self.batting_second

        print(f"\n{'='*40}")
        print("RESULT")
        print(f"{'='*40}")
        print(f"{bat_first.name}: {bat_first.runs}/{bat_first.outs}")
        print(f"{bat_second.name}: {bat_second.runs}/{bat_second.outs}")
        print()

        if bat_first.runs > bat_second.runs:
            diff = bat_first.runs - bat_second.runs
            print(f"{bat_first.name} wins by {diff} runs!")
        elif bat_second.runs > bat_first.runs:
            wickets = 10 - bat_second.outs
            print(f"{bat_second.name} wins by {wickets} wickets!")
        else:
            print("It's a tie!")

        print(f"\n--- Top Scorers ---")
        for team in (bat_first, bat_second):
            print(f"{team.name}:")
            top3 = sorted(team.batsmen, key=lambda b: b.runs, reverse=True)[:3]
            for i, b in enumerate(top3, 1):
                star = "" if b.out else "*"
                print(f"  {i}. {b.short_name}   {b.runs}{star}")

        print(f"\n--- Top Bowlers ---")
        for team, bowling_team in ((bat_first, bat_second),
                                   (bat_second, bat_first)):
            print(f"{bowling_team.name} (bowling vs {team.name}):")
            active = [b for b in bowling_team.batsmen if b.bowling_balls > 0]
            top3 = sorted(active, key=lambda b: (-b.wickets_taken, b.runs_conceded))[:3]
            for i, b in enumerate(top3, 1):
                overs = self._format_overs(b.bowling_balls)
                print(f"  {i}. {b.short_name}   {b.wickets_taken}/{b.runs_conceded} ({overs} ov)")

    def play(self):
        print(f"\nCoin Toss!")
        print(f"{self.team1.name} captain: {self.team1.captain.short_name} vs "
              f"{self.team2.name} captain: {self.team2.captain.short_name}")

        while True:
            call = input(f"Your captain {self.team1.captain.short_name} calls - Heads or Tails? (h/t): ").strip().lower()
            if call in ("h", "t"):
                break
            print("Please enter 'h' or 't'.")

        call_name = "Heads" if call == "h" else "Tails"
        flip = random.choice(["Heads", "Tails"])

        if call_name == flip:
            print(f"It's {flip}! You win the toss!")
            while True:
                choice = input("Bat or Bowl? (bat/bowl): ").strip().lower()
                if choice in ("bat", "bowl"):
                    break
                print("Please enter 'bat' or 'bowl'.")
        else:
            print(f"It's {flip}! You lose the toss.")
            choice = random.choice(["bat", "bowl"])
            print(f"{self.team2.name} choose to {choice}")
            # Invert: if opposition chooses to bat, player bowls and vice versa
            choice = "bowl" if choice == "bat" else "bat"

        if choice == "bat":
            self.batting_first = self.team1
            self.batting_second = self.team2
        else:
            self.batting_first = self.team2
            self.batting_second = self.team1

        self.play_innings(self.batting_first, self.batting_second)
        target = self.batting_first.runs + 1
        self.play_innings(self.batting_second, self.batting_first, target=target)
        self.declare_winner()


def main():
    print("Calculator Cricket")
    print("==================\n")

    name1 = input("Enter your team name (default: Team 1): ").strip()
    name2 = input("Enter opposition team name (default: Team 2): ").strip()

    if not name1:
        name1 = "Team 1"
    if not name2:
        name2 = "Team 2"

    game = Game(name1, name2)

    print(f"\nYour team - {game.team1.name}:")
    print(f"  Captain: {game.team1.captain.short_name} (c)")
    print(f"  Wicket Keeper: {game.team1.keeper.short_name} (wk)")
    print(f"\nOpposition - {game.team2.name}:")
    print(f"  Captain: {game.team2.captain.short_name} (c)")
    print(f"  Wicket Keeper: {game.team2.keeper.short_name} (wk)")

    game.play()


if __name__ == "__main__":
    main()
