import Entity
from Entity import async,sync

import websocket

from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar


game=None
sws=None

def start():
  global game,sws

  #root.ids.drawer.add_widget(BoxLayout())
  
  '''root.ids.frame.add_widget(
    MDRaisedButton(
      text='pop',
      on_press=lambda _ev: 
    )
  )'''
  
  '''messagebox = MDTextField()
  messagebox._hint_lbl.text='Message'
  
  root.ids.frame.add_widget(
    messagebox
  )

  
  root.ids.frame.add_widget(
    MDRaisedButton(
      text='Send',
      on_press=lambda _ev: sws.send({'message':messagebox.text})
    )
  )'''
  
  sws = sWs()
  game = game = Entity.Engine([
    sws
  ])
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.1)
  


class sWs(Entity.System):
  def __init__(self):
    super().__init__()
    
    self.ws = None
    
    #expected components
    self.component_filter=[]
    self.nodes=[]
    
  def add(self,_component):
    pass # get the nodes to process
  
  def remove(self,_component):
    pass # cleanup
  
  def tick(self,_delta=0):
    pass # do update
    
  def on_message(self,_ws, message):
    snack(message)
    _data = eval(message)
    
  def on_error(self,_ws, error):
    snack(error)
    self.ws=None
  
  def on_close(self,_ws):
    snack("### closed ###")
    self.ws=None
  
  def on_open(self,_ws):
    self.ws.send(str({'login':True,'user':self.user, 'game':'Chat',
                        'action':'join','room':'chatroom'}))

  @async
  def start(self, _addr='ws://localhost:8080/chat', _username='kivy', _pass=''):
    if self.ws is None:
      try:
        self.ws = websocket.WebSocketApp(_addr,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close,
                                on_open=self.on_open)
                                
        self.user=_username
        
        self.ws.run_forever()
      except Exception as e:
        snack(e)
        self.ws=None
  
  @async
  def stop(self):
    if self.ws is not None:
      self.ws.close()
      self.ws=None
  
  @async
  def send(self,_data):
    if self.ws is not None:
      self.ws.send(str(_data))







@sync
def snack(text):
  Snackbar(text=str(text)).show()

root = None

class SomeApp(App):
  theme_cls = ThemeManager()
  def build(self):
    global root
    self.snack=snack
    self.theme_cls.theme_style = 'Dark'
    
    root = Builder.load_file('main.kv')
    
    start() 
    
    return root
    
  def on_stop(self):
    sws.stop()

app = SomeApp()

app.run()
