import Entity
from Entity import async,sync

import websocket

from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout

from kivymd.navigationdrawer import NavigationLayout
from kivymd.navigationdrawer import MDNavigationDrawer
from kivymd.card import MDCard
from kivymd.button import MDRaisedButton
from kivymd.textfields import MDTextField


game=None
sws=None

def start():
  global game,sws
  
  uname = MDTextField(text='Kivy')
  uname._hint_lbl.text='Username'

  sname = MDTextField(text='ws://localhost:8000/chat')
  sname._hint_lbl.text='Server'
  
  root.ids.drawer.add_widget(
    uname
  )
  root.ids.drawer.add_widget(
    sname
  )

  root.ids.drawer.add_widget(
    MDRaisedButton(
      text='Connect',
      on_press=lambda _ev: sws.start(sname.text, uname.text)
    )
  )
  
  root.ids.drawer.add_widget(BoxLayout())
  
  sws = sWs()
  
  game = game = Entity.Engine([
    sws
  ])
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.1)
  
  #sws.start()

  


class sWs(Entity.System):
  def __init__(self):
    super().__init__()
    
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

  def on_error(self,_ws, error):
    snack(error)
  
  def on_close(self,_ws):
    snack("### closed ###")
  
  def on_open(self,_ws):
    self.ws.send(str({'login':True,'user':self.user}))

  @async
  def start(self, _addr='ws://localhost:8000/chat', _username='kivy', _pass=''):
    
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
  
  @async
  def stop(self):
    self.ws.close()
    
  def send(self,_data):
    self.ws.send(str(_data))






kv='''
NavigationLayout:
  MDNavigationDrawer:
    BoxLayout:
      orientation: 'vertical'
      padding:dp(8),dp(8),dp(8),dp(8)
      id:drawer
  ScatterLayout:
    MDCard:
      id:frame
'''

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
    
    root = Builder.load_string(kv)
    
    start()
    
    return root
    
  def on_stop(self):
    sws.stop()

app = SomeApp()

app.run()
