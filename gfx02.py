import pygame
import random as rand
import utils

screen_width = 1600
screen_height= 900
fps = None

def main():
    pygame.init()

    done = False
    screen = pygame.display.set_mode((screen_width, screen_height))

    global green, black, font, clock, fps
    fps = utils.Fps()
    green = pygame.Color(0,255,0)
    white = pygame.Color(255,255,255)
    black = pygame.Color(0,0,0)

    clock = pygame.time.Clock()

    x_orign = int(screen_width/2)
    y_orign = int(screen_height/2)
    slope = 0

    while not done:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_d]: 
            slope += 0.01
        elif keys[pygame.K_s] or keys[pygame.K_a]: 
            slope -= 0.01

        if keys[pygame.K_ESCAPE]: 
            done = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                done = True

        screen.fill(black)
                
        # x axis
        for x in range(screen_width):
            screen.set_at((x, y_orign), green)

        # y axis
        for y in range(screen_height):
            screen.set_at((x_orign, y), green)

        # draw line
        for x in range(-x_orign, x_orign):
            y = slope * x + 0 # line equation
            screen.set_at((int(x)+x_orign, int(y)+y_orign), white)

        fps.draw(screen, clock)

        pygame.display.update()
        clock.tick()

    pygame.quit()



if __name__ == '__main__':
    main()