from itertools import ifilter
import pygame
from pygame.locals import *
import resources as res
from lib.map_file import *

class Tile(pygame.sprite.Sprite):
  def __init__(self, pos=(0,0)):
    pygame.sprite.Sprite.__init__(self)

    self.image = res.resources.tile
    self.rect = self.image.get_rect()
    self.rect.center = pos


class Map(pygame.sprite.Group):
  def __init__(self, filename, screen_rect):
    pygame.sprite.Group.__init__(self)

    self.tile_size = (res.resources.tile.get_width(),
                      res.resources.tile.get_height())
    self.map_file = load_map(filename)
    self.map_offset = (0,0)
    ## center map on screen ##
    mapc = self.ij2xy_c(self.map_file.center)
    self.map_offset = (
        screen_rect.centerx - mapc[0],
        screen_rect.centery - mapc[1]
    )
    print "centering tile %s with offset %s" % (
        str(self.map_file.center), str(self.map_offset)
    )

    self.tiles = []
    for i in xrange(self.map_file.outer_size[0]):
      row = []
      for j in xrange(self.map_file.outer_size[1]):
        if self.map_file.outer[i][j].has_key('enabled'):
          tile = Tile(self.ij2xy_c((i,j)))
          row.append(tile)
          self.add(tile)

      self.tiles.append(row)

    print "map with outer_size=%s ready" % (
        str(self.map_file.outer_size)
    )


  def ij2xy_c(self, ij):
    """
    Convert map coordiantes (i,j) to screen coordinates (x,y), where (x,y) is
    the center of the tile at coordiantes (i,j).
    """
    y = self.map_offset[1] + (ij[0] * self.tile_size[1]) + (self.tile_size[1]/2)
    x = self.map_offset[0] + (ij[1] * self.tile_size[0]) + (self.tile_size[0]/2)

    return x, y

  def get_index_by_coords(self, xy):
    """
    Find the indices of the tile that contains coordinates xy.
    """

    i = int((xy[1] - self.map_offset[1]) / self.tile_size[1])
    j = int((xy[0] - self.map_offset[0]) / self.tile_size[0])

    return i, j

  def is_tile_enabled(self, ij):
    if( ij[0] >= 0 and ij[0] < len(self.map_file.outer) 
        and ij[1] >= 0 and ij[1] < len(self.map_file.outer[ij[0]]) ):
      return self.map_file.outer[ij[0]][ij[1]].has_key('enabled')
    else:
      return False

  def take_tile(self, ij, player):
    self.map_file.outer[ij[0]][ij[1]]['owner'] = player

  def is_tile_owned(self, ij, player=None):
    if( ij[0] >= 0 and ij[0] < self.map_file.outer_size[0]
        and ij[1] >= 0 and ij[1] < self.map_file.outer_size[1] ):
      rv = self.map_file.outer[ij[0]][ij[1]].has_key('owner')
      if rv and player != None:
        return self.map_file.outer[ij[0]][ij[1]]['owner'] == player
      else:
        return rv
    else:
      return False

  def get_owner(self, ij):
    if self.map_file.outer[ij[0]][ij[1]].has_key('owner'):
      return self.map_file.outer[ij[0]][ij[1]]['owner']
    else:
      return None

  def fields_without_owner(self):
    fil = lambda x: self.is_tile_enabled(x) and not self.is_tile_owned(x)
    return ifilter(fil, [ (i, j) for i in xrange(self.map_file.outer_size[0])
                         for j in xrange(self.map_file.outer_size[1]) ])
