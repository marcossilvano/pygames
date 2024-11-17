'''
Very simple PyGame example.

To activate VirtualEnv:
    $ source ../../venv-pygame/bin/activate

Add PyGame lib includes into Pylance extra paths
    ../../venv-pygame/lib/python3.10/site-packages
'''

import sys, pygame, time, copy

# ----- Constantes -------

COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
WIDTH = 1280
HEIGHT= WIDTH*(9/16)
SHIP_SPEED = 300

# ------ Classes ---------

class GameObject():
    x = 0
    y = 0
    speed_x = 0
    speed_y = 0
    width = 0
    height= 0
    rotation = 0
    rect = None
    orig_texture = None
    final_texture = None

# ------ Logic ---------

def should_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            return True
        
    return False


def get_time() -> None:
    time_curr = time.time() * 1000
    time_delay = 1000/60 - (time_curr - time_prev)
    time_prev = time_curr
    time_delay = max(int(time_delay), 0)


def create_game_object(x, y, speed_x, speed_y, texture: str) -> GameObject:
    obj = GameObject()
    obj.orig_texture = pygame.image.load(texture)
    obj.rect = obj.orig_texture.get_rect()
    
    obj.width = obj.rect.width
    obj.height= obj.rect.height
    obj.x = x
    obj.y = y
    obj.speed_x = speed_x
    obj.speed_y = speed_y

    return obj

def update_rect(obj):
    obj.t_texture = pygame.transform.rotate(obj.orig_texture, obj.rotation)
    obj.rect = obj.t_texture.get_rect()
    obj.rect.x = obj.x - obj.rect.width/2
    obj.rect.y = obj.y - obj.rect.height/2


def scale_object(obj, scale=1):
    obj.orig_texture = pygame.transform.scale_by(obj.orig_texture, scale)
    obj.width = obj.orig_texture.get_width()
    obj.height= obj.orig_texture.get_height()


def keep_inside_screen(obj):
    x_border = False
    y_border = False

    if obj.x - obj.width/2 < 0:
        obj.x = obj.width/2
        x_border = True
    elif obj.x > WIDTH - obj.width/2:
        obj.x = WIDTH - obj.width/2
        x_border = True

    if obj.y - obj.height/2 < 0:
        obj.y = obj.height/2
        y_border = True
    elif obj.y > HEIGHT - obj.height/2:
        obj.y = HEIGHT - obj.height/2
        y_border = True

    return (x_border, y_border)


def ball_update(ball, dt):
    ball.x = ball.x + ball.speed_x * dt
    ball.y = ball.y + ball.speed_y * dt

    ret = keep_inside_screen(ball)
    if ret[0]: ball.speed_x = -ball.speed_x
    if ret[1]: ball.speed_y = -ball.speed_y

    ball.rotation += 0.1

    update_rect(ball)


def ship_update(ship, keys, dt):
    ship.speed_x = 0
    ship.speed_y = 0
    dir = 0
    
    if keys[pygame.K_w]:
        ship.speed_y = -SHIP_SPEED
        ship.rotation = 90
        dir = -1
    elif keys[pygame.K_s]:
        ship.speed_y = SHIP_SPEED
        ship.rotation = 270
        dir = 1

    if keys[pygame.K_d]:
        ship.speed_x = SHIP_SPEED
        ship.rotation = 0
        if dir < 0:
            ship.rotation = 45
        elif dir > 0:
            ship.rotation = 270+45
    elif keys[pygame.K_a]:
        ship.speed_x = -SHIP_SPEED
        ship.rotation = 180
        if dir < 0:
            ship.rotation = 90+45
        elif dir > 0:
            ship.rotation = 180+45

    # diagonals
    if ship.speed_x != 0 and ship.speed_y != 0:
        ship.speed_x *= 0.71
        ship.speed_y *= 0.71

    ship.x = ship.x + ship.speed_x * dt
    ship.y = ship.y + ship.speed_y * dt

    keep_inside_screen(ship)

    update_rect(ship)

# ----------- MAIN --------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball PyGame Example")
    
    ball = create_game_object(5, 5, 300, 300, "textures/intro_ball.gif")
    ship = create_game_object(200, 200, SHIP_SPEED, SHIP_SPEED, "textures/ship_32x32.png")
    scale_object(ship, 2)

    clock = pygame.time.Clock()
    time_prev = time.time() * 1000

    font = pygame.font.Font('Coders_Crux.ttf', 32)
    text_fps = font.render('FPS: 60', False, COLOR_GREEN)
    text_rect= text_fps.get_rect()
    text_rect.topleft = (10,10)
    dt = 0

    rotation = 0.0

    # Game Loop
    while not should_quit():
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]: break
        #get_time()

        # --- Update Logic ---
        ball_update(ball, dt)
        ship_update(ship, keys, dt)

        # --- Render Frame ---
        screen.fill(COLOR_BLACK)

        screen.blit(ball.t_texture, ball.rect)
        screen.blit(ship.t_texture, ship.rect)

        text_fps = font.render('FPS: %d' % clock.get_fps(), False, COLOR_GREEN)
        screen.blit(text_fps, text_rect)
        
        pygame.display.flip()

        # --- Keep Sync ---
        dt = clock.tick()/1000 # (60)
        #pygame.time.delay(time_delay)

    sys.exit()

# ------ MAIN ---------

if __name__ == '__main__':
    main()