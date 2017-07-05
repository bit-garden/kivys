import Entity

class cMap(Entity.Component):
  def __init__(self, _textures=None,
                    x=0,y=0,
                    scale=128):
    super(cMap, self).__init__()
    self.pos = Entity.nPoint(x,y)
    self.textures=[]
    self.texture=None
    
    self.widget=Entity.Node(IconButton(pos=(x*scale,y*scale)))
    
    

class sMap(Entity.System):
  def __init__(self, _stage,
                    scale=128):
    super(sMap, self).__init__()
    
    self.component_filter = [cMap]
    self.stage=_stage
    self.scale=Entity.Node(scale)
    
  def add(self, _comp):
    self.nodes.append([_comp.pos,
                       _comp.texture,
                       _comp.widget
                      ])
    
    self.stage.add_widget(_comp.widget.data)
    
  def remove(self, _comp):
    self.nodes.remove([_comp.pos,
                       _comp.texture,
                       _comp.widget
                      ])
    
    self.stage.remove_widget(_comp.widget.data)

class test(Entity.Entity):
  def __init__(self,x,y):
    super(test,self).__init__()
    self.components=[
      Entity.cUpdate(self.tick,5000,True),
      cMap([],x,y)
    ]
    #root.ids.frame.add_widget(IconButton())

    
  def tick(self,_delta):
    #snack('hi')
    #snack(str(root.width))
    pass
  


timer,mapper,game=None,None,None


#start timer loop
def start():
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.5)
  
  global timer,mapper,game
  timer = Entity.sUpdate()
  mapper = sMap(root.ids.frame)
  
  game = Entity.Engine([
    timer,
    mapper
  ])
  
  game.add(test(0,0))
  game.add(test(3,3))
  
  

##################
#Kivy stuff
##################
from kivy.lang import Builder

from kivy.app import App
from kivy.clock import Clock

from kivy.uix.stacklayout import StackLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar
from kivymd.card import MDCard
from kivymd.selectioncontrols import MDSwitch
from kivymd.ripplebehavior import CircularRippleBehavior

from feedbacks import toast, notify

kv = '''
RelativeLayout:
  spacing: 50
  padding:[50,50,50,50]
  ScatterLayout:
    #size_hint:None,None
    #size: root.width,root.width*2
    #pos:(0,-self.height+root.height)
    MDCard:
      id:frame
    StackLayout:
      pos:50,-50
      MDSwitch:
        size_hint:None,None
        
<IconButton>:
  source: 'icon.png'
  size_hint:None,None
  size:200,200
  #pos: root.width/2-self.width/2,root.height/2-self.height/2
  ripple_scale:1.2
  #on_release: app.snack('squeek squeek squeek squeek')
'''

class IconButton(ButtonBehavior, CircularRippleBehavior, Image):
    pass


def snack(text):
  Snackbar(text=str(text)).show()

root = None

class DndApp(App):
  theme_cls = ThemeManager()
  def build(self):
    global root
    self.toast=toast
    self.notify=notify
    self.snack=snack
    self.theme_cls.theme_style = 'Dark'
    
    root = Builder.load_string(kv)
    
    start()
    
    return root

app = DndApp()

app.run()
