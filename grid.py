from itertools import ifilterfalse, ifilter, imap
import math
import copy
import pygame
from pygame.locals import *
import resources as res
import rules

class Point(pygame.sprite.Sprite):
  def __init__(self, init_val, owner, pos=(0,0)):
    pygame.sprite.Sprite.__init__(self)

    #self.image = res.resources.point 
    self.image = pygame.Surface((64, 64), SRCALPHA)
    self.image.fill(res.resources.colorkey)
    self.image.set_colorkey(res.resources.colorkey)
    self.rect = self.image.get_rect()
    self.rect.center = pos

    self.owner = owner
    self.value = init_val
    self.kill_me = False
    self.num_inbound = 0
    self.num_outbound = 0
    self.selected = False

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
        max(int(round(self.value * (self.image.get_width()/2 - 4))), 10))
    self.image.blit(res.resources.halo_screen, self.image.get_rect(),
                   special_flags=BLEND_RGBA_MIN)

     
    ## player color mark
    pygame.draw.circle(self.image,
        res.resources.player_colors[self.owner],
        self.image.get_rect().center,
        int(round((self.image.get_width()/4-6))))
    
    pygame.draw.circle(self.image,
                       res.resources.point_inner_color,
                       self.image.get_rect().center,
                       int(round((self.image.get_width()/8-4)))) 
     
    self.image.blit(res.resources.point_screen, self.image.get_rect())
    self.image.fill(res.resources.point_halo_colors[state],
                    pygame.Rect(4, 4, int(round(self.value * 56)), 4))

    for i in xrange(self.num_inbound):
      self.image.fill(res.resources.point_halo_colors[2],
                      pygame.Rect(4, 56 - i*6, 4, 4))

    for i in xrange(self.num_outbound):
      self.image.fill(res.resources.point_halo_colors[0],
                      pygame.Rect(56, 56 - i*6, 4, 4))

    if self.selected:
      pygame.draw.rect(self.image, res.resources.player_colors[self.owner],
                       self.image.get_rect(), 2)
    

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

    extra_size = 70
    self.image = pygame.Surface(
        (abs(xy_a[0] - xy_b[0]) + extra_size, abs(xy_a[1] - xy_b[1])+extra_size),
        SRCALPHA
    )
    self.rect = self.image.get_rect()
    self.rect.left = min(xy_a[0], xy_b[0])-(extra_size/2)
    self.rect.top = min(xy_a[1], xy_b[1])-(extra_size/2)
    #self.image.set_colorkey(res.resources.colorkey)

    self.timer = 0.0

  def collision_check(a, b):
    if not (type(a) == Connection and type(b) == Connection):
      return False

    #print "--- collision check ---"
    #print "a: u = (%d, %d), v = (%d, %d)" % (
        #a.u[0], a.u[1], a.v[0], a.v[1]
    #)
    #print "b: u = (%d, %d), v = (%d, %d)" % (
        #b.u[0], b.u[1], b.v[0], b.v[1]
    #)

    na_x = a.v[1] - a.u[1]
    na_y = -(a.v[0] - a.u[0])
    nb_x = b.v[1] - b.u[1]
    nb_y = -(b.v[0] - b.u[0])

    #print "normals for a: %d,%d, b: %d,%d" % (
        #na_x, na_y, nb_x, nb_y
    #)

    ## test b against a
    ba0_x = b.u[0] - a.u[0]
    ba0_y = b.u[1] - a.u[1]
    ba1_x = b.v[0] - a.u[0]
    ba1_y = b.v[1] - a.u[1]
    sep0_a = ba0_x * na_x + ba0_y * na_y
    sep1_a = ba1_x * na_x + ba1_y * na_y
    #print "sep0_a=%d, sep1_a=%d" % (
        #sep0_a, sep1_a
    #)

    ## test a against b
    ab0_x = a.u[0] - b.u[0]
    ab0_y = a.u[1] - b.u[1]
    ab1_x = a.v[0] - b.u[0]
    ab1_y = a.v[1] - b.u[1]
    sep0_b = ab0_x * nb_x + ab0_y * nb_y
    sep1_b = ab1_x * nb_x + ab1_y * nb_y

    #print "sep0_b=%d, sep1_b=%d" % (
        #sep0_b, sep1_a
    #)

    return (sep0_a * sep1_a) < 0 and (sep0_b * sep1_b) < 0

  def update(self, dt):
    self.timer += dt

    a = (self.u[0] - self.rect.left, self.u[1] - self.rect.top)
    b = (self.v[0] - self.rect.left, self.v[1] - self.rect.top)
    self.image.fill(pygame.Color(0,0,0,0))

    if self.is_attack:
      interval = rules.rules.attack_interval
      if self.timer > interval:
        if rules.rules.get_point_state(self.point_in.value) >= rules.rules.POINT_STATE_GROWING:
          self.point_in.value -= rules.rules.attack_invest
          self.point_out.value -= rules.rules.attack_damage
          self.point_in.value = max(rules.rules.value_min, self.point_in.value)
          self.point_out.value = max(rules.rules.value_min, self.point_out.value)
        self.timer = 0.0
      
      #color_scale = math.exp(-math.sin(self.timer / interval * math.pi))
      t = min(self.timer, interval)
      p = (
        int(self.u[0] - self.rect.left + (self.timer/interval) * (self.v[0] - self.u[0])),
        int(self.u[1] - self.rect.top+ (self.timer/interval) * (self.v[1] - self.u[1])),
      )
      color_scale = max(min(1.0, math.exp(-t/0.3) + math.exp((t - interval)/0.02)), 0.5)
      color = pygame.Color(int(color_scale * res.resources.player_colors[self.owner].r),
                           int(color_scale * res.resources.player_colors[self.owner].g),
                           int(color_scale * res.resources.player_colors[self.owner].b),
                           255)
      #pygame.draw.aaline(self.image, color, a, b, 0)
      #pygame.draw.aaline(self.image, pygame.Color('#ffffff'), a, b, 0)
      pygame.draw.line(self.image, pygame.Color('#ffffff80'), a, b, 3)
      pygame.draw.circle(self.image, res.resources.attack_color, p, 6)
      if interval - self.timer < 0.2:
        r = pygame.Rect(0, 0, 64, 64)
        r.center = b
        color = copy.copy(res.resources.player_colors[self.owner])
        color.a = 128
        self.image.fill(color, r)
    else:
      interval = rules.rules.transport_interval
      if self.timer > interval:
        if rules.rules.get_point_state(self.point_in.value) >= rules.rules.POINT_STATE_GROWING:
          self.point_in.value -= rules.rules.transport_value
          self.point_out.value += rules.rules.transport_value
          self.point_in.value = max(rules.rules.value_min, self.point_in.value)
          self.point_out.value = min(rules.rules.value_max, self.point_out.value)
        self.timer = 0.0

      p = (
        int(self.u[0] - self.rect.left + (self.timer/interval) * (self.v[0] - self.u[0])),
        int(self.u[1] - self.rect.top+ (self.timer/interval) * (self.v[1] - self.u[1])),
      )
      #pygame.draw.line(self.image,
          #res.resources.player_colors[self.owner],
          #a, b, 4)
      pygame.draw.aaline(self.image, res.resources.connection_color, a, b, 0)
      #pygame.draw.line(self.image, res.resources.connection_color, a, b, 1)
      pygame.draw.circle(self.image, res.resources.connection_color, b, 5)
      pygame.draw.circle(self.image, res.resources.transport_color, p, 3)



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
    self.last_sel = None

  def grow(self, ij, connect_in):
    if not self.points.has_key(connect_in):
      return

    pt = Point(rules.rules.new_point_val, self.player, self.map.ij2xy_c(ij))

    con = Connection(
        self.player,
        self.map.ij2xy_c(connect_in),
        self.map.ij2xy_c(ij),
        self.points[connect_in],
        pt)

    ## collision test ##
    for g in self.other_grids:
      collides = pygame.sprite.spritecollide(con, g, False,
          collided=Connection.collision_check)
      if len(collides) > 0:
        print "collision with opponent"
        return

    self.points[ij] = pt
    self.add(pt)
    self.map.take_tile(ij, self.player)
    self.connections.append(con)
    self.add(con)
    print "adding connection at %d,%d" % (connect_in[0], connect_in[1])

  def connect(self, ij_in, ij_out):
    if not self.points.has_key(ij_in) or not self.points.has_key(ij_out):
      return

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

  def remove_outbound(self, ij):
    pt = self.points[ij]
    fil = lambda c: c.point_in == pt
    outbound = ifilter(fil, self.connections)
    map(lambda c: c.kill(), outbound)
    self.connections[:] = list(ifilterfalse(fil, self.connections))


  def num_points(self):
    return len(self.points)

  def num_enemy_points(self):
    return sum(map(lambda x: x.num_points(), self.other_grids))

  def update(self, *args):
    pygame.sprite.Group.update(self, *args)

    to_kill = []
    for ij, pt in self.points.iteritems():
      pt.num_inbound = len(list(self.find_inbound(ij)))
      pt.num_outbound = len(list(self.find_outbound(ij)))

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
  
  def select_point(self, ij):
    if self.last_sel != None:
      if self.points.has_key(self.last_sel):
        self.points[self.last_sel].selected = False
      else:
        self.last_sel = None
    self.points[ij].selected = True
    self.last_sel = ij
  
  def unselect_point(self):
    if self.last_sel != None:
      if self.points.has_key(self.last_sel):
        self.points[self.last_sel].selected = False
      else:
        self.last_sel = None
    
