# Misc {{{
# Entity system to manage the systems.
import Entity
# Needed to juggle background process with main thread easily
from Entity import _async,sync

from Tables import *

# Websocket client library
import websocket
# }}}

# Base imports for Kivy {{{
from kivy.lang        import Builder
from kivy.app         import App
from kivy.metrics     import dp
from kivy.clock       import Clock
from kivy.core.window import Window
from kivy.core.window import Keyboard
# }}}

# Needed imports for Kivymd {{{
from kivymd.theming  import ThemeManager
from kivymd.snackbar import Snackbar
# }}}

# Global reference to game engine and web socket connection
game = None
sws  = None
keys = None

class eButton(Entity.Entity):
  def onkey(self, _keys, _levels, _edges):
    # only on press
    if 'j' in _edges and 'j' in _keys:
      snack('down')
    elif 'j' in _edges:
      snack('release')
    elif 'j' in _levels:
      snack('held')
    if 'k' in _edges and 'k' in _keys:
      snack('k eat')
  def __init__(self):
    super().__init__()
    self.components = [Entity.cKey(
      set(['j', 'k']),
      self.onkey
    )]

    
# Entry point for main loop {{{
def start():
  global game, sws, keys

  # Make websocket system
  sws  = sWs()
  keys = Entity.sKey(Window, Keyboard)

  # Make Entity Engine with websocket system ready to go.
  game = Entity.Engine([
    sws,
    keys
  ])

  game.add(eButton())
  game.add(eButton())

  # Start the loop process for the game.
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.1)
  #open('assets/map.txt')

#}}}  

# system Websocket {{{
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
#}}}


# Display snacks {{{
@sync
def snack(text):
  Snackbar(text = str(text)).show()
#}}}


# Root view
root = None

# Kivy base class App {{{
class SomeApp(App):
  theme_cls = ThemeManager()
  def build(self):
    global root
    self.snack = snack
    self.theme_cls.theme_style = 'Dark'
    
    root = Builder.load_file('main.kv')
    
    start() 

    #Window.bind(on_key_down=self.key_action)
    
    return root

  # Final escape to close websocket thread when the ui is closed.
  def on_stop(self):
    sws.stop()

  def key_action(self, *args):
    snack(Keyboard.keycode_to_string(None, args[1]))

app = SomeApp()

app.run()
#}}}
