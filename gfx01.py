import pygame
import random as rand

screen_width = 1280
screen_height= 720

fps = 0
fps_counter = 0
fps_frames = 0

def main():
    pygame.init()
    done = False
    screen = pygame.display.set_mode((screen_width, screen_height))

    global green, black, font, clock
    green = pygame.Color(0,255,0)
    black = pygame.Color(0,0,0)
    font = pygame.font.Font('Coders_Crux.ttf', 32)
    clock = pygame.time.Clock()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        x = rand.randrange(screen_width)    
        y = rand.randrange(screen_height)    
        color = pygame.Color(rand.randrange(255),rand.randrange(255),rand.randrange(255))       
        screen.set_at((x,y), color)

        draw_fps(screen)

        #screen.fill(COLOR_BLACK)
        pygame.display.update()
        clock.tick()

    pygame.quit()


def draw_fps(screen):
    global fps_counter, fps_frames, fps, font
    fps_counter += clock.get_time()
    fps_frames += 1
    fps += clock.get_fps()
    if fps_counter >= 1000:
        fps = int(fps / fps_frames)
        fps_frames = 0
        fps_counter -= 500

        pygame.draw.rect(screen, black, (0,0,120,30))
        text_fps = font.render('FPS: %d' % fps, False, green)
        screen.blit(text_fps, (10,10))
        fps = 0


if __name__ == '__main__':
    main()