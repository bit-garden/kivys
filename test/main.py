from kivy.app import App
from kivy.clock import Clock

from kivy.uix.stacklayout import StackLayout

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar

from feedbacks import toast, notify

import Entity


game = Entity.Engine([Entity.sUpdate()])

class test(Entity.Entity):
  def __init__(self):
    super(test,self).__init__()
    self.components=[Entity.cUpdate(self.tick,5000,True)]
    
  def tick(self,_delta):
    toast('hi')
  
def start():
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.5)
  game.add(test())
  toast(str(game.entities))





def snack(text):
  Snackbar(text=text).show()

class MyFirstWidget(StackLayout):
  pass

class DndApp(App):
  theme_cls = ThemeManager()
  def build(self):
    self.toast=toast
    self.notify=notify
    self.snack=snack
    
    start()
    
    return MyFirstWidget()

DndApp().run()
















