import Entity
from Entity import async,sync


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

import subprocess
import feedbacks

#asyncronous command caller
#this can return results of a call on the next sync
@async
def call(_command, _cb = None):
  @sync
  def _call(_str):
    _cb(_str)
  try:
    if _cb is None:
      subprocess.run(_command.split(' '))
    else:
      _val = subprocess.run(_command.split(' '), stdout=subprocess.PIPE).stdout
      _call(_val)
  except Exception as e:
    snack(e)


game=None

def start():
  global game
  
  def do_something(_ev):
    call("am start -f 0x00001000 --user 0 -n com.android.mms/.ui.ConversationList",
         feedbacks.toast)
     
  root.ids.drawer.add_widget(
    MDRaisedButton(
      text='command',
      on_press=do_something
    )
  )
  
  
  root.ids.drawer.add_widget(BoxLayout())
  
  '''  
  root.ids.frame.add_widget(
    MDRaisedButton(
      text='Send',
      on_press=lambda _ev: sws.send({'message':messagebox.text})
    )
  )'''
  
  game = Entity.Engine([
  ])
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.1)
  



kv='''
NavigationLayout:
  MDNavigationDrawer:
    BoxLayout:
      orientation: 'vertical'
      padding:dp(8),dp(8),dp(8),dp(8)
      id:drawer
  ScatterLayout:
    MDCard:
      #r:0
      #b:0
      #g:0
      BoxLayout:
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
