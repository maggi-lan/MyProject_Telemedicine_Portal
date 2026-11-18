import pygame
from game.maze import CELL

SPEED = 2

class Player:
    def __init__(self, r, c):
        self.r, self.c = r, c
        cx, cy = c*CELL+CELL//2, r*CELL+CELL//2
        self.rect = pygame.Rect(cx-10, cy-10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx=dy=0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx=-SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx=SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy=-SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy=SPEED
        nr = self.rect.move(dx,0)
        if self._valid(nr, walls, rows, cols): self.rect=nr
        nr = self.rect.move(0,dy)
        if self._valid(nr, walls, rows, cols): self.rect=nr

    def _valid(self, rect, walls, rows, cols):
        if rect.left < 0 or rect.right > cols * CELL or rect.top < 0 or rect.bottom > rows * CELL:
            return False
        r_min = max(0, rect.top // CELL)
        r_max = min(rows - 1, (rect.bottom - 1) // CELL)
        c_min = max(0, rect.left // CELL)
        c_max = min(cols - 1, (rect.right - 1) // CELL)
        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                x, y = c * CELL, r * CELL
                w = walls[r][c]
                if w[0] and rect.colliderect(pygame.Rect(x, y - 2, CELL, 4)):
                    return False
                if w[1] and rect.colliderect(pygame.Rect(x, y + CELL - 2, CELL, 4)):
                    return False
                if w[2] and rect.colliderect(pygame.Rect(x + CELL - 2, y, 4, CELL)):
                    return False
                if w[3] and rect.colliderect(pygame.Rect(x - 2, y, 4, CELL)):
                    return False
        return True

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

class Enemy:
    def __init__(self, r, c, color=(220, 60, 60)):
        self.r, self.c = r, c
        cx, cy = c*CELL+CELL//2, r*CELL+CELL//2
        self.rect = pygame.Rect(cx-12, cy-12, 24, 24)
        self.color = color
        self.timer = 0
        self.move_interval = 20  # frames between cell moves
        self.frozen = False
        self.freeze_timer = 0

    def freeze(self, frames=300):
        self.frozen = True
        self.freeze_timer = frames

    def update(self, walls, player, rows, cols):
        if self.frozen:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.frozen = False
            return
        from game.maze import bfs
        self.timer += 1
        if self.timer >= self.move_interval:
            self.timer = 0
            pr, pc = player.rect.centery//CELL, player.rect.centerx//CELL
            step = bfs(walls, (self.r, self.c), (pr, pc), rows, cols)
            if step:
                dr, dc = step
                self.r += dr; self.c += dc
                cx, cy = self.c*CELL+CELL//2, self.r*CELL+CELL//2
                self.rect.center = (cx, cy)

    def draw(self, screen):
        color = (100, 200, 255) if self.frozen else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        if self.frozen:
            # Frozen indicator: ice border and frost snowflake cross
            pygame.draw.rect(screen, (225, 245, 255), self.rect, width=2, border_radius=5)
            cx, cy = self.rect.center
            pygame.draw.line(screen, (255, 255, 255), (cx, cy - 5), (cx, cy + 5), 2)
            pygame.draw.line(screen, (255, 255, 255), (cx - 5, cy), (cx + 5, cy), 2)
        # eyes
        eye_y = self.rect.y + 8
        for ex in [self.rect.x+4, self.rect.x+14]:
            pygame.draw.circle(screen, (255, 255, 255), (ex, eye_y), 4)
            pupil_color = (0, 90, 190) if self.frozen else (0, 0, 0)
            pygame.draw.circle(screen, pupil_color, (ex + 1, eye_y), 2)

class PowerPellet:
    def __init__(self, r, c):
        self.r, self.c = r, c
        self.radius = 8
        cx = c * CELL + CELL // 2
        cy = r * CELL + CELL // 2
        self.rect = pygame.Rect(cx - self.radius, cy - self.radius, self.radius * 2, self.radius * 2)
        self.color = (255, 215, 0)  # Yellow / Gold
        self.active = True

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.color, self.rect.center, self.radius)
            pygame.draw.circle(screen, (255, 255, 220), (self.rect.centerx - 2, self.rect.centery - 2), 3)
