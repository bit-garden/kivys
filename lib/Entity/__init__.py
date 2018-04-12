from threading import Thread
from functools import wraps

entity_callback_queue = []

def _async(func):
  @wraps(func)
  def async_func(*args, **kwargs):
    func_hl = Thread(target = func, args = args, kwargs = kwargs)
    func_hl.start()
    return func_hl
  return async_func
  

def sync(func):
  @wraps(func)
  def sync_func(*args, **kwargs):
    def sync_callback(_dt):
      func(*args, **kwargs)
    entity_callback_queue.append(sync_callback)
  return sync_func


#Processes that consistantly tick in the same manor
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

#Collections of components
class Entity:
  def __init__(self):
    #Is added to engine
    self.added=False
    self.components=[]

#Peices of an Entity that contiains nodes
class Component:
  pass

#Peices of data shared between components and systems
class Node:
  def __init__(self,_data=None):
    self.updated=False
    self.data=_data
  def __repr__(self):
    return str(self.data)

#Entry point to adding and removing entities to the structure
class Engine:
  def add(self,_entity):
    _entity.added=True
    self.all_entities.append(_entity)
    for _ in _entity.components:
      _.parent=_entity
      if _.__class__ not in self.entities:
        self.entities[_.__class__]=[]
      self.entities[_.__class__].append(_entity)
    if _entity.__class__ not in self.entities:
      self.entities[_entity.__class__]=[]
    self.entities[_entity.__class__].append(_entity)
    for s in self.systems:
      for c in _entity.components:
        if c.__class__ in s.component_filter:
          s.add(c)
          
  def remove(self,_entity):
    _entity.added=False
    self.all_entities.remove(_entity)
    for _ in _entity.components:
      self.entities[_.__class__].remove(_entity)
      if len(self.entities[_.__class__])==0:
        del self.entities[_.__class__]
    self.entities[_entity.__class__].remove(_entity)
    if len(self.entities[_entity.__class__])==0:
      del self.entities[_entity.__class__]
    for s in self.systems:
      for c in _entity.components:
        if c.__class__ in s.component_filter:
          s.remove(c)
  
  #Tick all systems
  def tick(self,_delta=0):
    while len(entity_callback_queue):
      entity_callback_queue.pop(0)(_delta)
    for i in self.systems:
      i.tick(_delta)
  
  def __init__(self, _systems):
    self.systems=_systems
    self.all_entities=[]
    self.entities={}
    
  def __getitem__(self,_index):
    return self.entities[_index]

#Common etity tools
class nUpdate(Node):
  def __init__(self, _on_update, _when, _repeat):
    super().__init__(_on_update)
    self.when = _when
    self.repeat=_repeat
    self.done=False#set true to stop repeat
    self.last=0
    self.cur=0


# 2d point of reference
class nPoint(Node):
  @property
  def x(self): return self.data[0]
  @x.setter
  def x(self, value): 
    self.updated=True
    self.data[0] = value
  
  @property
  def y(self): return self.data[1]
  @y.setter
  def y(self, value): 
    self.updated=True
    self.data[1] = value
  
  def __init__(self,x,y):
    super().__init__([x,y])
    
#Rectangle node
class nRect(Node):
  @property
  def x(self): return self.data[0]
  @x.setter
  def x(self, value): 
    self.updated=True
    self.data[0] = value
  
  @property
  def y(self): return self.data[1]
  @y.setter
  def y(self, value):  
    self.updated=True
    self.data[1] = value
    
  @property
  def w(self): return self.data[2]
  @w.setter
  def w(self, value):  
    self.updated=True
    self.data[2] = value
  
  @property
  def h(self): return self.data[3]
  @h.setter
  def h(self, value):  
    self.updated=True
    self.data[3] = value
    
  def __init__(self,x,y,w,h):
    super().__init__([x,y,w,h])



#updatable is an example of when an Entity should provide the functions
#instead of the system
class cUpdate(Component):
  def __init__(self, _on_update, _when=0, _repeat=False):
    super().__init__()
    self.update=nUpdate(_on_update, _when, _repeat)




class sUpdate(System):
  def __init__(self):
    super().__init__()
    self.component_filter=[cUpdate]
    
  def add(self,_comp):
    self.nodes.append(_comp.update)
  def remove(self,_comp):
    self.nodes.remove(_comp.update)
    
  def tick(self,_delta=0):
    for _ in self.nodes:
      if not _.done:
        if _.when==0:
          _.data(_delta)
          if not _.repeat:
              _.done=True
        else:
          _.cur+=_delta
          if _.cur-_.last>=_.when:
            if _.repeat:
              #account for missed frames
              loops=int(((_.cur-_.last)/_.when))
              for __ in range(loops):
                _.data(_delta)
                _.last+=_.when
            else:
              _.data(_delta)
              _.last+=_.when
              _.done=True
