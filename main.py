import pygame
import sys
import random
from collections import deque

# --- Конфигурация ---
CELL_SIZE = 40
ROWS, COLS = 10, 15
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE + 50
FPS = 5
NUM_SHEEP = 10
NUM_WOLVES = 3
MAX_STEPS = 100

# --- Инициализация ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --- Цвета ---
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 100, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)


# --- Кнопки ---
class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        label = font.render(self.text, True, BLACK)
        screen.blit(label, (self.rect.x + 10, self.rect.y + 5))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


start_button = Button((10, HEIGHT - 40, 100, 30), "Старт")
pause_button = Button((120, HEIGHT - 40, 100, 30), "Пауза")
reset_button = Button((230, HEIGHT - 40, 100, 30), "Сброс")


# --- Игровые данные ---
def random_positions(count, exclude):
    positions = set()
    while len(positions) < count:
        pos = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
        if pos not in exclude:
            positions.add(pos)
    return list(positions)


def is_valid(x, y):
    return 0 <= x < ROWS and 0 <= y < COLS


def bfs(start, goals):
    queue = deque([start])
    visited = set([start])
    prev = {start: None}
    while queue:
        current = queue.popleft()
        if current in goals:
            path = []
            while current:
                path.append(current)
                current = prev[current]
            return list(reversed(path))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = current[0] + dx, current[1] + dy
            if is_valid(nx, ny) and (nx, ny) not in visited:
                visited.add((nx, ny))
                prev[(nx, ny)] = current
                queue.append((nx, ny))
    return []


# --- Сброс состояния ---
def reset_game():
    global pastukh, sheep_positions, wolf_positions, game_over, game_won, step_count
    step_count = 0
    game_over = False
    game_won = False
    pastukh = (ROWS // 2, COLS // 2)
    sheep_positions = random_positions(NUM_SHEEP, {pastukh})
    wolf_positions = random_positions(NUM_WOLVES, set(sheep_positions + [pastukh]))


reset_game()

running = False


# --- Симуляция одного шага ---
def step_simulation():
    global pastukh, sheep_positions, wolf_positions, game_over, game_won, step_count

    if game_over:
        return

    step_count += 1

    # Пастух к ближайшей овце
    path_to_sheep = bfs(pastukh, sheep_positions)
    if len(path_to_sheep) > 1:
        pastukh = path_to_sheep[1]

    # Волки к овцам или пастуху
    new_wolves = []
    for wolf in wolf_positions:
        targets = sheep_positions + [pastukh]
        path = bfs(wolf, targets)
        if len(path) > 1:
            new_wolves.append(path[1])
        else:
            new_wolves.append(wolf)
    wolf_positions[:] = new_wolves

    # Проверка столкновений
    sheep_positions[:] = [s for s in sheep_positions if s not in wolf_positions]

    if pastukh in wolf_positions:
        game_over = True
        game_won = True
    elif not sheep_positions:
        game_over = True
        game_won = False
    elif step_count >= MAX_STEPS:
        game_over = True
        game_won = False


# --- Рендеринг ---
def draw():
    screen.fill(WHITE)
    # Сетка
    for x in range(COLS):
        for y in range(ROWS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

    # Овцы
    for x, y in sheep_positions:
        pygame.draw.circle(screen, GREEN, (y * CELL_SIZE + 20, x * CELL_SIZE + 20), 10)

    # Волки
    for x, y in wolf_positions:
        pygame.draw.circle(screen, RED, (y * CELL_SIZE + 20, x * CELL_SIZE + 20), 10)

    # Пастух
    pygame.draw.circle(screen, BLUE, (pastukh[1] * CELL_SIZE + 20, pastukh[0] * CELL_SIZE + 20), 10)

    # Кнопки
    start_button.draw()
    pause_button.draw()
    reset_button.draw()

    # Статус
    status = f"Овцы: {len(sheep_positions)}  Ход: {step_count}/{MAX_STEPS}"
    label = font.render(status, True, BLACK)
    screen.blit(label, (350, HEIGHT - 35))

    if game_over:
        msg = "ПОБЕДА Пастуха!" if game_won else "Поражение. Все овцы съедены."
        result_label = font.render(msg, True, YELLOW)
        screen.blit(result_label, (WIDTH // 2 - 100, HEIGHT - 35))

    pygame.display.flip()


# --- Главный цикл ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(event.pos):
                running = True
            elif pause_button.is_clicked(event.pos):
                running = False
            elif reset_button.is_clicked(event.pos):
                running = False
                reset_game()

    if running:
        step_simulation()

    draw()
    clock.tick(FPS)
