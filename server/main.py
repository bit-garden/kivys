from kivy.clock import mainthread as ui

import os

def thread(func):
  from threading import Thread
  from functools import wraps
  
  @wraps(func)
  def async_func(*args, **kwargs):
    func_hl = Thread(target = func, args = args, kwargs = kwargs)
    func_hl.start()
    return func_hl
  return async_func

from kivy.app import App
from kivy.uix.button import Button

@thread
def start_serv():
  import server

class TestApp(App):
  def build(self):
    os.chdir('/sdcard/_stuff/code/server')
    start_serv()
    
    return Button(text='just a test')

TestApp().run()