import Entity
from Entity import async,sync

import websocket

ws=None

@async
def connect():
  try:
    global ws
    
    def on_message(_ws, message):
      snack(message)
  
    def on_error(_ws, error):
      snack(error)
    
    def on_close(_ws):
      snack("### closed ###")
    
    def on_open(_ws):
      _ws.send(str({'login':True,'user':'kivy'}))
      
    host='ws://localhost:8000/chat'
    
    ws = websocket.WebSocketApp(host,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close,
                            on_open=on_open)
                            
    ws.run_forever()
  except Exeption as e:
    snack(e)

def send_mess(_text):
  ws.send(str({'message':_text}))

engine,timer=None,None

#start timer loop
#@mainthread
def start():
  Clock.schedule_interval(lambda _dt:engine.tick(_dt*1000), 0.1)
  global engine,timer
  
  timer = Entity.sUpdate()
  
  engine = Entity.Engine([
    timer
  ])
  
  connect()

##################
#Kivy stuff
##################
from kivy.lang import Builder

from kivy.app import App
from kivy.clock import Clock
from kivy.atlas import Atlas

from kivy.metrics import dp

from kivy.uix.widget import Widget
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar
from kivymd.card import MDCard
from kivymd.selectioncontrols import MDSwitch
from kivymd.ripplebehavior import CircularRippleBehavior
from kivymd.ripplebehavior import RectangularRippleBehavior
from kivymd.navigationdrawer import NavigationLayout
from kivymd.navigationdrawer import MDNavigationDrawer
from kivymd.navigationdrawer import NavigationDrawerToolbar
from kivymd.textfields import MDTextField
from kivymd.label import MDLabel

kv = '''
NavigationLayout:
  MDNavigationDrawer:
    id:drawer
    #NavigationDrawerToolbar:
    #  title: "Navigation Drawer"
    BoxLayout:
      orientation: 'vertical'
      padding:dp(8),dp(8),dp(8),dp(8)
      MDTextField:
        multiline: True
        hint_text: 'Name'
        text:'Dakun Skye'
      BoxLayout:
        orientation: 'horizontal'
        size_hint:1,None
        MDLabel:
          font_style: 'Subhead'
          theme_text_color: 'Primary'
          text: "Some Option"
          size_hint:None,None
          width:self.parent.width-dp(48)
        
        MDSwitch:
          size_hint:None,None
          width:dp(32)
          on_active:app.snack(self.active)
      Widget:
  RelativeLayout:
    orientation: 'vertical'
    RelativeLayout:
      MDTextField:
        text:'test'
        on_text_validate:app.send_mess(self.text)
    Toolbar:
      title: 'Chat'
      md_bg_color: app.theme_cls.primary_color
      background_palette: 'Primary'
      background_hue: '500'
      pos_hint:{'top':1}
      left_action_items: [['menu', lambda x: app.root.toggle_nav_drawer()]]
  
  
'''

@sync
def snack(text):
  Snackbar(text=str(text)).show()

root = None

class ChatApp(App):
  theme_cls = ThemeManager()
  def build(self):
    global root
    self.snack=snack
    self.send_mess=send_mess
    self.theme_cls.theme_style = 'Dark'
    
    root = Builder.load_string(kv)
    
    start()
        
    return root

app = ChatApp()

app.run()
