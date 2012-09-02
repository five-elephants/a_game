import pygame
from pygame.locals import *
import resources as res

class Point(pygame.sprite.Sprite):
  def __init__(self, pos=(0,0)):
    pygame.sprite.Sprite.__init__(self)

    self.image = res.resources.point 
    self.rect = self.image.get_rect()
    self.rect.center = pos

  def update(self):
    pass


class Connection(pygame.sprite.Sprite):
  def __init__(self, xy_a, xy_b):
    pygame.sprite.Sprite.__init__(self)

    #self.rect = pygame.Rect(
        #min(xy_a[0], xy_b[0])-20, min(xy_a[1], xy_b[1])-20,
        #abs(xy_a[0] - xy_b[0])+40, abs(xy_a[1] - xy_b[1])+40
    #)
    #print "Connection rect: %s" % (self.rect)

    self.image = pygame.Surface(
        (abs(xy_a[0] - xy_b[0]) + 20, abs(xy_a[1] - xy_b[1])+20)
    )
    self.rect = self.image.get_rect()
    self.rect.left = min(xy_a[0], xy_b[0])-10
    self.rect.top = min(xy_a[1], xy_b[1])-10
    self.image.fill(res.resources.colorkey)
    self.image.set_colorkey(res.resources.colorkey)
    self.color = pygame.Color(58, 176, 242, 255)
    a = (xy_a[0] - self.rect.left, xy_a[1] - self.rect.top)
    b = (xy_b[0] - self.rect.left, xy_b[1] - self.rect.top)
    pygame.draw.aaline(self.image, self.color, a, b, 0)

  def update(self):
    pass


class Grid(pygame.sprite.Group):
  def __init__(self, player, screen_rect, startpoint, the_map):
    pygame.sprite.Group.__init__(self)

    self.player = player
    self.screen_rect = screen_rect
    self.map = the_map

    ## starting point in grid ##
    self.points = [
        Point(startpoint)
    ]
    self.add(self.points[0])

    self.connections = []

  def grow(self, ij):
    pt = Point(self.map.ij2xy_c(ij))
    self.points.append(pt)
    self.add(pt)
    self.map.take_tile(ij, self.player)

    for di,dj in [ (0,-1), (0,1), (-1,0), (1,0) ]:
      i = ij[0] + di
      j = ij[1] + dj

      while( i >= 0 and i < self.map.map_file.outer_size[0]
          and j >= 0 and j < self.map.map_file.outer_size[1]
          and not self.map.is_tile_owned((i,j)) ):
        print "testing %d,%d" % (i,j)
        i += di
        j += dj

      if self.map.is_tile_owned((i,j), self.player):
        con = Connection(self.map.ij2xy_c(ij), self.map.ij2xy_c((i,j)))
        self.connections.append(con)
        self.add(con)
        print "adding connection at %d,%d" % (i,j)

