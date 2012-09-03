import random
from agent import *
from rules import rules

class Test_agent(Agent):
  def __init__(self, map, grid):
    Agent.__init__(self, map, grid)

    self.expand_thresh = 0.9 
    self.outbound_per_point = 2
    self.attack_advantage = 3
    self.attacker_outbound = 0

  def work(self):
    if self.grid.num_points() - self.grid.num_enemy_points() > self.attack_advantage:
      self.attack()
    else:
      self.expand()

  def expand(self):
    acts = []
    for ij,pt in self.grid.points.iteritems():
      num_out = len(list(self.grid.find_outbound(ij)))
      if pt.value >= self.expand_thresh and num_out < self.outbound_per_point:
        to_ij = self.find_expansion_pos(ij)
        if to_ij != None:
          acts.append((to_ij, ij))
          break

    for a in acts:
      self.grid.grow(a[0], a[1])

  def find_expansion_pos(self, ij):
    free = list(self.map.fields_without_owner())
    random.shuffle(free)
    dist_key = lambda x: (x[0] - ij[0])**2 + (x[1] - ij[1])**2
    free_by_dist = sorted(free, key=dist_key)
    if free_by_dist:
      return free_by_dist[0]
    else:
      return None

  def attack(self):
    for ij,pt in self.grid.points.iteritems():
      num_out = len(list(self.grid.find_outbound(ij)))
      if num_out <= self.attacker_outbound:
        target,his_grid = self.find_target(ij)
        if target != None:
          self.grid.attack(ij, target, his_grid)

  def find_target(self, ij):
    enemies = []
    for g in self.grid.other_grids:
      enemies.extend([ (ij, g) for ij in g.points.iterkeys() ])

    dist_key = lambda x: (x[0][0] - ij[0])**2 + (x[0][1] - ij[1])**2
    sorted_enemies = sorted(enemies, key=dist_key)
    if sorted_enemies:
      return sorted_enemies[0][0], sorted_enemies[0][1]
    else:
      return None,None


