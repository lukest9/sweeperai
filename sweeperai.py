import pygame
import random
import time

# Constants
GRID_SIZE = 10  
CELL_SIZE = 40  
MINE_COUNT = 20
WIDTH, HEIGHT = GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE

# Colors
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLACK = (0, 0, 0)           # Mine, -1
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

# Grid Representation
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
flagged = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
mines = set()
game_over = False
win = False

def place_mines():
    while len(mines) < MINE_COUNT:
        row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if (row, col) not in mines:
            mines.add((row, col))
            grid[row][col] = -1

def calculate_numbers():
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    for row, col in mines:
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and grid[nr][nc] != -1:
                grid[nr][nc] += 1  

def reveal_cells(row, col):
    global game_over
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    #if a mine is clicked
    if grid[row][col] == -1:
        revealed[row][col] = True
        draw_grid()
        game_over = True
        return
    #if out of bounds, or if flagged, return
    if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
        return
    #if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE or revealed[row][col]:
    #    return
    #as long as the cell isn't flagged, but still allows recursion on neighbors
    if not flagged[row][col]:
        revealed[row][col] = True

    #if blank
    if grid[row][col] == 0:
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and not revealed[nr][nc]:
                #recursion
                reveal_cells(nr, nc)

def check_win():
    #checks by making sure nothing is unrevealed, possibly a global flag counter is faster, but it would be technically incorrect
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] != -1 and not revealed[row][col]:
                return False
    return True

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x, y = col * CELL_SIZE, row * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            if revealed[row][col]:  
                pygame.draw.rect(screen, DARK_GRAY, rect)

                if grid[row][col] == -1:  
                    pygame.draw.circle(screen, BLACK, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 10)
                elif grid[row][col] > 0:  
                    font = pygame.font.Font(None, 30)
                    text = font.render(str(grid[row][col]), True, BLUE)
                    screen.blit(text, (x + 12, y + 8))
            else:
                pygame.draw.rect(screen, GRAY, rect)

            if flagged[row][col]:  
                pygame.draw.circle(screen, RED, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 10)

            pygame.draw.rect(screen, BLACK, rect, 2)  

def draw_game_over():
    font = pygame.font.Font(None, 50)
    text = font.render("Game Over!", True, RED)
    screen.blit(text, (WIDTH // 4, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(500)

def draw_win_message():
    font = pygame.font.Font(None, 50)
    text = font.render("You Win!", True, GREEN)
    screen.blit(text, (WIDTH // 4, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(500)

def check_available():
    global win, running
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    changed = True
    while changed:
        changed = False
        #check all cells
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                #if it's a number
                if revealed[row][col] and grid[row][col] > 0:
                    adj_flags = 0
                    hidden = []
                    #check all adj
                    for dr, dc in directions:
                        nr, nc = row + dr, col + dc
                        #if not out of bounds
                        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                            #if its flagged, otherwise if it hasn't been touched yet add it to hidden
                            if flagged[nr][nc]:
                                adj_flags += 1
                            elif not revealed[nr][nc]:
                                hidden.append((nr, nc))

                    #if number == all adj cells, including flags, flag everything, which is the contents of hidden
                    if adj_flags + len(hidden) == grid[row][col]:
                        for nr, nc in hidden:
                            if not flagged[nr][nc]:
                                flagged[nr][nc] = True
                                #mark a change, because there might be cells above that are newly flagged
                                changed = True

                    #if the number is satisfied, reveal everything in hidden
                    if adj_flags == grid[row][col]:
                        for nr, nc in hidden:
                            if not revealed[nr][nc]:
                                revealed[nr][nc] = True
                                #mark a change, because new cells are revealed
                                changed = True
                                reveal_cells(nr, nc)
                elif revealed[row][col] and grid[row][col] == 0:
                    reveal_cells(row, col)
        if sum(cell for row in flagged for cell in row) >= MINE_COUNT:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if not flagged[row][col]:
                        revealed[row][col] = True
            win = True

def pick_random():
    while True:
        random_row = random.randint(0, GRID_SIZE - 1)
        random_col = random.randint(0, GRID_SIZE - 1)
        if not revealed[random_row][random_col]:
            print(f"Guessing randomly at {random_row}, {random_col} which is {grid[random_row][random_col]}")
            revealed[random_row][random_col] = True
            reveal_cells(random_row, random_col)
            return

def ai1():
    while True:
        stuck = sum(sum(row) for row in revealed)
        check_available()
        if win:
            return
        if stuck == sum(sum(row) for row in revealed):  # Stop if no new reveals
            break
    pick_random()
    if game_over:
        return
        
def pick_first():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if not grid[row][col] == -1:
                revealed[row][col] = True
                reveal_cells(row, col)
                return

def main():
    global game_over, win
    
    place_mines()
    calculate_numbers()
    pick_first()

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid()
        pygame.display.flip()

        if game_over:
            draw_grid()
            print(f"Revealed {sum(cell for row in revealed for cell in row)}")
            print(f"Flagged {sum(cell for row in flagged for cell in row)}")
            draw_game_over()
            return

        if check_win():
            draw_grid()
            print(f"Revealed {sum(cell for row in revealed for cell in row)}")
            print(f"Flagged {sum(cell for row in flagged for cell in row)}")
            win = True
            draw_win_message()
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not win:
                x, y = event.pos
                row, col = y // CELL_SIZE, x // CELL_SIZE

                if event.button == 1:  # Left click
                    if (row, col) in mines:
                        game_over = True  # Game over if mine is clicked
                    else:
                        reveal_cells(row, col)

                elif event.button == 3:  # Right click
                    if not revealed[row][col]:  
                        flagged[row][col] = not flagged[row][col]
        ai1()
    pygame.quit()

if __name__ == "__main__":
    main()
    pygame.quit()
