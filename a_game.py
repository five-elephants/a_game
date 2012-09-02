#!/usr/bin/env python

import pygame
from pygame.locals import *
import resources as res
from map import *
from grid import *


class Main:
  def __init__(self, screen_size=(800, 600)):
    if not pygame.font:
      print "Error: no fonts"
      return

    if not pygame.mixer:
      print "Error: no sound"
      return

    pygame.init()

    self.screen_size = screen_size
    self.clock = pygame.time.Clock()

    self.screen = pygame.display.set_mode(self.screen_size)
    pygame.display.set_caption('A Game!')

    res.resources = res.Resources('data', screen_size)

    ## create game object ##
    self.map = Map('data/diamond.map', self.screen.get_rect())
    if len(self.map.map_file.startpoints) < 2:
      raise SystemExit, "map does not specify enough startpoints"

    self.grids = []
    for player_i, startpoint in enumerate(self.map.map_file.startpoints):
      self.grids.append(Grid(player_i, self.screen.get_rect(),
          self.map.ij2xy_c(startpoint),
          self.map)) 
      self.map.take_tile(startpoint, player_i)
    self.user_grid = self.grids[0] 

  def show_fps(self):
    fps = self.clock.get_fps()
    font = res.resources.std_font
    surf = font.render("fps: %.1f" % (fps), 1, (180, 10, 10))
    frame = surf.get_rect()
    frame.right = self.screen.get_width()
    self.screen.blit(surf, frame)

  def left_click(self, pos):
    print "left click at %s" % (str(pos))
    ij = self.map.get_index_by_coords(pos)
    if self.map.is_tile_enabled(ij):
      if not self.map.is_tile_owned(ij):
        print "growing grid to tile %s" % (str(ij))
        self.user_grid.grow(ij)

  def main(self):
    while True:
      self.clock.tick(60)
      for event in pygame.event.get():
        if event.type == QUIT:
          return
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
          return
        elif event.type == MOUSEBUTTONUP:
          self.left_click(event.pos)

      self.screen.blit(res.resources.background, (0,0))

      self.map.update()
      for grid in self.grids:
        grid.update()

      self.map.draw(self.screen)
      for grid in self.grids:
        grid.draw(self.screen)

      self.show_fps()
      pygame.display.flip()


if __name__ == '__main__':
  main = Main()
  main.main()
