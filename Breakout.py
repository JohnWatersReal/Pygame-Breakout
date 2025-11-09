import math
import pygame, sys, random
from pygame.locals import*

pygame.init()

# Window Settings
window_width = 900
window_height = 1000

# Creating Colours
black = pygame.Color(0, 0, 0)
green = pygame.Color(0, 255, 0)
red = pygame.Color(255, 0, 0)
grey = pygame.Color(128, 128, 128)
white = pygame.Color(255, 255, 255)
blue = pygame.Color(0, 0, 255)

# Display Setup
DISPLAYSURF = pygame.display.set_mode((window_width,window_height))
DISPLAYSURF.fill(black)

# Setting Framerate
FPS = 60
FramePerSec = pygame.time.Clock()

# Setting window title
pygame.display.set_caption("Game")

# Setting up fonts
score_font = pygame.font.SysFont("Comic_sans", 60)
high_score_font = pygame.font.SysFont("Comic_sans", 30, False, True)

# Setting up pause screen
pause_rect = Rect(window_width/3, window_height/3, window_width/3, window_height/3)

# Constants
ball_speed_x = 4
ball_speed_y = 2 * ball_speed_x
ball_vector = pygame.Vector2(ball_speed_x, ball_speed_y)
player_width = 100
relic_width = 20
relic_height = 20

# Transition states
GAME_STATE = 0
PLAY_SCREEN = 0
RELIC_SCREEN = 1

class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__()
        self.x = 400
        self.y = 850
        self.surf = pygame.Surface((player_width, 20))
        self.rect = self.surf.get_rect(topleft=(self.x, self.y))
        
    def handle_keys(self):
        key = pygame.key.get_pressed()
        dx = 10
        if key[pygame.K_LEFT]:
            self.rect = self.rect.move(-dx, 0)
        elif key[pygame.K_RIGHT]:
            self.rect = self.rect.move(dx, 0)
            
    def draw(self, surface):
        pygame.draw.rect(surface, grey, self.rect, 0, 8)
        #pygame.draw.line(surface, red, (self.rect.x, self.rect.y), (self.rect.right, self.rect.y)) - uncomment to see hitbox
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__() 
        self.surf = pygame.Surface((100, 20))    
        self.rect = self.surf.get_rect(topleft=(x, y))  
        
    def draw(self, surface):
        pygame.draw.rect(surface, grey, self.rect)
            
class Projectile(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.surf = pygame.Surface((20, 20))
        self.rect = self.surf.get_rect(center=(player.x + player.surf.get_width()/2, player.y - 16))
        self.vector = ball_vector
        
    def draw(self, surface):
        #pygame.draw.rect(surface, blue, self.rect) - uncomment to draw hitbox
        pygame.draw.circle(surface, grey, self.rect.center, 10)
        
    def move(self):
        self.rect.x += self.vector.x
        self.rect.y += self.vector.y
        if (self.rect.x - 10 <= 0 or self.rect.x + 10 >= window_width):
            self.vector.x *= -1
        if (self.rect.y - 10 <= 0):
            self.vector.y *= -1
            
class Relic(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((relic_width, relic_height))
        self.rect = self.surf.get_rect()
        
    def on_pickup():
        return
    
class Lengthen(Relic):
    def __init__(self):
        super().__init__()
        self.name = "Lengthen"
        self.desc = "Extend the paddle by 15%"
        self.surf.fill(green)
            
def spawn(xNumber, yNumber, array):
    for y in range(yNumber):
        for x in range(xNumber):
            enemy = Enemy((window_width - ((100 * xNumber) + 10 * (xNumber - 1)))/2 + x * 110, 200 + y * 30)
            array.append(enemy)
              

def pause_check(paused):
    while (paused):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit() # close pygame window
                sys.exit()    # stop the python script
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    paused = False 

def do_relic_loop():
    DISPLAYSURF.fill(black)

def do_play_loop():
    # Draw the background
    DISPLAYSURF.fill(black)
                
    # handle the player
    player.draw(DISPLAYSURF)
    projectile.move()
    player.handle_keys()
    
    # Draw the circle
    projectile.draw(DISPLAYSURF)   

    # If circle hits bouncer
    if pygame.Rect.colliderect(player.rect, projectile.rect):
        if (projectile.rect.y >= player.rect.y):
            projectile.vector.x *= -1
        else:
            projectile.rect.bottom = player.rect.top
            # Calculate where on the paddle it hit
            hit_pos = (projectile.rect.x - player.rect.x) / (player_width / 2)

            # Clamp between -1 (left) and 1 (right)
            hit_pos = max(-1, min(1, hit_pos))
            max_angle = 67
            angle = math.radians(hit_pos * max_angle)

            # Make vector using the angle
            speed = projectile.vector.length()
            projectile.vector = pygame.Vector2(speed * math.sin(angle), -speed * math.cos(angle))
            
    # If projectile hits enemy
    i = projectile.rect.collidelist(enemies)
    if (i != -1):
        enemy = enemies[i]
        relx = projectile.rect.centerx - enemy.rect.x
        rely = projectile.rect.centery - enemy.rect.y
        if (relx < abs(projectile.vector.x) and relx <= rely and relx + rely <= 20):
            projectile.vector.x *= -1
            projectile.rect.right = enemy.rect.left
        elif (relx > 100 - abs(projectile.vector.x) and relx + rely >= 100 and relx - rely >= 80):
            projectile.vector.x *= -1
            projectile.rect.left = enemy.rect.right
        elif (rely < abs(projectile.vector.y) and relx > rely and relx + rely < 100):
            projectile.vector.y *= -1
            projectile.rect.bottom = enemy.rect.top
        elif (rely > 20 - abs(projectile.vector.y) and relx + rely > 20 and relx - rely < 80):
            projectile.vector.y *= -1
            projectile.rect.top = enemy.rect.bottom

        enemies.remove(enemy)
    
    i = -1
    
    # Spawn enemies
    for entity in enemies:
        entity.draw(DISPLAYSURF)
    if not enemies:
        spawn(3, 2, enemies)
        return RELIC_SCREEN
    else:
        return PLAY_SCREEN
        

# Global variables
player = Player()
projectile = Projectile(player)
enemies = []
relic = Lengthen()


# ===== GAME LOOP BEGIN ===== #
while True:
    
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit() # close pygame window
            sys.exit()    # stop the python script
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.draw.rect(DISPLAYSURF, white, pause_rect)
                paused = score_font.render("PAUSED", True, black)
                rect = paused.get_rect(center=(window_width/2, window_height/2))
                DISPLAYSURF.blit(paused, rect)
                pygame.display.update()
                pause_check(True)
                
    if not enemies:
        spawn(2, 2, enemies)
    if GAME_STATE == PLAY_SCREEN:
       GAME_STATE = do_play_loop()
    elif GAME_STATE == RELIC_SCREEN:
        do_relic_loop()
    
    #player.rect.centerx = projectile.rect.centerx #- uncomment to autoplay
    
    
    pygame.display.update()
    FramePerSec.tick(FPS)
    
# Show score - for reference
    # score_string = score_font.render(("Score: " + str(score)), True, white)
    # DISPLAYSURF.blit(score_string, (30, 30))
    # high_score_text = high_score_font.render(("High Score: " + str(high_score)), True, white)
    # DISPLAYSURF.blit(high_score_text, (30, 120))
    