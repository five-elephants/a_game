import os
import pygame
from pygame.locals import *

def load_image(name, colorkey=None):
  try:
    image = pygame.image.load(name)
  except pygame.error, message:
    print 'Cannot load image:', name
    raise SystemExit, message
  #image = image.convert()
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image


class Resources:
  def __init__(self, data_dir, screen_size):
    ## fonts ##
    self.std_font = pygame.font.Font(None, 20)
    self.big_font = pygame.font.Font(None, 50)

    ## colors ##
    self.colorkey = pygame.Color(0, 255, 0, 0)
    self.player_colors = [
        pygame.Color('#d91a1a'),
        pygame.Color('#1a5cd9'),
    ]
    self.point_halo_colors = [
        pygame.Color('#8db6d9ef'),
        pygame.Color('#d9ca8def'),
        pygame.Color('#91d98def'),
    ]
    self.point_inner_color = pygame.Color('#cfcd5d')
    self.connection_color = pygame.Color('#cbe1e6')
    self.transport_color = pygame.Color('#67d0e6')

    ## images ##
    #self.background = pygame.Surface(screen_size)
    #self.background = self.background.convert()
    #self.background.fill((250, 250, 250))

    self.background = load_image(os.path.join(data_dir,
        'background_galaxy_800x600.png')).convert()
    self.tile = load_image(os.path.join(data_dir, 'tile.png')).convert()
    self.point = load_image(os.path.join(data_dir, 'point.png'),
        colorkey=self.colorkey).convert()
    self.point_screen = load_image(os.path.join(data_dir, 'point_screen.png')).convert_alpha()
    self.halo_screen = load_image(os.path.join(data_dir, 'halo_screen.png')).convert_alpha()


resources = None
