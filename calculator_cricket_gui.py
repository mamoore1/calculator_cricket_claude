#!/usr/bin/env python3
"""PyGame GUI for Calculator Cricket."""

import sys
import random
from enum import Enum

import pygame

from calculator_cricket import (
    Game, Team, Player, BallResult,
    MAX_OVERS, MAX_PER_BOWLER, TEAM_SIZE, MAX_WICKETS,
)

# ---------- Constants ----------

WIDTH, HEIGHT = 1024, 900

COLORS = {
    'bg':          (34, 85, 34),
    'header_bg':   (20, 60, 20),
    'panel_bg':    (44, 100, 44),
    'text_white':  (255, 255, 255),
    'text_yellow': (255, 215, 0),
    'text_gray':   (180, 180, 180),
    'ball_dot':    (100, 100, 100),
    'ball_run':    (50, 180, 50),
    'ball_four':   (70, 130, 230),
    'ball_six':    (255, 215, 0),
    'ball_wicket': (220, 50, 50),
    'ball_noball': (180, 80, 220),
    'row_alt':     (38, 92, 38),
    'separator':   (60, 120, 60),
}


class GamePhase(Enum):
    TOSS_CALL = 1
    TOSS_RESULT = 2
    TOSS_CHOICE = 3
    INNINGS_READY = 4
    WAITING_FOR_BALL = 5
    INNINGS_COMPLETE = 6
    MATCH_RESULT = 7
    OVER_COMPLETE = 8


class CricketGUI:
    def __init__(self, team1_name="Team 1", team2_name="Team 2"):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Calculator Cricket")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_large = pygame.font.SysFont("monospace", 32, bold=True)
        self.font_medium = pygame.font.SysFont("monospace", 22, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 18)
        self.font_tiny = pygame.font.SysFont("monospace", 14)
        self.font_result = pygame.font.SysFont("monospace", 40, bold=True)

        # Game objects
        self.game = Game(team1_name, team2_name)
        self.phase = GamePhase.TOSS_CALL

        # Toss state
        self.toss_call = None
        self.toss_flip = None
        self.toss_won = False
        self.toss_message = ""

        # Innings state
        self.innings_number = 0
        self.batting_team = None
        self.bowling_team = None
        self.target = None
        self.over_number = 0
        self.balls_this_over = 0
        self.current_bowler = None
        self.last_bowler = None
        self.current_over_results = []
        self.last_result = None
        self.last_roll = None
        self.last_batsman_name = None
        self.scorecard_scroll = 0
        self.milestone_message = None
        self.over_complete_pending = False
        self.bowlers = []

    def _select_bowler(self):
        eligible = [b for b in self.bowlers
                    if b.bowling_balls < MAX_PER_BOWLER * 6 and b is not self.last_bowler]
        return random.choice(eligible)

    def _start_innings(self, batting, bowling, target=None):
        self.batting_team = batting
        self.bowling_team = bowling
        self.target = target
        self.innings_number += 1
        self.over_number = 1
        self.balls_this_over = 0
        self.last_bowler = None
        self.current_over_results = []
        self.last_result = None
        self.last_roll = None
        self.last_batsman_name = None
        self.scorecard_scroll = 0
        self.milestone_message = None
        self.over_complete_pending = False
        self.top_bat_idx = batting.striker_idx
        self.bot_bat_idx = batting.non_striker_idx
        self.bowler_order = []
        self.bowlers = bowling.players[5:TEAM_SIZE]
        self.current_bowler = self._select_bowler()
        self.bowler_order.append(self.current_bowler)

    def _end_over(self):
        """Handle end-of-over housekeeping."""
        self.last_bowler = self.current_bowler
        # Swap strike
        self.batting_team.striker_idx, self.batting_team.non_striker_idx = (
            self.batting_team.non_striker_idx, self.batting_team.striker_idx)
        self.over_number += 1
        self.balls_this_over = 0
        self.current_over_results = []
        if self.over_number <= MAX_OVERS:
            self.current_bowler = self._select_bowler()
            if self.current_bowler not in self.bowler_order:
                self.bowler_order.append(self.current_bowler)

    def _check_innings_end(self):
        """Return True if innings should end."""
        if self.batting_team.is_all_out():
            return True
        if self.target is not None and self.batting_team.runs >= self.target:
            return True
        if self.batting_team.legal_balls >= MAX_OVERS * 6:
            return True
        return False

    def bowl_delivery(self):
        roll = random.randint(0, 9)
        self.last_roll = roll
        self.last_batsman_name = self.batting_team.striker.short_name
        self.milestone_message = None

        old_striker_idx = self.batting_team.striker_idx
        runs_before = self.batting_team.striker.runs

        result = self.game._process_ball(
            self.batting_team, self.bowling_team, self.current_bowler, roll)

        self.last_result = result
        self.current_over_results.append((roll, result))

        # Update display slots: replace dismissed batsman with incoming one
        if result.is_wicket and not self.batting_team.is_all_out():
            new_idx = self.batting_team.striker_idx
            if self.top_bat_idx == old_striker_idx:
                self.top_bat_idx = new_idx
            elif self.bot_bat_idx == old_striker_idx:
                self.bot_bat_idx = new_idx

        # Check milestones on the batsman who faced the ball
        if not result.is_wicket:
            runs_after = self.batting_team.striker.runs
            if runs_before < 100 <= runs_after:
                self.milestone_message = "CENTURY!"
            elif runs_before < 50 <= runs_after:
                self.milestone_message = "HALF-CENTURY!"

        if result.is_legal:
            self.balls_this_over += 1

        # Check if innings is done
        if self._check_innings_end():
            self.phase = GamePhase.INNINGS_COMPLETE
        # Flag over as complete (transition happens on next SPACE)
        elif self.balls_this_over >= 6:
            self.over_complete_pending = True

    def _format_overs(self, legal_balls):
        return Game._format_overs(legal_balls)

    # ---------- Event handling ----------

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_q:
                return False
            self._handle_key(event.key)
        if event.type == pygame.MOUSEWHEEL:
            self.handle_scroll(-event.y)
        return True

    def _handle_key(self, key):
        if self.phase == GamePhase.TOSS_CALL:
            if key == pygame.K_h:
                self._do_toss("Heads")
            elif key == pygame.K_t:
                self._do_toss("Tails")

        elif self.phase == GamePhase.TOSS_RESULT:
            if key == pygame.K_SPACE:
                if self.toss_won:
                    self.phase = GamePhase.TOSS_CHOICE
                else:
                    # Opposition decides
                    choice = random.choice(["bat", "bowl"])
                    # Opposition chose — invert for team1
                    if choice == "bat":
                        self.game.batting_first = self.game.team2
                        self.game.batting_second = self.game.team1
                    else:
                        self.game.batting_first = self.game.team1
                        self.game.batting_second = self.game.team2
                    self.toss_message = f"{self.game.team2.name} chose to {choice}"
                    self._start_innings(self.game.batting_first, self.game.batting_second)
                    self.phase = GamePhase.INNINGS_READY

        elif self.phase == GamePhase.TOSS_CHOICE:
            if key == pygame.K_b:
                self.game.batting_first = self.game.team1
                self.game.batting_second = self.game.team2
                self._start_innings(self.game.batting_first, self.game.batting_second)
                self.phase = GamePhase.INNINGS_READY
            elif key == pygame.K_o:
                self.game.batting_first = self.game.team2
                self.game.batting_second = self.game.team1
                self._start_innings(self.game.batting_first, self.game.batting_second)
                self.phase = GamePhase.INNINGS_READY

        elif self.phase == GamePhase.INNINGS_READY:
            if key == pygame.K_SPACE:
                self.phase = GamePhase.WAITING_FOR_BALL

        elif self.phase == GamePhase.WAITING_FOR_BALL:
            if key == pygame.K_SPACE:
                if self.over_complete_pending:
                    self.over_complete_pending = False
                    self.phase = GamePhase.OVER_COMPLETE
                else:
                    self.bowl_delivery()

        elif self.phase == GamePhase.OVER_COMPLETE:
            if key == pygame.K_SPACE:
                self._end_over()
                self.last_result = None
                self.last_roll = None
                self.milestone_message = None
                self.phase = GamePhase.WAITING_FOR_BALL

        elif self.phase == GamePhase.INNINGS_COMPLETE:
            if key == pygame.K_SPACE:
                if self.innings_number == 1:
                    target = self.game.batting_first.runs + 1
                    self._start_innings(self.game.batting_second, self.game.batting_first, target)
                    self.phase = GamePhase.INNINGS_READY
                else:
                    self.phase = GamePhase.MATCH_RESULT

        elif self.phase == GamePhase.MATCH_RESULT:
            if key == pygame.K_SPACE:
                return  # will be caught by quit

    def _do_toss(self, call):
        self.toss_call = call
        self.toss_flip = random.choice(["Heads", "Tails"])
        self.toss_won = (self.toss_call == self.toss_flip)
        if self.toss_won:
            self.toss_message = f"It's {self.toss_flip}! You win the toss!"
        else:
            self.toss_message = f"It's {self.toss_flip}! You lose the toss."
        self.phase = GamePhase.TOSS_RESULT

    def handle_scroll(self, direction):
        self.scorecard_scroll += direction * 20
        self.scorecard_scroll = max(0, self.scorecard_scroll)

    # ---------- Drawing ----------

    def draw(self):
        self.screen.fill(COLORS['bg'])

        if self.phase in (GamePhase.TOSS_CALL, GamePhase.TOSS_RESULT, GamePhase.TOSS_CHOICE):
            self._draw_toss_screen()
        elif self.phase == GamePhase.MATCH_RESULT:
            self._draw_result_screen()
        else:
            self._draw_header()
            self._draw_match_info()
            self._draw_score_banner()
            self._draw_current_over_and_batsmen()
            self._draw_bowler_info()
            self._draw_ball_result()
            self._draw_scorecard()
            self._draw_status_bar()

        pygame.display.flip()

    def _draw_header(self):
        pygame.draw.rect(self.screen, COLORS['header_bg'], (0, 0, WIDTH, 50))
        text = self.font_large.render("Calculator Cricket", True, COLORS['text_white'])
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 10))

    def _draw_match_info(self):
        pygame.draw.rect(self.screen, COLORS['panel_bg'], (0, 50, WIDTH, 40))
        pygame.draw.line(self.screen, COLORS['separator'], (0, 50), (WIDTH, 50))

        innings_text = f"{'1st' if self.innings_number == 1 else '2nd'} Innings"
        overs_text = f"Overs: {self._format_overs(self.batting_team.legal_balls)}/{MAX_OVERS}"

        parts = [innings_text, overs_text]
        if self.target is not None:
            remaining = self.target - self.batting_team.runs
            balls_left = MAX_OVERS * 6 - self.batting_team.legal_balls
            parts.append(f"Target: {self.target}")
            parts.append(f"Need {remaining} from {balls_left} balls")

        info_str = "  |  ".join(parts)
        text = self.font_small.render(info_str, True, COLORS['text_gray'])
        self.screen.blit(text, (20, 60))

    def _draw_score_banner(self):
        pygame.draw.rect(self.screen, COLORS['header_bg'], (0, 90, WIDTH, 60))
        overs = self._format_overs(self.batting_team.legal_balls)
        score_str = f"{self.batting_team.name}: {self.batting_team.runs}/{self.batting_team.outs}  ({overs} ov)"
        text = self.font_large.render(score_str, True, COLORS['text_yellow'])
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 103))

    def _draw_current_over_and_batsmen(self):
        # Left panel: current over
        pygame.draw.rect(self.screen, COLORS['panel_bg'], (0, 150, WIDTH // 2, 70))
        pygame.draw.rect(self.screen, COLORS['panel_bg'], (WIDTH // 2, 150, WIDTH // 2, 70))
        pygame.draw.line(self.screen, COLORS['separator'], (WIDTH // 2, 150), (WIDTH // 2, 220))
        pygame.draw.line(self.screen, COLORS['separator'], (0, 150), (WIDTH, 150))

        label = self.font_tiny.render(f"Over {self.over_number}", True, COLORS['text_gray'])
        self.screen.blit(label, (15, 155))

        x = 15
        for i, (roll, result) in enumerate(self.current_over_results):
            color = self._ball_color(roll, result)
            pygame.draw.circle(self.screen, color, (x + 15, 192), 14)
            # Text on ball
            if result.is_wicket:
                btext = "W"
            elif result.runs == 0:
                btext = "."
            elif not result.is_legal:
                btext = "NB"
            else:
                btext = str(result.runs)
            bt = self.font_tiny.render(btext, True, COLORS['text_white'])
            self.screen.blit(bt, (x + 15 - bt.get_width() // 2, 192 - bt.get_height() // 2))
            x += 36

        # Right panel: batsmen (stable positions, yellow = on strike)
        if not self.batting_team.is_all_out():
            si = self.batting_team.striker_idx
            top = self.batting_team.players[self.top_bat_idx]
            bot = self.batting_team.players[self.bot_bat_idx]
            top_on_strike = (self.top_bat_idx == si)
            bot_on_strike = (self.bot_bat_idx == si)
            top_str = f"{'*' if top_on_strike else ' '} {top.short_name}  {top.runs} ({top.balls_faced}b)"
            bot_str = f"{'*' if bot_on_strike else ' '} {bot.short_name}  {bot.runs} ({bot.balls_faced}b)"
            top_color = COLORS['text_yellow'] if top_on_strike else COLORS['text_gray']
            bot_color = COLORS['text_yellow'] if bot_on_strike else COLORS['text_gray']
            self.screen.blit(self.font_small.render(top_str, True, top_color), (WIDTH // 2 + 15, 160))
            self.screen.blit(self.font_small.render(bot_str, True, bot_color), (WIDTH // 2 + 15, 185))

    def _draw_bowler_info(self):
        pygame.draw.rect(self.screen, COLORS['panel_bg'], (0, 220, WIDTH, 30))
        pygame.draw.line(self.screen, COLORS['separator'], (0, 220), (WIDTH, 220))
        if self.current_bowler:
            overs = self._format_overs(self.current_bowler.bowling_balls)
            b_str = (f"Bowling: {self.current_bowler.short_name}  "
                     f"{overs} ov  {self.current_bowler.wickets_taken}/{self.current_bowler.runs_conceded}")
            text = self.font_small.render(b_str, True, COLORS['text_white'])
            self.screen.blit(text, (15, 225))

    def _draw_ball_result(self):
        pygame.draw.rect(self.screen, COLORS['bg'], (0, 250, WIDTH, 80))
        pygame.draw.line(self.screen, COLORS['separator'], (0, 250), (WIDTH, 250))

        if self.phase == GamePhase.INNINGS_READY:
            text = self.font_medium.render("Press SPACE to start innings", True, COLORS['text_white'])
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 270))
        elif self.phase == GamePhase.OVER_COMPLETE:
            over_done = self.over_number
            over_text = self.font_result.render(f"End of Over {over_done}", True, COLORS['text_white'])
            self.screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 255))
            prompt = self.font_tiny.render("Press SPACE to start next over", True, COLORS['text_gray'])
            self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 305))
        elif self.last_result is not None:
            # Big result text
            color = COLORS['text_yellow'] if self.last_result.runs >= 4 else COLORS['text_white']
            if self.last_result.is_wicket:
                color = COLORS['ball_wicket']
            result_text = self.font_result.render(self.last_result.desc, True, color)
            self.screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 255))

            if self.milestone_message:
                milestone_text = self.font_medium.render(self.milestone_message, True, COLORS['text_yellow'])
                self.screen.blit(milestone_text, (WIDTH // 2 - milestone_text.get_width() // 2, 295))
                prompt = self.font_tiny.render("Press SPACE to bowl next delivery", True, COLORS['text_gray'])
                self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 320))
            else:
                prompt = self.font_tiny.render("Press SPACE to bowl next delivery", True, COLORS['text_gray'])
                self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 305))
        else:
            text = self.font_medium.render("Press SPACE to bowl", True, COLORS['text_white'])
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 275))

    def _draw_scorecard(self):
        y_start = 330
        card_height = 530
        pygame.draw.rect(self.screen, COLORS['bg'], (0, y_start, WIDTH, card_height))
        pygame.draw.line(self.screen, COLORS['separator'], (0, y_start), (WIDTH, y_start))

        # Title
        title = self.font_small.render("SCORECARD", True, COLORS['text_gray'])
        self.screen.blit(title, (15, y_start + 5))

        # Clipping region
        clip_y = y_start + 25
        clip_h = card_height - 25
        clip_rect = pygame.Rect(0, clip_y, WIDTH, clip_h)

        # Build rows
        rows = []
        for i, p in enumerate(self.batting_team.players):
            if p.out:
                status = p.how_out
                runs_str = f"{p.runs}  ({p.balls_faced}b)"
            elif p.balls_faced > 0 or i in (self.batting_team.striker_idx, self.batting_team.non_striker_idx):
                status = "not out"
                runs_str = f"{p.runs}* ({p.balls_faced}b)"
            else:
                status = "did not bat"
                runs_str = ""
            rows.append((p.short_name, status, runs_str))

        row_h = 22
        active_bowlers = len([b for b in self.bowling_team.players if b.bowling_balls > 0])
        # batting rows + bowling header + bowler rows + spacing
        total_h = len(rows) * row_h + 32 + active_bowlers * row_h
        max_scroll = max(0, total_h - clip_h + 10)
        self.scorecard_scroll = min(self.scorecard_scroll, max_scroll)

        self.screen.set_clip(clip_rect)
        for i, (name, status, runs_str) in enumerate(rows):
            ry = clip_y + i * row_h - self.scorecard_scroll
            if ry + row_h < clip_y or ry > clip_y + clip_h:
                continue
            if i % 2 == 1:
                pygame.draw.rect(self.screen, COLORS['row_alt'], (0, ry, WIDTH, row_h))
            name_t = self.font_tiny.render(f"  {name:<18}", True, COLORS['text_white'])
            stat_t = self.font_tiny.render(f"{status:<28}", True, COLORS['text_gray'])
            runs_t = self.font_tiny.render(runs_str, True, COLORS['text_yellow'])
            self.screen.blit(name_t, (10, ry + 2))
            self.screen.blit(stat_t, (200, ry + 2))
            self.screen.blit(runs_t, (520, ry + 2))
        self.screen.set_clip(None)

        # Bowling figures below batting
        bowl_y = clip_y + len(rows) * row_h - self.scorecard_scroll + 10
        if bowl_y < clip_y + clip_h:
            self.screen.set_clip(clip_rect)
            bl = self.font_small.render("BOWLING", True, COLORS['text_gray'])
            self.screen.blit(bl, (15, bowl_y))
            bowl_y += 22
            active = [b for b in self.bowler_order if b.bowling_balls > 0]
            for i, b in enumerate(active):
                by = bowl_y + i * row_h
                if by + row_h < clip_y or by > clip_y + clip_h:
                    continue
                if i % 2 == 1:
                    pygame.draw.rect(self.screen, COLORS['row_alt'], (0, by, WIDTH, row_h))
                overs = self._format_overs(b.bowling_balls)
                nt = self.font_tiny.render(f"  {b.short_name:<18}", True, COLORS['text_white'])
                st = self.font_tiny.render(f"{overs} ov   {b.wickets_taken}/{b.runs_conceded}", True, COLORS['text_gray'])
                self.screen.blit(nt, (10, by + 2))
                self.screen.blit(st, (200, by + 2))
            self.screen.set_clip(None)

    def _draw_status_bar(self):
        pygame.draw.rect(self.screen, COLORS['header_bg'], (0, 860, WIDTH, 40))
        text = self.font_tiny.render("SPACE = Bowl  |  ESC = Quit  |  Scroll = Scorecard", True, COLORS['text_gray'])
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 872))

    def _draw_toss_screen(self):
        self._draw_header()
        cy = HEIGHT // 2 - 80

        # Show team info
        t1 = self.font_small.render(
            f"{self.game.team1.name} — Captain: {self.game.team1.captain.short_name}",
            True, COLORS['text_white'])
        t2 = self.font_small.render(
            f"{self.game.team2.name} — Captain: {self.game.team2.captain.short_name}",
            True, COLORS['text_white'])
        self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, cy))
        self.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, cy + 30))

        if self.phase == GamePhase.TOSS_CALL:
            prompt = self.font_medium.render("COIN TOSS", True, COLORS['text_yellow'])
            self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, cy + 80))
            prompt2 = self.font_small.render("Press H for Heads, T for Tails", True, COLORS['text_white'])
            self.screen.blit(prompt2, (WIDTH // 2 - prompt2.get_width() // 2, cy + 120))

        elif self.phase == GamePhase.TOSS_RESULT:
            msg = self.font_medium.render(self.toss_message, True, COLORS['text_yellow'])
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, cy + 80))
            prompt = self.font_small.render("Press SPACE to continue", True, COLORS['text_gray'])
            self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, cy + 120))

        elif self.phase == GamePhase.TOSS_CHOICE:
            msg = self.font_medium.render("You won the toss!", True, COLORS['text_yellow'])
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, cy + 80))
            prompt = self.font_small.render("Press B to Bat first, O to Bowl first", True, COLORS['text_white'])
            self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, cy + 120))

    def _draw_result_screen(self):
        self._draw_header()

        bat_first = self.game.batting_first
        bat_second = self.game.batting_second

        cy = 80
        title = self.font_large.render("MATCH RESULT", True, COLORS['text_yellow'])
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, cy))

        cy += 60
        s1 = f"{bat_first.name}: {bat_first.runs}/{bat_first.outs} ({self._format_overs(bat_first.legal_balls)} ov)"
        s2 = f"{bat_second.name}: {bat_second.runs}/{bat_second.outs} ({self._format_overs(bat_second.legal_balls)} ov)"
        t1 = self.font_medium.render(s1, True, COLORS['text_white'])
        t2 = self.font_medium.render(s2, True, COLORS['text_white'])
        self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, cy))
        self.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, cy + 35))

        cy += 90
        # Winner
        if bat_first.runs > bat_second.runs:
            diff = bat_first.runs - bat_second.runs
            winner = f"{bat_first.name} wins by {diff} runs!"
        elif bat_second.runs > bat_first.runs:
            wickets = MAX_WICKETS - bat_second.outs
            winner = f"{bat_second.name} wins by {wickets} wickets!"
        else:
            winner = "It's a tie!"

        wt = self.font_large.render(winner, True, COLORS['text_yellow'])
        self.screen.blit(wt, (WIDTH // 2 - wt.get_width() // 2, cy))

        # Top scorers
        cy += 60
        for team in (bat_first, bat_second):
            label = self.font_small.render(f"{team.name} - Top Scorers:", True, COLORS['text_gray'])
            self.screen.blit(label, (60, cy))
            cy += 25
            top3 = sorted(team.players, key=lambda b: b.runs, reverse=True)[:3]
            for i, b in enumerate(top3, 1):
                star = "" if b.out else "*"
                line = f"  {i}. {b.short_name}   {b.runs}{star} ({b.balls_faced}b)"
                lt = self.font_tiny.render(line, True, COLORS['text_white'])
                self.screen.blit(lt, (80, cy))
                cy += 20
            cy += 10

        # Top bowlers
        for team, bowling_team in ((bat_first, bat_second), (bat_second, bat_first)):
            label = self.font_small.render(f"{bowling_team.name} - Top Bowlers:", True, COLORS['text_gray'])
            self.screen.blit(label, (60, cy))
            cy += 25
            active = [b for b in bowling_team.players if b.bowling_balls > 0]
            top3 = sorted(active, key=lambda b: (-b.wickets_taken, b.runs_conceded))[:3]
            for i, b in enumerate(top3, 1):
                overs = self._format_overs(b.bowling_balls)
                line = f"  {i}. {b.short_name}   {b.wickets_taken}/{b.runs_conceded} ({overs} ov)"
                lt = self.font_tiny.render(line, True, COLORS['text_white'])
                self.screen.blit(lt, (80, cy))
                cy += 20
            cy += 10

        prompt = self.font_small.render("Press SPACE or ESC to exit", True, COLORS['text_gray'])
        self.screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 50))

    def _ball_color(self, roll, result):
        if result.is_wicket:
            return COLORS['ball_wicket']
        if not result.is_legal:
            return COLORS['ball_noball']
        if result.runs == 6:
            return COLORS['ball_six']
        if result.runs == 4:
            return COLORS['ball_four']
        if result.runs == 0:
            return COLORS['ball_dot']
        return COLORS['ball_run']

    # ---------- Main loop ----------

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                running = self.handle_event(event)
                if not running:
                    break
            if running:
                self.draw()
                self.clock.tick(30)
        pygame.quit()


def main():
    team1 = sys.argv[1] if len(sys.argv) > 1 else "Team 1"
    team2 = sys.argv[2] if len(sys.argv) > 2 else "Team 2"
    gui = CricketGUI(team1, team2)
    gui.run()


if __name__ == "__main__":
    main()
