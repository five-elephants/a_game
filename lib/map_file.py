import pickle

class Map_file:
  def __init__(self, name, outer_size):
    self.name = name
    self.outer_size = outer_size
    self.outer = [
        [ {} for i in xrange(outer_size[1]) ]
        for j in xrange(outer_size[0])
    ]
    self.center = (outer_size[0]/2,outer_size[1]/2)
    self.startpoints = []

  def enable_tile(self, i, j):
    self.outer[i][j]['enabled'] = True
  
def save_map(map_file, filename):
  with open(filename, 'wb') as f:
    pickle.dump(map_file, f, protocol=2)


def load_map(filename):
  with open(filename, 'rb') as f:
    rv = pickle.load(f)

  return rv
