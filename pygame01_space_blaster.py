'''
Space Blaster.

To activate VirtualEnv:
    $ source ../../venv-pygame/bin/activate

Add PyGame lib includes into Pylance extra paths
    ../../venv-pygame/lib/python3.10/site-packages
'''

import sys, pygame, random

# ----- Constants -------

COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)

WIDTH = 1280
HEIGHT= WIDTH*(9/16)

SHIP_SPEED = 300

STATE_ALIVE = 0
STATE_DEAD  = 1

MOVE_H = 0
MOVE_V = 1

ANIM_MOVE = 0
ANIM_EXPLODE  = 1
ANIM_HIT      = 2
ANIM_LEFT     = 3
ANIM_RIGHT    = 4

FRAME_STOP = -1
FRAME_RTA  = -2

TAG_SHIP  = 0
TAG_ENEMY = 1

levels=[
"""  
     X X       X X
       X X   X X  
         x x x 
       x x   x x
     o o o o o o o


     bbb  bbb  bbb
"""
]

# ------ Classes ---------

class Animation:
    frame_duration = 0
    time_count  = 0
    curr_frame = 1
    curr_anim = 0
    anims: dict = None

class GameObject:
    x = 0
    y = 0
    speed_x = 0
    speed_y = 0
    min_x = 0
    max_x = 0
    
    width = 0
    height= 0
    texture = None
    
    health = 0
    state = STATE_ALIVE    
    move = MOVE_H
    move_count = 0
    anim: Animation = None

    tag = 0
    fire_count = 0
    fire_count_max = 0

class Background:
    scroll = 0
    scroll_speed = 0
    texture = None

# ------ Globals --------

ship: GameObject = None
ships: list = []
enemies: list = []
bullets_ship: list = []
bullets_enem: list = []
shields: list = []
textures: list = {}

# ------- Logic ---------

def should_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            return True
        
    return False

def load_image(image_path: str, has_alpha: bool = True) -> pygame.Surface:
    global textures
    if image_path not in textures:
        if has_alpha:
            textures[image_path] = pygame.image.load(image_path).convert_alpha()    # textures cache (only load once)
        else:
            textures[image_path] = pygame.image.load(image_path).convert()

    return textures[image_path]

def create_game_object(x, y, speed_x, speed_y, scale, width, height, health, image_path: str):
    obj: GameObject = GameObject()

    obj.texture = load_image(image_path)
    obj.x = x
    obj.y = y
    obj.speed_x = speed_x
    obj.speed_y = speed_y
    obj.min_x = 0
    obj.max_x = WIDTH
    obj.width = width
    obj.height = height
    obj.health = health

    obj.anim = Animation()
    obj.anim.curr_anim = ANIM_MOVE
    obj.anim.anims = {}
    obj.anim.frame_duration = 0.3
    #obj.anim.total_frames = obj.texture.get_rect().width // width

    scale_object(obj, scale)

    return obj

def scale_object(obj, scale=1):
    obj.texture = pygame.transform.scale_by(obj.texture, scale)
    obj.width *= scale
    obj.height*= scale

def clamp(value, min, max):
    new_value = value
    overflow = False
    
    if value < min:
        new_value = min
        overflow = True
    elif value > max:
        new_value = max
        overflow = True

    return (new_value, overflow)

def keep_inside_bounds(obj):
    check_x = clamp(obj.x, obj.min_x, obj.max_x)
    obj.x = check_x[0]
    
    check_y = clamp(obj.y, 0, HEIGHT - obj.height)
    obj.y = check_y[0]

    return (check_x[1],check_y[1])

def set_animation(obj: GameObject, anim: str):
    # reassure anim index is ok
    #anim = min(anim, len(obj.anim.anims))

    obj.anim.curr_anim = anim
    obj.anim.curr_frame = 1
    obj.anim.time_count = 0
    obj.anim.frame_duration = obj.anim.anims[anim][0] # first position cotains delay

def check_collision(obj1: GameObject, obj2: GameObject):
    if obj1.state == STATE_DEAD or obj2.state == STATE_DEAD:
        return False
    '''
      r1.left    <     r2.right   
        +------------+
        |     R1     |
        |      +----------+
        +------|-----+    |
               |    R2    |
               +----------+
           r2.left  <  r1.right
    '''
    r1 = pygame.Rect(obj1.x - obj1.width//2, obj1.y - obj1.height//2, obj1.width, obj1.height)
    r2 = pygame.Rect(obj2.x - obj2.width//2, obj2.y - obj2.height//2, obj2.width, obj2.height)

    if r1.left < r2.right and r2.left < r1.right and r1.top < r2.bottom and r2.top < r1.bottom:
        return True

    return False

def hit_game_object(obj: GameObject):
    obj.health -= 1
    if obj.health <= 0:
        set_animation(obj, ANIM_EXPLODE)
        obj.state = STATE_DEAD
    else:
        set_animation(obj, ANIM_HIT)

def check_collision_lists(bul_list, list2):
    for bul in bul_list:
        for obj2 in list2:
            if check_collision(bul, obj2):
                hit_game_object(bul)
                hit_game_object(obj2)
                return True
            
    return False

def create_background(texture, scroll_speed, has_alpha = True):
    bg: Background = Background()
    bg.texture = load_image(texture, has_alpha)
    bg.texture = pygame.transform.scale_by(bg.texture, WIDTH/bg.texture.get_width())
    bg.scroll = 0
    bg.scroll_speed = scroll_speed
    return bg

def blit_background(screen: pygame.Surface, bg: Background, dt: float):
    for i in range (0,2):
        screen.blit(bg.texture, (bg.texture.get_width()*i + bg.scroll, 0))
    bg.scroll -= bg.scroll_speed * dt
    if bg.scroll < -bg.texture.get_width():
        bg.scroll = 0

def blit_game_object(screen: pygame.Surface, obj: GameObject, dt: float):
    has_ended = False
    
    animation = obj.anim.anims[obj.anim.curr_anim]

    # animate
    obj.anim.time_count += dt
    if obj.anim.time_count >= obj.anim.frame_duration:
        obj.anim.time_count -= obj.anim.frame_duration
        obj.anim.curr_frame += 1
        if obj.anim.curr_frame == len(animation):
            obj.anim.curr_frame = 1

    # one-shot animation
    frame = animation[obj.anim.curr_frame]
    if frame == FRAME_STOP:
        obj.anim.curr_frame -= 1
        has_ended = True

    # return to animation
    elif frame == FRAME_RTA:
        next_anim = animation[obj.anim.curr_frame+1]
        set_animation(obj, next_anim)
        animation = obj.anim.anims[obj.anim.curr_anim]

    # draw
    offset = animation[obj.anim.curr_frame]
    pos = (obj.x - obj.width//2, obj.y - obj.height//2)
    clip = (offset * obj.width,0,obj.width,obj.height)
    screen.blit(obj.texture, pos, clip)

    return has_ended

def blit_list(screen, list, dt):
    for obj in list.copy(): 
        has_ended = blit_game_object(screen, obj, dt)
        if obj.anim.curr_anim == ANIM_EXPLODE and has_ended:
            list.remove(obj)

#---- Create Entities ----

def create_bullet(x, y, speed_y, texture):
    bullet = create_game_object(x, y, 0, speed_y, 1.5, 10, 15, 1, texture)
    bullet.anim.anims[ANIM_MOVE]    = [0.05,0,1]
    bullet.anim.anims[ANIM_EXPLODE] = [0.05,2,3,4,FRAME_STOP]
    return bullet

def create_ship() -> GameObject:
    ship = create_game_object((WIDTH-64)/2, HEIGHT-50, SHIP_SPEED, 0, 1.5, 32, 32, 3, "textures/ship_32x32.png")
    ship.min_x = 100
    ship.max_x = WIDTH-100
    ship.fire_count_max = 0.5
    ship.anim.anims[ANIM_MOVE]    = [1.0,0]
    ship.anim.anims[ANIM_EXPLODE] = [0.05,3,4,5,6,7,8]
    ship.anim.anims[ANIM_HIT]     = [0.05,9,0,9,0,9,0,FRAME_RTA,ANIM_MOVE]
    ship.anim.anims[ANIM_LEFT]    = [1.0,1]
    ship.anim.anims[ANIM_RIGHT]   = [1.0,2]
    return ship

def create_enemy(x, y, fire_delay, health, scale, texture):
    en = create_game_object(x, y, 100, 100, scale, 32, 32, health, texture)
    en.min_x = en.x - 300
    en.max_x = en.x + 300
    en.fire_count_max = fire_delay
    en.anim.anims[ANIM_MOVE]    = [0.3,0,1]
    en.anim.anims[ANIM_EXPLODE] = [0.05,2,3,4,5,FRAME_STOP]
    en.anim.anims[ANIM_HIT]     = [0.05,0,6,0,6,0,6,FRAME_RTA,ANIM_MOVE]
    return en

def create_shield(x, y):
    shield = create_game_object(x, y, 0, 0, 1.0, 50, 50, 3, "textures/shield_50x50.png")
    shield.anim.anims[ANIM_MOVE]    = [1.0,0]
    shield.anim.anims[ANIM_EXPLODE] = [0.05,1,2,3,FRAME_STOP]
    shield.anim.anims[ANIM_HIT]     = [0.05,1,4,1,4,1,4,FRAME_RTA,ANIM_MOVE]
    return shield

def init_map(current_level):
    global enemies
    global shields

    padding_x = 50
    padding_y = 70

    row, col = 0, 0
    level_str = levels[current_level]

    # cria os inimigos baseado no mapa do level
    for ch in level_str:
        x = col*padding_x + padding_x/2
        y = row*padding_y
        match ch:
            case 'o': enemies.append(create_enemy(x, y, 0.5, 1, 1.0, "textures/enemy_purple_32x32.png"))
            case 'x': enemies.append(create_enemy(x, y, 1.0, 2, 1.5, "textures/enemy_purple_32x32.png"))
            case 'X': enemies.append(create_enemy(x, y, 2.0, 4, 2.0, "textures/enemy_purple_32x32.png"))
            case 'b': shields.append(create_shield(x, y))
            case '\n': 
                row += 1
                col = 0
        col += 1

#----- Update Entities Logic -----

def update_ship(keys, dt):
    global ship
    
    if ship.state == STATE_DEAD:
        return
    
    ship.speed_x = 0
    if keys[pygame.K_d]:
        ship.speed_x = SHIP_SPEED
    elif keys[pygame.K_a]:
        ship.speed_x = -SHIP_SPEED

    if ship.anim.curr_anim != ANIM_HIT:
        if ship.speed_x == 0:
            set_animation(ship, ANIM_MOVE)
        elif ship.speed_x > 0:
            set_animation(ship, ANIM_RIGHT)
        elif ship.speed_x < 0:
            set_animation(ship, ANIM_LEFT)

    ship.fire_count += dt
    if keys[pygame.K_w]:
        if ship.fire_count >= ship.fire_count_max:
            ship.fire_count = 0
            bullets_ship.append(create_bullet(ship.x, ship.y, -700, "textures/bullet_10x15.png"))

    ship.x = ship.x + ship.speed_x * dt

    keep_inside_bounds(ship)

def update_enemies(dt):
    global enemies

    for en in enemies:
        if en.state == STATE_DEAD:
            continue

        if en.move == MOVE_H:
            en.x = en.x + en.speed_x * dt
            
            bounds = keep_inside_bounds(en)
            if bounds[0]:
                en.speed_x = -en.speed_x
                en.move = MOVE_V
                en.move_count = 0

        if en.move == MOVE_V:
            en.y = en.y + en.speed_y * dt
            en.move_count += dt

            if en.move_count >= 0.3:
                en.move_count = 0
                en.move = MOVE_H

        en.fire_count += dt
        if en.fire_count >= en.fire_count_max:
            en.fire_count = 0
            if random.randint(1,5) == 1:
                bullets_enem.append(create_bullet(en.x, en.y, 300, "textures/bullet_enemy_10x15.png"))

def update_bullets(bullets, dt):
    for bul in bullets:
        if bul.state == STATE_DEAD: 
            continue

        bul.y = bul.y + bul.speed_y * dt
        
        bounds = keep_inside_bounds(bul)
        if bounds[1]:
            bullets.remove(bul)

# ----------- MAIN --------------

def print_flags(surf: pygame.Surface):
    flags = surf.get_flags()
    print('Surface in vram') if flags & 0x00000001 else print('Surface in vram')
    print('Blit in hardware') if flags & 0x00000100 else print('Blit in software')

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Ball PyGame Example")
    
    global ship, enemies, bullets_ship, bullets_enem, shields

    level = 0
    ship = create_ship()
    ships.append(ship)
    init_map(level)

    bg1 = create_background("textures/background_stars.png", 20, False)
    bg2 = create_background("textures/background_stars_fg.png", 60)

    clock = pygame.time.Clock()

    font = pygame.font.Font('Coders_Crux.ttf', 32)
    text_fps = font.render('HUD', False, COLOR_GREEN).convert_alpha()
    text_rect= text_fps.get_rect()
    text_rect.topleft = (10,10)
    dt = 0

    print_flags(bg1.texture)

    # Game Loop
    while not should_quit():
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]: break

        # --- Update Logic ---
        update_ship(keys, dt)
        update_enemies(dt)
        update_bullets(bullets_ship, dt)
        update_bullets(bullets_enem, dt)

        # ---- Collisions ----
        check_collision_lists(bullets_ship, shields)
        check_collision_lists(bullets_enem, shields)
        check_collision_lists(bullets_ship, enemies)
        check_collision_lists(bullets_enem, ships)
        check_collision_lists(enemies, ships)

        # --- Render Frame ---
        screen.fill(COLOR_BLACK)

        blit_background(screen, bg1, dt)
        blit_background(screen, bg2, dt)
        blit_list(screen, bullets_ship, dt)
        blit_list(screen, bullets_enem, dt)
        blit_game_object(screen, ship, dt)
        blit_list(screen, enemies, dt)
        blit_list(screen, shields, dt)

        text_fps = font.render('FPS: %d  Enemies: %d  Health: %d' % (clock.get_fps(), len(enemies), ship.health), False, COLOR_GREEN)
        screen.blit(text_fps, text_rect)
        pygame.display.flip()

        # --- Keep Sync ---
        dt = clock.tick()/1000 # (60)

    sys.exit()

if __name__ == '__main__':
    main()



'''
def get_time() -> None:
    time_curr = time.time() * 1000
    time_delay = 1000/60 - (time_curr - time_prev)
    time_prev = time_curr
    time_delay = max(int(time_delay), 0)
'''