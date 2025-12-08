import pygame, random, math, json

with open("game_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

GAME_TITLE = config["game"]["title"]
INITIAL_LIVES = config["game"]["initial_lives"]
DIFFICULTIES = config["game"]["difficulty_levels"]

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 500
WORLD_SIZE = 2000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Ubuntu", 20, True)


def distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.hypot(dx, dy)


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0

    def follow(self, target):
        self.zoom = 100 / target.mass + 0.3
        self.x = SCREEN_WIDTH / 2 - target.x * self.zoom
        self.y = SCREEN_HEIGHT / 2 - target.y * self.zoom


class Drawable:
    def __init__(self, surface, camera):
        self.surface = surface
        self.camera = camera

    def draw(self):
        pass


class Grid(Drawable):
    def __init__(self, surface, camera):
        super().__init__(surface, camera)
        self.color = (220, 220, 220)

    def draw(self):
        z = self.camera.zoom
        camx, camy = self.camera.x, self.camera.y
        step = 50
        for i in range(0, WORLD_SIZE + 1, step):
            pygame.draw.line(self.surface, self.color,
                             (camx, i * z + camy),
                             (WORLD_SIZE * z + camx, i * z + camy), 1)
            pygame.draw.line(self.surface, self.color,
                             (i * z + camx, camy),
                             (i * z + camx, WORLD_SIZE * z + camy), 1)


class Cell(Drawable):
    COLORS = [(80, 252, 54), (36, 244, 255), (243, 31, 46), (4, 39, 243), (254, 6, 178),
              (255, 211, 7), (216, 6, 254), (145, 255, 7), (7, 255, 182), (255, 6, 86), (147, 7, 255)]

    def __init__(self, surface, camera):
        super().__init__(surface, camera)
        self.x = random.randint(20, WORLD_SIZE - 20)
        self.y = random.randint(20, WORLD_SIZE - 20)
        self.mass = 5
        self.color = random.choice(Cell.COLORS)

    def draw(self):
        z = self.camera.zoom
        camx, camy = self.camera.x, self.camera.y
        cx, cy = int(self.x * z + camx), int(self.y * z + camy)
        pygame.draw.circle(self.surface, self.color, (cx, cy), int(self.mass * z))


class CellList(Drawable):
    def __init__(self, surface, camera, n):
        super().__init__(surface, camera)
        self.cells = [Cell(surface, camera) for _ in range(n)]

    def draw(self):
        for c in self.cells:
            c.draw()


class Player(Drawable):
    COLORS = [(37, 7, 255), (35, 183, 253), (48, 254, 241), (19, 79, 251), (255, 7, 230), (255, 7, 23), (6, 254, 13)]

    def __init__(self, surface, camera, name="Player", speed=4):
        super().__init__(surface, camera)
        self.x = random.randint(100, 400)
        self.y = random.randint(100, 400)
        self.mass = 20
        self.speed = speed
        self.color = random.choice(Player.COLORS)
        self.name = name

    @property
    def radius(self):
        return self.mass / 2

    def move(self):
        keys = pygame.key.get_pressed()
        vx, vy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: vy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: vy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: vx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: vx += 1

        if vx != 0 or vy != 0:
            dist = math.hypot(vx, vy)
            vx, vy = vx / dist, vy / dist
            self.x += vx * self.speed
            self.y += vy * self.speed
        else:
            mx, my = pygame.mouse.get_pos()
            cx, cy = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
            dx, dy = mx - cx, my - cy
            dist = math.hypot(dx, dy)
            if dist != 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

        self.x = max(self.radius, min(WORLD_SIZE - self.radius, self.x))
        self.y = max(self.radius, min(WORLD_SIZE - self.radius, self.y))

    def eat(self, cells):
        eaten = 0
        for c in cells[:]:
            if distance((self.x, self.y), (c.x, c.y)) <= self.radius:
                self.mass += 0.5
                cells.remove(c)
                eaten += 1
        return eaten

    def draw(self):
        z = self.camera.zoom
        camx, camy = self.camera.x, self.camera.y
        cx, cy = int(self.x * z + camx), int(self.y * z + camy)
        pygame.draw.circle(self.surface, (0, 0, 0), (cx, cy), int((self.radius + 3) * z))
        pygame.draw.circle(self.surface, self.color, (cx, cy), int(self.radius * z))
        text = font.render(self.name, True, (50, 50, 50))
        tw, th = text.get_size()
        self.surface.blit(text, (cx - tw // 2, cy - th // 2))



def create_game(difficulty):
    camera = Camera()
    if difficulty == "easy":
        return Grid(screen, camera), CellList(screen, camera, 800), Player(screen, camera, "You", 4)
    elif difficulty == "hard":
        return Grid(screen, camera), CellList(screen, camera, 300), Player(screen, camera, "You", 5)
    else:
        return Grid(screen, camera), CellList(screen, camera, 500), Player(screen, camera, "You", 4)

def create_game(difficulty):
    camera = Camera()
    if difficulty == "easy":
        grid = Grid(screen, camera)
        cells = CellList(screen, camera, 800)
        player = Player(screen, camera, "You", 4)
    elif difficulty == "hard":
        grid = Grid(screen, camera)
        cells = CellList(screen, camera, 300)
        player = Player(screen, camera, "You", 5)
    else:
        grid = Grid(screen, camera)
        cells = CellList(screen, camera, 500)
        player = Player(screen, camera, "You", 4)
    return camera, grid, cells, player


state = "menu"
running = True
score = 0
lives = INITIAL_LIVES
difficulty_index = 0

camera, grid, cells, player = create_game(DIFFICULTIES[difficulty_index])

while running:
    clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            if state == "menu":
                if e.key == pygame.K_LEFT:
                    difficulty_index = (difficulty_index - 1) % len(DIFFICULTIES)
                if e.key == pygame.K_RIGHT:
                    difficulty_index = (difficulty_index + 1) % len(DIFFICULTIES)
                if e.key == pygame.K_RETURN:
                    score, lives = 0, INITIAL_LIVES
                    camera, grid, cells, player = create_game(DIFFICULTIES[difficulty_index])
                    state = "play"
            if state == "game_over":
                if e.key == pygame.K_RETURN:
                    score, lives = 0, INITIAL_LIVES
                    camera, grid, cells, player = create_game(DIFFICULTIES[difficulty_index])
                    state = "play"

    if state == "play":
        player.move()
        eaten = player.eat(cells.cells)
        score += eaten * 10
        camera.follow(player)
        if player.mass < 10:  # условие проигрыша
            state = "game_over"

    screen.fill((242, 251, 255))

    if state == "menu":
        title = font.render("Agar.io by Tomov & Antonova", True, (0, 0, 0))
        tw, th = title.get_size()
        screen.blit(title, (SCREEN_WIDTH // 2 - tw // 2, SCREEN_HEIGHT // 2 - 80))

        diff_text = font.render(f"Difficulty: {DIFFICULTIES[difficulty_index]}", True, (0, 0, 0))
        dw, dh = diff_text.get_size()
        screen.blit(diff_text, (SCREEN_WIDTH // 2 - dw // 2, SCREEN_HEIGHT // 2 - 20))

        hint = font.render("LEFT/RIGHT arrows, ENTER to start", True, (100, 100, 100))
        hw, hh = hint.get_size()
        screen.blit(hint, (SCREEN_WIDTH // 2 - hw // 2, SCREEN_HEIGHT // 2 + 20))

    elif state == "play":
        grid.draw()
        cells.draw()
        player.draw()

        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"Lives: {lives}", True, (0, 0, 0))
        screen.blit(lives_text, (10, 35))
        diff_text = font.render(f"{DIFFICULTIES[difficulty_index]}", True, (0, 0, 0))
        screen.blit(diff_text, (10, 60))

    elif state == "game_over":
        msg = font.render("GAME OVER", True, (200, 0, 0))
        mw, mh = msg.get_size()
        screen.blit(msg, (SCREEN_WIDTH // 2 - mw // 2, SCREEN_HEIGHT // 2 - 40))

        score_text = font.render(f"Final Score: {score}", True, (0, 0, 0))
        sw, sh = score_text.get_size()
        screen.blit(score_text, (SCREEN_WIDTH // 2 - sw // 2, SCREEN_HEIGHT // 2))

        restart = font.render("ENTER to restart", True, (100, 100, 100))
        rw, rh = restart.get_size()
        screen.blit(restart, (SCREEN_WIDTH // 2 - rw // 2, SCREEN_HEIGHT // 2 + 40))

    pygame.display.flip()

pygame.quit()
