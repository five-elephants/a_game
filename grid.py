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
  def __init__(self, owner, xy_a, xy_b, pt_in, pt_out, is_attack=False):
    pygame.sprite.Sprite.__init__(self)

    #self.rect = pygame.Rect(
        #min(xy_a[0], xy_b[0])-20, min(xy_a[1], xy_b[1])-20,
        #abs(xy_a[0] - xy_b[0])+40, abs(xy_a[1] - xy_b[1])+40
    #)
    #print "Connection rect: %s" % (self.rect)

    self.owner = owner
    self.point_in = pt_in
    self.point_out = pt_out
    self.u = xy_a
    self.v = xy_b
    self.is_attack = is_attack

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

  def collision_check(a, b):
    if not (type(a) == Connection and type(b) == Connection):
      return False

    print "--- collision check ---"
    print "a: u = (%d, %d), v = (%d, %d)" % (
        a.u[0], a.u[1], a.v[0], a.v[1]
    )
    print "b: u = (%d, %d), v = (%d, %d)" % (
        b.u[0], b.u[1], b.v[0], b.v[1]
    )

    na_x = a.v[1] - a.u[1]
    na_y = -(a.v[0] - a.u[0])
    nb_x = b.v[1] - b.u[1]
    nb_y = -(b.v[0] - b.u[0])

    print "normals for a: %d,%d, b: %d,%d" % (
        na_x, na_y, nb_x, nb_y
    )

    ## test b against a
    ba0_x = b.u[0] - a.u[0]
    ba0_y = b.u[1] - a.u[1]
    ba1_x = b.v[0] - a.u[0]
    ba1_y = b.v[1] - a.u[1]
    sep0_a = ba0_x * na_x + ba0_y * na_y
    sep1_a = ba1_x * na_x + ba1_y * na_y
    print "sep0_a=%d, sep1_a=%d" % (
        sep0_a, sep1_a
    )

    ## test a against b
    ab0_x = a.u[0] - b.u[0]
    ab0_y = a.u[1] - b.u[1]
    ab1_x = a.v[0] - b.u[0]
    ab1_y = a.v[1] - b.u[1]
    sep0_b = ab0_x * nb_x + ab0_y * nb_y
    sep1_b = ab1_x * nb_x + ab1_y * nb_y

    print "sep0_b=%d, sep1_b=%d" % (
        sep0_b, sep1_a
    )

    return (sep0_a * sep1_a) < 0 and (sep0_b * sep1_b) < 0

  def update(self, dt):
    self.timer += dt
    if self.is_attack:
      if self.timer > rules.rules.attack_interval:
        if rules.rules.get_point_state(self.point_in.value) >= rules.rules.POINT_STATE_GROWING:
          self.point_in.value -= rules.rules.attack_invest
          self.point_out.value -= rules.rules.attack_damage
          self.point_in.value = max(rules.rules.value_min, self.point_in.value)
          self.point_out.value = max(rules.rules.value_min, self.point_out.value)
        self.timer = 0.0
    else:
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
    self.other_grids = []

    ## starting point in grid ##
    sp = Point(rules.rules.source_thresh, player, the_map.ij2xy_c(startpoint))
    self.points = {
        startpoint: sp
    }
    self.add(sp)

    self.connections = []
    self.game_over = False

  def grow(self, ij, connect_in):
    pt = Point(rules.rules.new_point_val, self.player, self.map.ij2xy_c(ij))
    self.points[ij] = pt
    self.add(pt)
    self.map.take_tile(ij, self.player)

    con = Connection(
        self.player,
        self.map.ij2xy_c(connect_in),
        self.map.ij2xy_c(ij),
        self.points[connect_in],
        self.points[ij])

    ## collision test ##
    for g in self.other_grids:
      collides = pygame.sprite.spritecollide(con, g, False,
          collided=Connection.collision_check)
      if len(collides) > 0:
        print "collision with opponent"
        return

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

    ## collision test ##
    for g in self.other_grids:
      collides = pygame.sprite.spritecollide(con, g, False,
          collided=Connection.collision_check)
      if len(collides) > 0:
        print "collision with opponent"
        return

    self.connections.append(con)
    self.add(con)
    print "adding connection from %d,%d to %d,%d" % (
        ij_in[0], ij_in[1], ij_out[0], ij_out[1]
    )

  def attack(self, my_ij, his_ij, his_grid):
    con = Connection(
        self.player,
        self.map.ij2xy_c(my_ij),
        self.map.ij2xy_c(his_ij),
        self.points[my_ij],
        his_grid.points[his_ij],
        is_attack=True
    )

    ## collision test ##
    for g in self.other_grids:
      collides = pygame.sprite.spritecollide(con, g, False,
          collided=Connection.collision_check)
      if len(collides) > 0:
        print "collision with opponent"
        return

    self.connections.append(con)
    self.add(con)
    print "adding attack-connection from %d,%d to %d,%d" % (
        my_ij[0], my_ij[1], his_ij[0], his_ij[1]
    )

  def find_outbound(self, ij):
    pt = self.points[ij]
    fil = lambda c: c.point_in == pt
    return ifilter(fil, self.connections)

  def find_inbound(self, ij):
    pt = self.points[ij]
    fil = lambda c: c.point_out == pt
    return ifilter(fil, self.connections)

  def num_points(self):
    return len(self.points)

  def num_enemy_points(self):
    return sum(map(lambda x: x.num_points(), self.other_grids))

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

        ## remove attack-connections from other grids ##
        for g in self.other_grids:
          filter = lambda c: c.point_out == pt 
          cons_to_rm = ifilter(filter, g.connections)
          map(lambda c: c.kill(), cons_to_rm)
          g.connections[:] = list(ifilterfalse(filter, g.connections))
    
    for ij in to_kill:
      self.points.pop(ij)
      print "killing %s" % (str(ij))

    if len(self.points) == 0:
      self.game_over = True

