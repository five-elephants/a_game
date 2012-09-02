from lib.map_file import *

def create_plain_map(fn, size):
  """
  Create a simple rectangular map with identical tiles.
  """
  
  m = Map_file(fn, size)
  for i in xrange(size[0]):
    for j in xrange(size[1]):
      m.enable_tile(i, j)

  save_map(m, fn)

def create_diamond_map(fn, base_width, height):
  """
  Create a diamond shaped map.

      x ..[base_width].. x
     xx                  xx
          ..[height]..
     xx                  xx
      x                  x
  """

  size = (2*height + 1, base_width + 2*height)
  m = Map_file(fn, size)

  print "map of outer size %d, %d" % (size[0], size[1])

  for i in xrange(height+1):
    for j in xrange(height-i, height+base_width+i):
      print "enabling tile %d, %d" % (i, j)
      m.enable_tile(i, j)

  for i in xrange(height+1, 2*height+1):
    for j in xrange(height - (2*height-i), height+base_width + (2*height-i)):
      print "enabling tile %d, %d" % (i, j)
      m.enable_tile(i, j)

  m.center = (3,4)
  m.startpoints = [ (0, 4), (6, 4) ]
  save_map(m, fn)

if __name__ == '__main__':
  create_diamond_map('data/diamond.map', 3, 3)
