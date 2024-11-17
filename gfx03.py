import pygame
import random as rand
import utils as lib

screen_width = 1600
screen_height= 900
fps = None

def main():
    pygame.init()

    done = False
    screen = pygame.display.set_mode((screen_width, screen_height))

    global green, black, clock, fps
    fps = lib.Fps()
    green = pygame.Color(0,255,0)
    white = pygame.Color(255,255,255)
    black = pygame.Color(0,0,0)

    clock = pygame.time.Clock()

    x_origin = int(screen_width/2)
    y_origin = int(screen_height/2)
    slope = 0
    times_clicked = 0
    lines = []

    done = False
    while not done:
        done = lib.should_quit()
        screen.fill(black)
        draw_axis(screen, x_origin, y_origin)
        fps.draw(screen, clock)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                done = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if times_clicked == 0:
                    point1 = pygame.mouse.get_pos()
                else:
                    point2 = pygame.mouse.get_pos()
                
                times_clicked += 1
                if times_clicked > 1:
                    lines.append((point1, point2))
                    times_clicked = 0

        for line in lines:
            pygame.draw.line(screen, white, line[0], line[1], 1)

        pygame.display.update()
        clock.tick()

    pygame.quit()


def draw_axis(screen, x_origin, y_origin):
    # x axis
    for x in range(screen_width):
        screen.set_at((x, y_origin), green)

    # y axis
    for y in range(screen_height):
        screen.set_at((x_origin, y), green)


if __name__ == '__main__':
    main()