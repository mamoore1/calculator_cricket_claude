import random


class Team:
    def __init__(self, name):
        self.name = name
        self.runs = 0
        self.outs = 0
        self.balls = 0

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
            roll = random.randint(0, 9)
            team.balls += 1

            if roll in (0, 1, 2, 3, 4):
                team.runs += roll
                if roll == 0:
                    desc = "Dot ball"
                else:
                    desc = f"{roll} run{'s' if roll > 1 else ''}"
            elif roll == 6:
                team.runs += 6
                desc = "SIX!"
            elif roll in (5, 7):
                desc = "Dot ball"
            elif roll == 8:
                team.runs += 1
                desc = "No-ball/Wide (+1 run)"
            elif roll == 9:
                team.outs += 1
                desc = "OUT!"

            print(f"Ball {team.balls}: [{roll}] {desc}  |  "
                  f"Score: {team.runs}/{team.outs}")

            if target is not None and team.runs >= target:
                print(f"\n{team.name} reached the target!")
                break

        if team.is_all_out():
            print(f"\n{team.name} all out!")

        print(f"\n{team.name} final score: {team.runs}/{team.outs} "
              f"({team.balls} balls)")

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
