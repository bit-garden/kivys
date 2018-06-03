# Entity system to manage the systems.
import Entity
# Needed to juggle background process with main thread easily
from Entity import _async,sync

from Tables import *

# Websocket client library
import websocket

from kivy.lang          import Builder
from kivy.app           import App
from kivy.metrics       import dp
from kivy.clock         import Clock
from kivy.core.window   import Window
from kivy.core.window   import Keyboard
from kivy.uix.image     import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.atlas         import Atlas
from kivy.uix.scatter   import Scatter

from kivymd.theming  import ThemeManager
from kivymd.snackbar import Snackbar

from kivy.uix.image import Image
from kivymd.ripplebehavior import CircularRippleBehavior

# Global reference to game engine and web socket connection
game   = None
sws    = None
keys   = None
mapper = None

# Touchable components
class cMap_interactive(Entity.Component):
  def __init__(self, _textures,
                    x=0,y=0, **kwargs):
    super(cMap_interactive, self).__init__()
    self.pos = Entity.nPoint(x,y)
    self.textures=Entity.Node(_textures)
    
    self.widget=Entity.Node(mappable_interactive(
                            pos=(x,y), **kwargs
                           ))

# Non touchable elements.
class cMap(Entity.Component):
  def __init__(self, _textures,
                    x=0,y=0, **kwargs):
    super(cMap, self).__init__()
    self.pos = Entity.nPoint(x,y)
    self.textures=Entity.Node(_textures)
    
    self.widget=Entity.Node(mappable(
                            pos=(x,y), **kwargs
                           ))

class sMap(Entity.System):
  def __init__(self, _stage):
    super(sMap, self).__init__()
    
    self.component_filter = [cMap_interactive, cMap]
    self.stage=_stage
    
  def add(self, _comp):
    self.nodes.append([_comp.pos,
                       _comp.textures,
                       _comp.widget
                      ])
    
    self.stage.add_widget(_comp.widget.data)
    
  def remove(self, _comp):
    self.nodes.remove([_comp.pos,
                       _comp.textures,
                       _comp.widget
                      ])
    
    self.stage.remove_widget(_comp.widget.data)
    
  def tick(self, _delta = 0):
    for _ in self.nodes:
      if _[0].updated:
        _[2].data.pos = (_[0].x,_[0].y)
      if _[1].updated:
        _[2].data.texture=_[1].data[0]


class sCleanup(Entity.System):
  def __init__(self):
    super(sCleanup,self).__init__()
    self.component_filter=[cMap_interactive, cMap]
    
  def add(self,_comp):
    self.nodes.append([_comp.pos,
                       _comp.textures,
                      ])
  def remove(self,_comp):
    self.nodes.remove([_comp.pos,
                       _comp.textures,
                      ])
    
  def tick(self,_delta=0):
    for _ in self.nodes:
      for __ in _:
        __.updated=False

# Ship
class eShip(Entity.Entity):
  def on_key(self, _keys, _levels, _edges, _dt):
    if _keys & {'w'}:
      self.cmappable.pos.y += dp(self.speed.data * _dt)
    if _keys & {'s'}:
      self.cmappable.pos.y -= dp(self.speed.data * _dt)


  def __init__(self, x, y):
    super().__init__()

    _textures = [ground_tex['grass1']]

    self.speed = Entity.Node(1)

    self.cmappable=cMap_interactive(_textures,x,y,
        texture=_textures[0], on_release=self.on_tap
      )

    self.components = [
      Entity.cKey(
        {'w', 'a', 's', 'd'},
        self.on_key
      ),
      self.cmappable
    ]

  def on_tap(self,_ev):
    #self.action(_ev,self.cmappable.pos.x,self.cmappable.pos.y)
    #snack('tapped')
    keys.fake_up(set('s'))
    
def start():
  global game, sws, keys, mapper

  # Make websocket system
  sws  = sWs()
  keys = Entity.sKey(Window, Keyboard)
  mapper = sMap(root.ids.frame)

  # Make Entity Engine with websocket system ready to go.
  game = Entity.Engine([
    sws,
    keys,
    mapper,
    sCleanup(),
  ])

  game.add(eShip(dp(200),dp(200)))

  # Start the loop process for the game.
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.01)
  #open('assets/map.txt')


class sWs(Entity.System):
  def __init__(self):
    super().__init__()
    
    self.ws = None
    
    #expected components
    self.component_filter = []
    self.nodes = []
    
  def add(self, _component):
    pass # get the nodes to process
  
  def remove(self, _component):
    pass # cleanup
  
  def tick(self, _delta = 0):
    pass # do update
    
  def on_message(self, _ws, message):
    snack(message)
    _data = eval(message)
    
  def on_error(self, _ws, error):
    snack(error)
    self.ws = None
  
  def on_close(self, _ws):
    snack("### closed ###")
    self.ws = None
  
  def on_open(self, _ws):
    self.ws.send(str({'login':True, 'user':self.user, 'game':'Chat',
                        'action':'join', 'room':'chatroom'}))

  @_async
  def start(self, _addr = 'ws://localhost:8080/chat', _username = 'kivy', _pass = ''):
    if self.ws is None:
      try:
        self.ws = websocket.WebSocketApp(_addr,
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close,
                                on_open = self.on_open)
                                
        self.user = _username
        
        self.ws.run_forever()
      except Exception as e:
        snack(e)
        self.ws = None
  
  @_async
  def stop(self):
    if self.ws is not None:
      self.ws.close()
      self.ws = None
  
  @_async
  def send(self, _data):
    if self.ws is not None:
      self.ws.send(str(_data))


@sync
def snack(text):
  Snackbar(text = str(text)).show()


# Root view
root = None

#fix for scaling textures up
def atlas_nearest(_atlas):
  for _ in _atlas.original_textures:
    _.mag_filter='nearest'
  return _atlas

ground_tex = atlas_nearest(Atlas('assets/images/ground/ground.atlas'))

# touchable elements of the screen, like buttons or in world objects.
class mappable_interactive(ButtonBehavior, CircularRippleBehavior, Image):
  #allow dragging off of a target to cancel the click
  def on_touch_up(self, touch):
    if self.collide_point(*touch.pos):
      return super(mappable_interactive, self).on_touch_up(touch)
    return False

# just a drawable element.
class mappable(Scatter, Image):
  pass

class SomeApp(App):
  theme_cls = ThemeManager()
  def build(self):
    global root
    self.snack = snack
    self.theme_cls.theme_style = 'Dark'
    
    root = Builder.load_file('main.kv')
    
    start() 

    return root

  # Final escape to close websocket thread when the ui is closed.
  def on_stop(self):
    sws.stop()

app = SomeApp()

app.run()
