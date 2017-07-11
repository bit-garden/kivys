from kivy.clock import mainthread as ui

from kivy.lang import Builder
from kivy.app import App

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar


def thread(func):
  from threading import Thread
  from functools import wraps
  
  @wraps(func)
  def async_func(*args, **kwargs):
    func_hl = Thread(target = func, args = args, kwargs = kwargs)
    func_hl.start()
    return func_hl
  return async_func
  
def snack(text):
  Snackbar(text=str(text)).show()

kv='''
#:import Toolbar kivymd.toolbar.Toolbar
#:import BoxLayout kivy.uix.boxlayout
#:import NavigationLayout kivymd.navigationdrawer.NavigationLayout
#:import MDNavigationDrawer kivymd.navigationdrawer.MDNavigationDrawer
#:import MDCard kivymd.card.MDCard

NavigationLayout:
  MDNavigationDrawer:
    id:drawer
  BoxLayout:
    orientation: 'vertical'
    Toolbar:
      title: 'KivyMD Kitchen Sink'
      md_bg_color: app.theme_cls.primary_color
      background_palette: 'Primary'
      background_hue: '500'
      
    BoxLayout:
      

'''

root = None

class SomeApp(App):
  theme_cls = ThemeManager()
  def build(self):
    global root
    self.snack=snack
    self.theme_cls.theme_style = 'Dark'
    
    root = Builder.load_string(kv)
        
    return root

app = SomeApp()

app.run()
