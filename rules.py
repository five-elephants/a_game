
class Rules:
  POINT_STATE_SHRINKING = 0
  POINT_STATE_GROWING = 1
  POINT_STATE_MAX = 2

  def __init__(self):
    self.source_thresh = 0.5
    self.growth_rate = 0.11
    self.shrink_rate = 0.01
    self.value_max = 1.0
    self.value_min = 0.05
    self.kill_value = 0.05
    self.new_point_val = 0.2
    self.transport_interval = 1.0
    self.transport_value = 0.05
    self.attack_interval = 1.2 
    self.attack_invest = 0.09
    self.attack_damage = 0.026

  def get_point_state(self, value):
    if value < self.source_thresh: state = 0
    elif value < self.value_max: state = 1
    else: state = 2

    return state

rules = Rules()
