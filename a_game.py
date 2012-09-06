#!/usr/bin/env python

import pygame
from pygame.locals import *
import resources as res
from map import *
from grid import *
from test_agent import Test_agent 


class Main:
  CLICK_IDLE = 0
  CLICK_ED = 1

  def __init__(self, screen_size=(800, 600)):
    if not pygame.font:
      print "Error: no fonts"
      return

    if not pygame.mixer:
      print "Error: no sound"
      return

    pygame.init()
    
    self.debug_mode = False
    self.click_state = self.CLICK_IDLE

    self.screen_size = screen_size
    self.clock = pygame.time.Clock()

    self.screen = pygame.display.set_mode(self.screen_size)
    pygame.display.set_caption('A Game!')
    print "display driver: ", pygame.display.get_driver()
    print "screen bit depth: ", self.screen.get_bitsize()

    res.resources = res.Resources('data', screen_size)

    ## create game object ##
    self.map = Map('data/sparse_diamond.map', self.screen.get_rect())
    if len(self.map.map_file.startpoints) < 2:
      raise SystemExit, "map does not specify enough startpoints"

    self.grids = []
    for player_i, startpoint in enumerate(self.map.map_file.startpoints):
      self.grids.append(Grid(player_i, self.screen.get_rect(),
          startpoint,
          self.map)) 
      self.map.take_tile(startpoint, player_i)
    self.user_grid = self.grids[0] 

    for g in self.grids:
      g.other_grids = filter(lambda x: x != g, self.grids)

    self.agents = []
    for g in self.grids[1:]:
      self.agents.append(Test_agent(self.map, g))

  def show_fps(self):
    fps = self.clock.get_fps()
    font = res.resources.std_font
    surf = font.render("fps: %.1f" % (fps), 1, (180, 10, 10))
    frame = surf.get_rect()
    frame.right = self.screen.get_width()
    self.screen.blit(surf, frame)

  def left_click(self, pos, player=0):
    ij = self.map.get_index_by_coords(pos)
    print "left click at %s, tile: %s" % (str(pos), str(ij))
    if self.map.is_tile_enabled(ij):
      if self.click_state == self.CLICK_IDLE:
        if not self.map.is_tile_owned(ij, player):
          print "Error: first select one of your tiles"
        else:
          self.click_state = self.CLICK_ED
          self.sel_a = ij
          self.user_grid.select_point(ij)
      elif self.click_state == self.CLICK_ED:
        if not self.map.is_tile_owned(ij):
          print "growing grid to tile %s" % (str(ij))
          self.grids[player].grow(ij, connect_in=self.sel_a)
        elif self.map.is_tile_owned(ij, player):
          self.grids[player].connect(self.sel_a, ij)
        else:
          other_grid = self.grids[self.map.get_owner(ij)]
          self.grids[player].attack(self.sel_a, ij, other_grid)

        self.click_state = self.CLICK_IDLE
        self.user_grid.unselect_point()

  def right_click(self, pos, player=0):
    ij = self.map.get_index_by_coords(pos)
    print "right click at %s, tile: %s" % (str(pos), str(ij))
    if self.map.is_tile_enabled(ij) and self.map.is_tile_owned(ij, player):
      self.user_grid.remove_outbound(ij)

  def game_over(self):
    self.map.draw(self.screen)
    for grid in self.grids:
      grid.draw(self.screen)

    shade = pygame.Surface(self.screen_size)
    shade.fill(pygame.Color(128,128,128,255))
    self.screen.blit(shade, shade.get_rect(), special_flags=BLEND_SUB)

    msg = res.resources.big_font.render("GAME OVER!", 1, (250, 10, 10))
    frame = msg.get_rect(center=self.screen.get_rect().center)
    self.screen.blit(msg, frame)
    pygame.display.flip()

  def you_win(self):
    self.map.draw(self.screen)
    for grid in self.grids:
      grid.draw(self.screen)

    shade = pygame.Surface(self.screen_size)
    shade.fill(pygame.Color(128,128,128,255))
    self.screen.blit(shade, shade.get_rect(), special_flags=BLEND_SUB)

    msg = res.resources.big_font.render("YOU WIN!", 1, (10, 250, 10))
    frame = msg.get_rect(center=self.screen.get_rect().center)
    self.screen.blit(msg, frame)
    pygame.display.flip()

  def main(self):
    while True:
      dt = self.clock.tick(60) / 1000.0
      for event in pygame.event.get():
        if event.type == QUIT:
          return
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
          return
        elif event.type == MOUSEBUTTONUP and event.button == 1:
          self.left_click(event.pos)
        elif event.type == MOUSEBUTTONUP and event.button == 3:
          self.right_click(event.pos)
        elif self.debug_mode and event.type == MOUSEBUTTONUP and event.button == 3:
          self.left_click(event.pos, player=1)

      self.screen.blit(res.resources.background, (0,0))

      if self.user_grid.game_over:
        self.game_over()
      elif all(map(lambda x: x.game_over, self.grids[1:])):
        self.you_win()
      else:
        self.map.update(dt)
        for grid in self.grids:
          grid.update(dt)

        for agent in self.agents:
          agent.work(dt)

        self.map.draw(self.screen)
        for grid in self.grids:
          grid.draw(self.screen)

        self.show_fps()
        pygame.display.flip()


if __name__ == '__main__':
  main = Main()
  main.main()
