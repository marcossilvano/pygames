import pygame

def should_quit():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]: 
        return True
        
    return False


class Fps:
    rate = 0
    counter = 0
    frames = 0
    text = None
    font = None

    def __init__(self):
        self.font = pygame.font.Font('Coders_Crux.ttf', 32)
        self.green = pygame.Color(0,255,0)
        self.black = pygame.Color(0,0,0)
        self.text = self.font.render('FPS: 00', False, self.green)


    def draw(self, screen, clock):
        self.counter += clock.get_time()
        self.frames += 1
        self.rate += clock.get_fps()
        if self.counter >= 1000:
            self.rate = int(self.rate / self.frames)
            self.frames = 0
            self.counter -= 500

            pygame.draw.rect(screen, self.black, (0,0,120,30))
            self.text = self.font.render('FPS: %d' % self.rate, False, self.green)
            self.rate = 0

        screen.blit(self.text, (10,10))
