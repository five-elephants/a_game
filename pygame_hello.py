#!/usr/bin/env python

import pygame
from pygame.locals import *
import random

class Wandering_text:
    def __init__(self, text, color, center, bbox):
        self.font = pygame.font.Font(None, 36)
        self.surface = self.font.render(text, 1, color)
        self.pos = self.surface.get_rect(center=center)
        self.bbox = bbox

    def draw(self, screen):
        screen.blit(self.surface, self.pos)

    def update(self):
        self.pos.left += (random.random() - 0.5) * 10.0
        self.pos.top += (random.random() - 0.5) * 10.0

        if self.pos.left < self.bbox.left:
            self.pos.left = self.bbox.left + (self.bbox.left - self.pos.left)
        elif self.pos.right > self.bbox.right:
            self.pos.right = self.bbox.right - (self.bbox.right - self.pos.right)
        elif self.pos.top < self.bbox.top:
            self.pos.top = self.bbox.top + (self.bbox.top - self.pos.top)
        elif self.pos.bottom > self.bbox.bottom:
            self.pos.bottom = self.bbox.bottom - (self.bbox.bottom - self.bbox.top)

def show_fps(screen, fps):
    font = pygame.font.Font(None, 18)
    surf = font.render("fps: %.1f" % (fps), 1, (180, 10, 10))
    frame = surf.get_rect()
    frame.right = screen.get_width()
    screen.blit(surf, frame)


def main():
    if not pygame.font:
        print "Error: no fonts"
        return

    if not pygame.mixer:
        print "Error: no sound"
        return

    random.seed()

    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Hello World')

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0,0))

    #if pygame.font:
        #font = pygame.font.Font(None, 36)
        #text = font.render("Hello World", 1, (10, 10, 10))
        #textpos = text.get_rect(centerx=background.get_width()/2)
        #background.blit(text, textpos)

    hello = Wandering_text("Hello World", (10, 10, 10),
            center=(screen.get_width()/2, screen.get_height()/2),
            bbox=screen.get_rect())

    pygame.display.flip()

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            
        screen.blit(background, (0,0))
        hello.update()
        hello.draw(screen)
        show_fps(screen, clock.get_fps())
        pygame.display.flip()

if __name__ == '__main__':
    main()
