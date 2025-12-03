import pygame
import sys
import random
import time
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Number Match")

# Space theme colors
DARK_SPACE = (5, 5, 20)
DEEP_SPACE = (10, 10, 40)
STAR_BLUE = (30, 144, 255)
PLANET_PURPLE = (138, 43, 226)
ASTEROID_GRAY = (169, 169, 169)
SPACESHIP_ORANGE = (255, 140, 0)
GALAXY_PINK = (255, 105, 180)
NEBULA_TEAL = (0, 255, 255)
STAR_WHITE = (255, 255, 255)
ALIEN_GREEN = (50, 205, 50)
WARNING_RED = (255, 50, 50)
GRID_BLUE = (0, 100, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# Fonts
try:
    title_font = pygame.font.Font(None, 64)
    header_font = pygame.font.Font(None, 40)
    button_font = pygame.font.Font(None, 32)
    cell_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
except:
    title_font = pygame.font.SysFont('arial', 64, bold=True)
    header_font = pygame.font.SysFont('arial', 40, bold=True)
    button_font = pygame.font.SysFont('arial', 32)
    cell_font = pygame.font.SysFont('arial', 36, bold=True)
    small_font = pygame.font.SysFont('arial', 24)

# Game constants
GRID_SIZE = 5
CELL_SIZE = 80
GRID_WIDTH = GRID_SIZE * CELL_SIZE
GRID_HEIGHT = GRID_SIZE * CELL_SIZE
# CENTERED GRID POSITION
GRID_MARGIN_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_MARGIN_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2
GRID_TOP = 180  # Keep this for vertical positioning
TIME_PER_LEVEL = 120
MAX_SCORE_FILE = "max_score.txt"
TOTAL_PAIRS_PER_LEVEL = 10
MAX_SCORE_PER_LEVEL = TOTAL_PAIRS_PER_LEVEL * 5

# Load assets
def load_assets():
    assets = {
        'start_bg': None,
        'game_over_bg': None,
        'bg_music': None,
        'game_over_sound': None
    }
    
    # Try to load images
    for img_file in ['game_start.jpeg', 'game_start.jpg', 'game_start.png']:
        if os.path.exists(img_file):
            try:
                assets['start_bg'] = pygame.image.load(img_file)
                assets['start_bg'] = pygame.transform.scale(assets['start_bg'], (SCREEN_WIDTH, SCREEN_HEIGHT))
                break
            except:
                pass
    
    for img_file in ['game_over.jpeg', 'game_over.jpg', 'game_over.png']:
        if os.path.exists(img_file):
            try:
                assets['game_over_bg'] = pygame.image.load(img_file)
                assets['game_over_bg'] = pygame.transform.scale(assets['game_over_bg'], (SCREEN_WIDTH, SCREEN_HEIGHT))
                break
            except:
                pass
    
    # Load sounds
    if os.path.exists('music.mp3'):
        try:
            assets['bg_music'] = 'music.mp3'
            pygame.mixer.music.load('music.mp3')
        except:
            pass
    
    if os.path.exists('game_over.mp3'):
        try:
            assets['game_over_sound'] = pygame.mixer.Sound('game_over.mp3')
        except:
            pass
    
    return assets

assets = load_assets()

if assets['bg_music']:
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)

# Score handling
def load_max_score():
    if os.path.exists(MAX_SCORE_FILE):
        with open(MAX_SCORE_FILE, 'r') as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_max_score(score):
    with open(MAX_SCORE_FILE, 'w') as f:
        f.write(str(score))

# Clean minimalist button
class Button:
    def __init__(self, x, y, width, height, text, color=SPACESHIP_ORANGE, hover_color=NEBULA_TEAL):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
    
    def draw(self, surface):
        # Clean rectangle with slight glow on hover
        if self.current_color == self.hover_color:
            # Hover glow effect
            glow = pygame.Surface((self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*self.current_color, 100), glow.get_rect(), border_radius=6)
            surface.blit(glow, (self.rect.x - 4, self.rect.y - 4))
        
        # Main button
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, STAR_WHITE, self.rect, 2, border_radius=6)
        
        # Text
        text_surf = button_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_hovered(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                return True
        return False

# Clean grid cell
class Cell:
    def __init__(self, row, col, number):
        self.row = row
        self.col = col
        self.number = number
        # CENTERED GRID: Use GRID_MARGIN_X for horizontal centering
        self.x = GRID_MARGIN_X + col * CELL_SIZE
        self.y = GRID_TOP + row * CELL_SIZE  # Keep vertical position from top
        self.rect = pygame.Rect(self.x, self.y, CELL_SIZE, CELL_SIZE)
        self.visible = True
        self.highlighted = False
        
        # Space-themed colors for numbers
        self.colors = [
            STAR_BLUE, PLANET_PURPLE, SPACESHIP_ORANGE, NEBULA_TEAL,
            ALIEN_GREEN, GALAXY_PINK, GRID_BLUE, GOLD, ASTEROID_GRAY
        ]
        self.color = self.colors[(number - 1) % len(self.colors)]
    
    def draw(self, surface):
        if not self.visible:
            return
        
        # Clean cell design
        cell_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        
        # Main cell with slight gradient
        pygame.draw.rect(cell_surf, self.color, (2, 2, CELL_SIZE-4, CELL_SIZE-4), border_radius=8)
        
        # Highlight border if selected
        border_color = GOLD if self.highlighted else STAR_WHITE
        border_width = 3 if self.highlighted else 1
        pygame.draw.rect(cell_surf, border_color, (0, 0, CELL_SIZE, CELL_SIZE), border_width, border_radius=10)
        
        # Number (centered properly)
        num_text = cell_font.render(str(self.number), True, WHITE)
        text_rect = num_text.get_rect(center=(CELL_SIZE//2, CELL_SIZE//2))
        cell_surf.blit(num_text, text_rect)
        
        surface.blit(cell_surf, (self.x, self.y))
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos) and self.visible

# Generate grid with 10 pairs + 5 extras
def generate_grid(rows, cols):
    numbers = []
    
    # 10 pairs
    for _ in range(TOTAL_PAIRS_PER_LEVEL):
        num = random.randint(1, 9)
        numbers.append(num)
        numbers.append(num)
    
    # 5 extras for 5x5 grid
    for _ in range(rows * cols - len(numbers)):
        numbers.append(random.randint(1, 9))
    
    random.shuffle(numbers)
    
    grid = []
    idx = 0
    for r in range(rows):
        row_cells = []
        for c in range(cols):
            row_cells.append(Cell(r, c, numbers[idx]))
            idx += 1
        grid.append(row_cells)
    
    return grid

# Find pairs
def find_identical_pairs(grid):
    pairs = []
    positions = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if not grid[r][c].visible:
                continue
            num = grid[r][c].number
            for rr in range(r, len(grid)):
                start_col = c + 1 if rr == r else 0
                for cc in range(start_col, len(grid[0])):
                    if grid[rr][cc].visible and grid[rr][cc].number == num:
                        pairs.append((num, num))
                        positions.append([(r, c), (rr, cc)])
    return pairs, positions

def find_sum_pairs(grid, target=7):
    pairs = []
    positions = []
    cells = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c].visible:
                cells.append((r, c, grid[r][c].number))
    
    for i in range(len(cells)):
        r1, c1, n1 = cells[i]
        for j in range(i + 1, len(cells)):
            r2, c2, n2 = cells[j]
            if n1 + n2 == target:
                pairs.append((n1, n2))
                positions.append([(r1, c1), (r2, c2)])
    return pairs, positions

# NEW FUNCTION: Check if any sum-to-7 pairs exist
def can_continue_level2(grid):
    """Check if there are any possible sum-to-7 pairs left"""
    visible_numbers = []
    for row in grid:
        for cell in row:
            if cell.visible:
                visible_numbers.append(cell.number)
    
    # Check if any two visible numbers can sum to 7
    for i in range(len(visible_numbers)):
        for j in range(i + 1, len(visible_numbers)):
            if visible_numbers[i] + visible_numbers[j] == 7:
                return True
    return False

# Draw space background
def draw_space_background():
    # Dark space gradient
    screen.fill(DARK_SPACE)
    
    # Stars
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 2)
        brightness = random.randint(150, 255)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
    
    # Distant planets
    pygame.draw.circle(screen, (40, 40, 100), (SCREEN_WIDTH - 100, 100), 50)
    pygame.draw.circle(screen, (100, 40, 100), (100, SCREEN_HEIGHT - 100), 30)

def draw_grid(grid):
    for row in grid:
        for cell in row:
            cell.draw(screen)

def draw_game_info(level, score, time_left, target_text, pairs_found):
    # Info panel
    panel = pygame.Rect(0, 0, SCREEN_WIDTH, 140)
    pygame.draw.rect(screen, DEEP_SPACE, panel)
    pygame.draw.line(screen, STAR_BLUE, (0, 140), (SCREEN_WIDTH, 140), 2)
    
    # Left column: Level and Score
    level_text = header_font.render(f"MISSION {level}", True, STAR_WHITE)
    score_text = small_font.render(f"SCORE: {score}/50", True, GOLD)
    pairs_text = small_font.render(f"PAIRS: {pairs_found}/10", True, ALIEN_GREEN)
    
    screen.blit(level_text, (50, 30))
    screen.blit(score_text, (50, 75))
    screen.blit(pairs_text, (50, 100))
    
    # Center: Mission objective
    target_surf = header_font.render(target_text, True, NEBULA_TEAL)
    screen.blit(target_surf, (SCREEN_WIDTH // 2 - target_surf.get_width() // 2, 75))
    
    # Right column: Timer
    time_text = header_font.render(f"TIME: {int(time_left)}s", True, STAR_WHITE)
    screen.blit(time_text, (SCREEN_WIDTH - 150, 30))
    
    # Timer bar
    bar_width = 200
    bar_height = 8
    bar_x = SCREEN_WIDTH - bar_width - 50
    bar_y = 90
    
    # Background bar
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    
    # Progress bar
    progress = time_left / TIME_PER_LEVEL
    bar_color = ALIEN_GREEN if progress > 0.3 else SPACESHIP_ORANGE if progress > 0.1 else WARNING_RED
    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_width * progress, bar_height))

def draw_selection_info(selected):
    if len(selected) == 1:
        cell = selected[0]
        text = small_font.render(f"Selected: {cell.number}", True, NEBULA_TEAL)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 120))

def display_message(text, color=NEBULA_TEAL, duration=1):
    # Simple message display
    msg_surf = header_font.render(text, True, color)
    msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(msg_surf, msg_rect)
    pygame.display.flip()
    time.sleep(duration)

def level_screen(level, score, time_taken):
    draw_space_background()
    
    # Mission complete panel
    panel = pygame.Rect(SCREEN_WIDTH // 2 - 250, 150, 500, 350)
    pygame.draw.rect(screen, DEEP_SPACE, panel, border_radius=10)
    pygame.draw.rect(screen, STAR_BLUE, panel, 3, border_radius=10)
    
    title = title_font.render(f"MISSION {level} COMPLETE", True, GOLD)
    score_text = header_font.render(f"Points: {score}/50", True, STAR_WHITE)
    time_text = header_font.render(f"Time: {int(time_taken)}s", True, NEBULA_TEAL)
    
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))
    screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 330))
    
    if level == 1:
        btn_text = "CONTINUE"
    else:
        btn_text = "VIEW MISSION REPORT"
    
    continue_btn = Button(SCREEN_WIDTH // 2 - 120, 420, 240, 50, btn_text)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if continue_btn.is_clicked(mouse_pos, event):
                return
        
        continue_btn.is_hovered(mouse_pos)
        continue_btn.draw(screen)
        pygame.display.flip()

def game_over_screen(total_score, total_time, max_score):
    if assets.get('game_over_sound'):
        pygame.mixer.music.stop()
        assets['game_over_sound'].play()
    
    # Draw background
    if assets.get('game_over_bg'):
        screen.blit(assets['game_over_bg'], (0, 0))
    else:
        draw_space_background()
    
    # Mission report panel
    panel = pygame.Rect(SCREEN_WIDTH // 2 - 300, 100, 600, 400)
    pygame.draw.rect(screen, DEEP_SPACE, panel, border_radius=10)
    pygame.draw.rect(screen, STAR_BLUE, panel, 3, border_radius=10)
    
    title = title_font.render("MISSION REPORT", True, GOLD)
    total_score_text = header_font.render(f"Total Points: {total_score}/100", True, STAR_WHITE)
    total_time_text = header_font.render(f"Mission Duration: {int(total_time)}s", True, NEBULA_TEAL)
    max_score_text = header_font.render(f"High Score: {max_score}", True, ALIEN_GREEN)
    
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
    screen.blit(total_score_text, (SCREEN_WIDTH // 2 - total_score_text.get_width() // 2, 230))
    screen.blit(total_time_text, (SCREEN_WIDTH // 2 - total_time_text.get_width() // 2, 280))
    screen.blit(max_score_text, (SCREEN_WIDTH // 2 - max_score_text.get_width() // 2, 330))
    
    restart_btn = Button(SCREEN_WIDTH // 2 - 160, 400, 150, 50, "NEW GAME")
    quit_btn = Button(SCREEN_WIDTH // 2 + 10, 400, 150, 50, "EXIT", WARNING_RED, SPACESHIP_ORANGE)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if restart_btn.is_clicked(mouse_pos, event):
                if assets.get('bg_music'):
                    pygame.mixer.music.play(-1)
                return True
            if quit_btn.is_clicked(mouse_pos, event):
                return False
        
        restart_btn.is_hovered(mouse_pos)
        quit_btn.is_hovered(mouse_pos)
        restart_btn.draw(screen)
        quit_btn.draw(screen)
        pygame.display.flip()

def start_screen():
    max_score = load_max_score()
    
    # Draw background
    if assets.get('start_bg'):
        screen.blit(assets['start_bg'], (0, 0))
    else:
        draw_space_background()
    
    # Title panel
    title_panel = pygame.Rect(SCREEN_WIDTH // 2 - 350, 50, 700, 150)
    pygame.draw.rect(screen, DEEP_SPACE, title_panel, border_radius=10)
    pygame.draw.rect(screen, STAR_BLUE, title_panel, 3, border_radius=10)
    
    title1 = title_font.render("SPACE NUMBER", True, STAR_WHITE)
    title2 = title_font.render("MATCH MISSION", True, NEBULA_TEAL)
    
    screen.blit(title1, (SCREEN_WIDTH // 2 - title1.get_width() // 2, 80))
    screen.blit(title2, (SCREEN_WIDTH // 2 - title2.get_width() // 2, 150))
    
    # Instructions panel
    instr_panel = pygame.Rect(SCREEN_WIDTH // 2 - 300, 220, 600, 220)
    pygame.draw.rect(screen, DEEP_SPACE, instr_panel, border_radius=10)
    pygame.draw.rect(screen, GRID_BLUE, instr_panel, 2, border_radius=10)
    
    instructions = [
        "MISSION 1: Find 10 matching number pairs",
        "MISSION 2: Find 10 pairs that sum to 7",
        "Click two numbers to select them",
        "Press SPACE to clear selection",
        "Complete both missions before time runs out"
    ]
    
    for i, instruction in enumerate(instructions):
        instr_text = small_font.render(instruction, True, STAR_WHITE)
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, 250 + i * 35))
    
    # High score
    score_panel = pygame.Rect(SCREEN_WIDTH // 2 - 200, 460, 400, 50)
    pygame.draw.rect(screen, DEEP_SPACE, score_panel, border_radius=8)
    pygame.draw.rect(screen, GOLD, score_panel, 2, border_radius=8)
    
    max_text = header_font.render(f"High Score: {max_score}/100", True, GOLD)
    screen.blit(max_text, (SCREEN_WIDTH // 2 - max_text.get_width() // 2, 475))
    
    # Start button
    start_btn = Button(SCREEN_WIDTH // 2 - 120, 530, 240, 60, "LAUNCH MISSION")
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if start_btn.is_clicked(mouse_pos, event):
                return
        
        start_btn.is_hovered(mouse_pos)
        start_btn.draw(screen)
        pygame.display.flip()

def count_pairs_found(grid, level):
    visible_count = 0
    for row in grid:
        for cell in row:
            if cell.visible:
                visible_count += 1
    
    total_cells = len(grid) * len(grid[0])
    cells_cleared = total_cells - visible_count
    pairs_found = cells_cleared // 2
    
    return pairs_found

def play_level(level, grid_rows, grid_cols):
    grid = generate_grid(grid_rows, grid_cols)
    score = 0
    selected = []
    level_start_time = time.time()
    time_left = TIME_PER_LEVEL
    pairs_found = 0
    
    if level == 1:
        target_text = "FIND MATCHING NUMBER PAIRS"
        check_pairs_func = find_identical_pairs
    else:
        target_text = "FIND PAIRS THAT SUM TO 7"
        check_pairs_func = lambda g: find_sum_pairs(g, 7)
    
    while True:
        current_time = time.time()
        elapsed = current_time - level_start_time
        time_left = max(0, TIME_PER_LEVEL - elapsed)
        
        pairs_found = count_pairs_found(grid, level)
        
        # Level 1: End when time runs out OR all 10 pairs found
        # Level 2: End when time runs out OR all 10 pairs found OR no more sum-to-7 pairs exist
        if level == 1:
            end_condition = (time_left <= 0 or pairs_found >= TOTAL_PAIRS_PER_LEVEL)
        else:
            # Level 2: Also check if any sum-to-7 pairs are possible
            can_continue = can_continue_level2(grid)
            end_condition = (time_left <= 0 or 
                           pairs_found >= TOTAL_PAIRS_PER_LEVEL or 
                           not can_continue)
        
        if end_condition:
            level_time = TIME_PER_LEVEL - time_left
            # Show message if no more pairs possible (Level 2 only)
            if level == 2 and not can_continue_level2(grid) and pairs_found < TOTAL_PAIRS_PER_LEVEL:
                display_message("NO MORE VALID PAIRS", WARNING_RED, 1.5)
            return score, level_time, grid
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                for row in grid:
                    for cell in row:
                        if cell.is_clicked(pos):
                            if cell in selected:
                                selected.remove(cell)
                                cell.highlighted = False
                            else:
                                if len(selected) < 2:
                                    selected.append(cell)
                                    cell.highlighted = True
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for cell in selected:
                    cell.highlighted = False
                selected.clear()
        
        # Check if two cells selected
        if len(selected) == 2:
            cell1, cell2 = selected
            valid = False
            
            if level == 1:
                valid = (cell1.number == cell2.number)
            else:
                valid = (cell1.number + cell2.number == 7)
            
            if valid:
                score += 5
                cell1.visible = False
                cell2.visible = False
                
                if pairs_found + 1 >= TOTAL_PAIRS_PER_LEVEL:
                    display_message("MISSION COMPLETE!", GOLD, 1)
                else:
                    display_message("+5 POINTS", ALIEN_GREEN, 0.5)
            else:
                display_message("INVALID PAIR", WARNING_RED, 0.5)
            
            for cell in selected:
                cell.highlighted = False
            selected.clear()
        
        # Drawing
        draw_space_background()
        draw_game_info(level, score, time_left, target_text, pairs_found)
        draw_selection_info(selected)
        draw_grid(grid)
        
        # Grid border - CENTERED
        #border_rect = pygame.Rect(GRID_MARGIN_X - 5, GRID_TOP - 5,
        #                         GRID_WIDTH + 10, GRID_HEIGHT + 10)
        #pygame.draw.rect(screen, GRID_BLUE, border_rect, 3, border_radius=12)
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def main_game():
    max_score = load_max_score()
    
    while True:
        start_screen()
        
        # Mission 1
        level1_score, level1_time, grid = play_level(1, GRID_SIZE, GRID_SIZE)
        level_screen(1, level1_score, level1_time)
        
        # Mission 2
        level2_score, level2_time, _ = play_level(2, len(grid), len(grid[0]))
        
        # Calculate totals
        total_score = level1_score + level2_score
        total_time = level1_time + level2_time
        
        # Update max score
        if total_score > max_score:
            max_score = total_score
            save_max_score(max_score)
        
        # Mission report
        restart = game_over_screen(total_score, total_time, max_score)
        if not restart:
            break

if __name__ == "__main__":
    main_game()
    pygame.quit()
    sys.exit()