from itertools import ifilterfalse, ifilter, imap
import pygame
from pygame.locals import *
import resources as res
import rules

class Point(pygame.sprite.Sprite):
  def __init__(self, init_val, owner, pos=(0,0)):
    pygame.sprite.Sprite.__init__(self)

    #self.image = res.resources.point 
    self.image = pygame.Surface((64, 64))
    self.image.fill(res.resources.colorkey)
    self.image.set_colorkey(res.resources.colorkey)
    self.rect = self.image.get_rect()
    self.rect.center = pos

    self.owner = owner
    self.value = init_val
    self.kill_me = False

  def update(self, dt):
    state = rules.rules.get_point_state(self.value)
    
    if state == 1:
      self.value += rules.rules.growth_rate * dt
      self.value = min(rules.rules.value_max, self.value)
    elif state == 0:
      self.value -= rules.rules.shrink_rate * dt
      self.value = max(rules.rules.value_min, self.value)

    if self.value <= rules.rules.kill_value:
      self.kill_me = True

    self.image.fill(res.resources.colorkey)

    ## halo
    pygame.draw.circle(self.image,
        res.resources.point_halo_colors[state],
        self.image.get_rect().center,
        max(int(self.value * (self.image.get_width()/2 - 4)), 10))

    ## player color mark
    pygame.draw.circle(self.image,
        res.resources.player_colors[self.owner],
        self.image.get_rect().center,
        int(self.value * (self.image.get_width()/2 - 12)))


class Connection(pygame.sprite.Sprite):
  def __init__(self, owner, xy_a, xy_b, pt_in, pt_out):
    pygame.sprite.Sprite.__init__(self)

    #self.rect = pygame.Rect(
        #min(xy_a[0], xy_b[0])-20, min(xy_a[1], xy_b[1])-20,
        #abs(xy_a[0] - xy_b[0])+40, abs(xy_a[1] - xy_b[1])+40
    #)
    #print "Connection rect: %s" % (self.rect)

    self.owner = owner
    self.point_in = pt_in
    self.point_out = pt_out

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
    pygame.draw.line(self.image,
        res.resources.player_colors[self.owner],
        a, b, 4)
    pygame.draw.aaline(self.image, self.color, a, b, 0)
    pygame.draw.circle(self.image, self.color, b, 5)

    self.timer = 0.0

  def update(self, dt):
    self.timer += dt
    if self.timer > rules.rules.transport_interval:
      if rules.rules.get_point_state(self.point_in.value) >= rules.rules.POINT_STATE_GROWING:
        self.point_in.value -= rules.rules.transport_value
        self.point_out.value += rules.rules.transport_value
        self.point_in.value = max(rules.rules.value_min, self.point_in.value)
        self.point_out.value = min(rules.rules.value_max, self.point_out.value)
      self.timer = 0.0


class Grid(pygame.sprite.Group):
  def __init__(self, player, screen_rect, startpoint, the_map):
    pygame.sprite.Group.__init__(self)

    self.player = player
    self.screen_rect = screen_rect
    self.map = the_map

    ## starting point in grid ##
    sp = Point(rules.rules.source_thresh, player, the_map.ij2xy_c(startpoint))
    self.points = {
        startpoint: sp
    }
    self.add(sp)

    self.connections = []
    self.game_over = False

  def grow(self, ij, connect_in=None):
    pt = Point(rules.rules.new_point_val, self.player, self.map.ij2xy_c(ij))
    self.points[ij] = pt
    self.add(pt)
    self.map.take_tile(ij, self.player)

    if connect_in == None:
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
          con = Connection(
              self.player,
              self.map.ij2xy_c((i,j)),
              self.map.ij2xy_c(ij),
              self.points[(i,j)],
              pt)
          self.connections.append(con)
          self.add(con)
          print "adding connection at %d,%d" % (i,j)
    else:
      con = Connection(
          self.player,
          self.map.ij2xy_c(connect_in),
          self.map.ij2xy_c(ij),
          self.points[connect_in],
          self.points[ij])
      self.connections.append(con)
      self.add(con)
      print "adding connection at %d,%d" % (connect_in[0], connect_in[1])

  def connect(self, ij_in, ij_out):
    con = Connection(
        self.player,
        self.map.ij2xy_c(ij_in),
        self.map.ij2xy_c(ij_out),
        self.points[ij_in],
        self.points[ij_out])
    self.connections.append(con)
    self.add(con)
    print "adding connection from %d,%d to %d,%d" % (
        ij_in[0], ij_in[1], ij_out[0], ij_out[1]
    )

  def update(self, *args):
    pygame.sprite.Group.update(self, *args)

    to_kill = []
    for ij, pt in self.points.iteritems():
      if pt.kill_me:
        to_kill.append(ij)
        pt.kill() # remove from sprite groups
        self.map.map_file.outer[ij[0]][ij[1]].pop('owner')

        ## remove any connections from and to this point ##
        filter = lambda c: c.point_in == pt or c.point_out == pt
        cons_to_rm = ifilter(filter, self.connections)
        print map(lambda c: c.kill(), cons_to_rm)
        self.connections[:] = list(ifilterfalse(filter, self.connections))
    
    for ij in to_kill:
      self.points.pop(ij)
      print "killing %s" % (str(ij))

    if len(self.points) == 0:
      self.game_over = True

