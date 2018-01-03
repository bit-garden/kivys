'''from kivy.app import App
from kivy.uix.button import Button

class TestApp(App):
  def build(self):
    return Button(text='Hello World')

TestApp().run()'''

project='dndmd'

import os
os.chdir('/sdcard/kivy/'+project)

import sys
sys.path.append('/sdcard/kivy/'+project)

sys.path.append('/sdcard/kivy/lib')

import traceback

def run():
  try:
    import main
  except Exception as e:
    f=open('log.txt','w')
    f.write(str(e)+'\n')
    for frame in traceback.extract_tb(sys.exc_info()[2]):
      fname,lineno,fn,text = frame
    
    #f.write(str(type(e)))
    #f.write(str(e))
    #f.write(str(e.args))
      
      f.write("Error in %s on line %d\n" % (fname, lineno))
    f.close()
    
    
