import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy, PowerPellet

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 54
FPS = 60

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 14)
        self.hud_font = pygame.font.SysFont("monospace", 15, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 36, bold=True)
        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)
        self.player = Player(0, 0)
        # Task 1: 3 enemies starting at different corners
        self.enemies = [
            Enemy(ROWS - 1, COLS - 1, color=(220, 60, 60)),  # Bottom-Right (Red)
            Enemy(0, COLS - 1, color=(230, 110, 40)),        # Top-Right (Orange)
            Enemy(ROWS - 1, 0, color=(190, 50, 180)),        # Bottom-Left (Purple)
        ]
        # Task 3: Power pellet (freeze enemies for 5s)
        self.pellet = PowerPellet(2, COLS // 2)
        self.exit_rect = pygame.Rect((COLS // 2) * CELL + 5, (ROWS // 2) * CELL + 5, CELL - 10, CELL - 10)
        self.caught = False
        self.won = False
        # Task 2: Elapsed time & Speed Tier
        self.start_ticks = pygame.time.get_ticks()
        self.speed_tier = 1
        # Task 4: Survival Score
        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
        return True

    def update(self):
        if self.caught or self.won:
            return

        # Task 4: Score increments every frame alive
        self.score += 1

        # Task 2: Difficulty ramp - reduce move_interval by 2 every 15s (min 5)
        elapsed_sec = (pygame.time.get_ticks() - self.start_ticks) // 1000
        tier_steps = elapsed_sec // 15
        self.speed_tier = tier_steps + 1
        current_interval = max(5, 20 - tier_steps * 2)

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)

        # Task 3: Power pellet collection (freeze for 5s = 300 frames)
        if self.pellet.active and self.player.rect.colliderect(self.pellet.rect):
            self.pellet.active = False
            for enemy in self.enemies:
                enemy.freeze(300)

        # Task 1: Loop over all enemies independently
        for enemy in self.enemies:
            enemy.move_interval = current_interval
            enemy.update(self.walls, self.player, ROWS, COLS)
            if not enemy.frozen and self.player.rect.colliderect(enemy.rect):
                self.caught = True

        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw(self):
        self.screen.fill((230, 220, 210))
        wc = (50, 40, 60)
        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, r * CELL
                w = self.walls[r][c]
                if w[0]: pygame.draw.line(self.screen, wc, (x, y), (x + CELL, y), 3)
                if w[1]: pygame.draw.line(self.screen, wc, (x, y + CELL), (x + CELL, y + CELL), 3)
                if w[2]: pygame.draw.line(self.screen, wc, (x + CELL, y), (x + CELL, y + CELL), 3)
                if w[3]: pygame.draw.line(self.screen, wc, (x, y), (x, y + CELL), 3)

        # Exit
        pygame.draw.rect(self.screen, (80, 200, 80), self.exit_rect, border_radius=4)
        lbl = self.font.render("EXIT", True, (20, 80, 20))
        self.screen.blit(lbl, (self.exit_rect.x + 3, self.exit_rect.y + 12))

        # Power Pellet
        self.pellet.draw(self.screen)

        # Entities
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # HUD
        hud = pygame.Rect(0, ROWS * CELL, WIDTH, 54)
        pygame.draw.rect(self.screen, (30, 30, 50), hud)

        survived_str = f"Survived: {self.score // 60}s"
        speed_str = f"Speed: Tier {self.speed_tier} ({self.enemies[0].move_interval}f)"
        frozen_enemy = next((e for e in self.enemies if e.frozen), None)
        if frozen_enemy:
            freeze_left = (frozen_enemy.freeze_timer + 59) // 60
            pellet_str = f"Power: FROZEN ({freeze_left}s)"
        elif self.pellet.active:
            pellet_str = "Pellet: Ready (Yellow)"
        else:
            pellet_str = "Pellet: Used"

        line1 = f"{survived_str}  |  {speed_str}  |  {pellet_str}"
        line1_surf = self.hud_font.render(line1, True, (240, 240, 240))
        self.screen.blit(line1_surf, (8, ROWS * CELL + 6))

        line2 = "WASD/Arrows: Move | R: Restart | Escape to green EXIT"
        line2_surf = self.font.render(line2, True, (170, 170, 190))
        self.screen.blit(line2_surf, (8, ROWS * CELL + 28))

        if self.caught:
            self._overlay("CAUGHT!", (220, 60, 60))
        if self.won:
            self._overlay("ESCAPED!", (80, 220, 80))
        pygame.display.flip()

    def _overlay(self, text, color):
        surf = pygame.Surface((WIDTH, ROWS * CELL), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        self.screen.blit(surf, (0, 0))
        msg = self.big_font.render(text, True, color)
        score_msg = self.hud_font.render(
            f"Final Score: {self.score}  (Survived: {self.score // 60}s)",
            True,
            (255, 230, 100),
        )
        sub = self.font.render("Press R to Restart", True, (200, 200, 200))
        self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, ROWS * CELL // 2 - 45))
        self.screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, ROWS * CELL // 2 + 5))
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, ROWS * CELL // 2 + 35))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
