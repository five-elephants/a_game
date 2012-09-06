import pygame

class Agent:
  def __init__(self, map, grid):
    self.map = map
    self.grid = grid
    self.aps_limit = 0.5  # numbers of actions per second
    self.expand_delay = 1.2  # minimum time until field is retaken
    self.grow_timestamp = {}

  def work(self):
    pass

  def grow(self, to_ij, from_ij):
    """
    This function implements growing to new fields with a minimum latency. This
    will prevent the AI from retaking a field immediately after it was destroyed
    there.
    """
    t = float(pygame.time.get_ticks()) / 1000.0
    print "t = %f" % t
    print self.grow_timestamp
    if not self.grow_timestamp.has_key(to_ij):
      self.grow_timestamp[to_ij] = t
    elif (t - self.grow_timestamp[to_ij]) < self.expand_delay:
      print "limiting growth"
      return
    else:
      self.grid.grow(to_ij, from_ij)
      self.grow_timestamp.pop(to_ij)
      print "growing"
