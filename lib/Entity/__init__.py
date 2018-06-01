from threading import Thread
from functools import wraps

entity_callback_queue = []

# Async wrapper for offloading processes to the background.{{{
def _async(func):
  @wraps(func)
  def async_func(*args, **kwargs):
    func_hl = Thread(target = func, args = args, kwargs = kwargs)
    func_hl.start()
    return func_hl
  return async_func
#}}}
  
# Sync wrapper to add function calls to entity_callback_queue.{{{
def sync(func):
  @wraps(func)
  def sync_func(*args, **kwargs):
    def sync_callback(_dt):
      func(*args, **kwargs)
    entity_callback_queue.append(sync_callback)
  return sync_func
#}}}

# Processes that consistently tick in the same manor.{{{
class System:
  def __init__(self):
    #expected components
    self.component_filter = []
    self.nodes = []
  def add(self, _component):
    pass # get the nodes to process

  def remove(self, _component):
    pass # cleanup

  def tick(self, _delta = 0):
    pass # do update
#}}}

# Collections of components{{{
class Entity:
  def __init__(self):
    # Is added to engine
    self.added = False
    self.components = []
#}}}

# Pieces of an Entity that contains nodes
class Component:
  pass

# Pieces of data shared between components and systems{{{
class Node:
  def __init__(self, _data = None):
    self.updated = False
    self.data = _data
  def __repr__(self):
    return str(self.data)
#}}}

#Entry point to adding and removing entities to the structure{{{
class Engine:
  # Needs to have a list of systems that are used to process the data
  def __init__(self, _systems):
    self.systems = _systems

    # List of all entities that exist in the Engine
    self.all_entities = []

    # Tracks entities by entity type
    # {entity.__class__ : [entity, entity, ...]
    self.entities = {}

  def add(self, _entity):
    # Mark the Entity as added
    _entity.added = True
    self.all_entities.append(_entity)

    # Adds entities and creates the entity entries if they don't
    # already exist.
    for _ in _entity.components:
      _.parent = _entity # Assigned parent.

      # If component type is not already tracked, add it to self.entities
      if _.__class__ not in self.entities:
        self.entities[_.__class__] = []
      self.entities[_.__class__].append(_entity)

    # If entity type is not not being tracked, add it.
    if _entity.__class__ not in self.entities:
      self.entities[_entity.__class__] = []
    self.entities[_entity.__class__].append(_entity)

    # Add components to systems
    for s in self.systems:
      for c in _entity.components:
        if c.__class__ in s.component_filter:
          s.add(c)
          
  def remove(self, _entity):
    _entity.added = False
    self.all_entities.remove(_entity)
    for _ in _entity.components:
      self.entities[_.__class__].remove(_entity)
      if len(self.entities[_.__class__]) == 0:
        del self.entities[_.__class__]
    self.entities[_entity.__class__].remove(_entity)
    if len(self.entities[_entity.__class__]) == 0:
      del self.entities[_entity.__class__]
    for s in self.systems:
      for c in _entity.components:
        if c.__class__ in s.component_filter:
          s.remove(c)
  
  # Tick all systems
  def tick(self, _delta = 0):
    # Pop all function calls that were synced during the last cycle.
    while len(entity_callback_queue):
      entity_callback_queue.pop(0)(_delta)
    for i in self.systems:
      i.tick(_delta)
    
  # Short hand to getting lists of entities.
  # You can supply either entity or component class to get a list of associated lists.
  def __getitem__(self, _index):
    return self.entities[_index]
#}}}

# Common entity tools{{{
class nUpdate(Node):
  def __init__(self, _on_update, _when, _repeat):
    super().__init__(_on_update)
    self.when = _when
    self.repeat = _repeat
    self.done = False # Set true to stop repeat
    self.last = 0 # Last time that the timer had ticked
    self.cur = 0 # Current time on the timer.

class nKeys(Node):
  # _keys ('a','b','c')
  # _action function
  def __init__(self, _keys, _action):
    super().__init__(_keys)
    self._action = _action
  @property
  def keys(self): return self.data
  @property
  def action(self): return self._action

# Common pieces to use.
# 2d point of reference
class nPoint(Node):
  @property
  def x(self): return self.data[0]
  @x.setter
  def x(self, value):
    self.updated = True
    self.data[0] = value
  
  @property
  def y(self): return self.data[1]
  @y.setter
  def y(self, value):
    self.updated = True
    self.data[1] = value
  
  def __init__(self, x, y):
    super().__init__([x, y])
    
# Rectangle node
class nRect(Node):
  @property
  def x(self): return self.data[0]
  @x.setter
  def x(self, value):
    self.updated = True
    self.data[0] = value
  
  @property
  def y(self): return self.data[1]
  @y.setter
  def y(self, value):
    self.updated = True
    self.data[1] = value
    
  @property
  def w(self): return self.data[2]
  @w.setter
  def w(self, value):
    self.updated = True
    self.data[2] = value
  
  @property
  def h(self): return self.data[3]
  @h.setter
  def h(self, value):
    self.updated = True
    self.data[3] = value
    
  def __init__(self, x, y, w, h):
    super().__init__([x, y, w, h])



# Timer component to delay or have repeatable function calls
class cUpdate(Component):
  def __init__(self, _on_update, _when = 0, _repeat = False):
    super().__init__()
    self.update = nUpdate(_on_update, _when, _repeat)

class cKey(Component):
  def __init__(self, _keys, _action):
    super().__init__()
    self.keys = nKeys(_keys, _action)
   

# System to handle cUpdate component ticking.
class sUpdate(System):
  def __init__(self):
    super().__init__()
    self.component_filter = [cUpdate]
    
  def add(self, _comp):
    self.nodes.append(_comp.update)
  def remove(self, _comp):
    self.nodes.remove(_comp.update)
    
  def tick(self, _delta = 0):
    for _ in self.nodes:
      if not _.done:
        if _.when == 0:
          _.data(_delta)
          if not _.repeat:
              _.done = True
        else:
          _.cur += _delta
          if _.cur-_.last >= _.when:
            if _.repeat:
              #account for missed frames
              loops = int(((_.cur-_.last)/_.when))
              for __ in range(loops):
                _.data(_delta)
                _.last += _.when
            else:
              _.data(_delta)
              _.last += _.when
              _.done = True



class sKey(System):
  def __init__(self, _window, _keyboard):
    super().__init__()
    self.keyboard = _keyboard
    self.component_filter = [cKey]
    _window.bind(on_key_down=self.key_action_down)
    _window.bind(on_key_up=self.key_action_up)
    self.levels    = set() # Keys held down since last cycle
    self.edges     = set() # Keys just changed, either pressed or unpressed
    self.keys      = set() # Keys currently pressed.
    self.last_keys = set() # Keys tracked between cycles
    '''
    edges - keys & set(key) = on release
    edges & keys & set(key) = on press
    levels & set(key)       = held
    '''

  def add(self, _comp):
    self.nodes.append(_comp.keys)
  def remove(self, _comp):
    self.nodes.remove(_comp.keys)
    
  def tick(self, _delta = 0):
    # xor   abc ^ cde = abde
    self.edges = self.keys ^ self.last_keys | self.edges

    # and   abc & cde = c
    self.levels = self.keys & self.last_keys

    self.last_keys = self.keys.copy()

    # list of all involved keys within the event
    compare_keys = self.edges | self.levels

    for i in reversed(self.nodes):
      if compare_keys & i.keys:
        _ret = i.action(compare_keys & i.keys & self.keys, self.levels & compare_keys, self.edges & compare_keys)
        if _ret:
          compare_keys = compare_keys - _ret

    self.edges.clear()

  def key_action_down(self, *args):
    _event = self.keyboard.keycode_to_string(None, args[1])
    if _event:
      _event = set(_event)
      self.keys |= _event

  def key_action_up(self, *args):
    _event = self.keyboard.keycode_to_string(None, args[1])
    if _event:
      _event = set(_event)
      self.keys -= _event
      self.edges |= _event

  def fake_down(self, _keys):
    self.keys |= _keys

  def fake_up(self, _keys):
    self.keys -= _keys
    self.edges |= _keys

#}}}
