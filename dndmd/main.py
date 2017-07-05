import Entity

game = Entity.Engine([Entity.sUpdate()])

class test(Entity.Entity):
  def __init__(self):
    super(test,self).__init__()
    self.components=[Entity.cUpdate(self.tick,5000,True)]
    
  def tick(self,_delta):
    #snack('hi')
    snack(str(root.width))
  
  
#start timer loop
def start():
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.5)
  game.add(test())
  
  

##################
#Kivy stuff
##################
from kivy.lang import Builder

from kivy.app import App
from kivy.clock import Clock

from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar
from kivymd.selectioncontrols import MDSwitch
from kivymd.ripplebehavior import RectangularRippleBehavior

from feedbacks import toast, notify

kv = '''
RelativeLayout:
  spacing: 50
  padding:[50,50,50,50]
  IconButton:
    source: 'icon.png'
    size_hint:None,None
    size:500,500
    pos: root.width/2-self.width/2,root.height/2-self.height/2
    #on_release: app.snack('squeek squeek squeek squeek')
  StackLayout:
    pos:50,-50
    MDSwitch:
      size_hint:None,None
'''

class IconButton(ButtonBehavior, RectangularRippleBehavior, Image):
    pass


def snack(text):
  Snackbar(text=text).show()

root = None

class DndApp(App):
  theme_cls = ThemeManager()
  def build(self):
    global root
    self.toast=toast
    self.notify=notify
    self.snack=snack
    self.theme_cls.theme_style = 'Dark'
    
    start()
    
    root = Builder.load_string(kv)
    
    return root

app = DndApp()
app.run()
