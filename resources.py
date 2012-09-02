import os
import pygame
from pygame.locals import *

def load_image(name, colorkey=None):
  try:
    image = pygame.image.load(name)
  except pygame.error, message:
    print 'Cannot load image:', name
    raise SystemExit, message
  image = image.convert()
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image


class Resources:
  def __init__(self, data_dir, screen_size):
    self.colorkey = pygame.Color(0, 255, 0, 255)

    ## fonts ##
    self.std_font = pygame.font.Font(None, 20)
    self.big_font = pygame.font.Font(None, 50)

    ## images ##
    #self.background = pygame.Surface(screen_size)
    #self.background = self.background.convert()
    #self.background.fill((250, 250, 250))

    self.background = load_image(os.path.join(data_dir,
        'background_galaxy_800x600.png')).convert()
    self.tile = load_image(os.path.join(data_dir, 'tile.png')).convert()
    self.point = load_image(os.path.join(data_dir, 'point.png'),
        colorkey=self.colorkey).convert()


resources = None
