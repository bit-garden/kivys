import Entity
from Entity import async,sync

from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar




from kivymd.button import MDRaisedButton






game=None

def start():
  global game

  game = game = Entity.Engine([
  ])
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.1)
  
  from jnius import cast
  from jnius import autoclass
  import android
  import android.activity

  # test for an intent passed to us
  PythonActivity = autoclass('org.kivy.android.PythonActivity')
  activity = PythonActivity.mActivity
  intent = activity.getIntent()
  intent_data = intent.getData()

  
  
  try:
    file_uri= intent_data.toString()
  except AttributeError:
    file_uri = None
  
  #snack(file_uri)
  
  root.ids.data.text=str(file_uri)
  
  
  Intent = autoclass('android.content.Intent')
  
  pm = activity.getPackageManager()
  
  mainIntent = Intent(Intent.ACTION_MAIN, None)
  mainIntent.addCategory(Intent.CATEGORY_LAUNCHER)

  mApps = activity.getPackageManager().queryIntentActivities(mainIntent, 0);
  
  s = mApps.size()
  
  _out = ''
  
  for i in range(s):
    #mApps.get(i).activityInfo.packageName
    name = mApps.get(i).loadLabel(pm).lower().replace(" ","_")
    runnable = pm.getLaunchIntentForPackage(mApps.get(i).activityInfo.packageName).getComponent().flattenToShortString()

    _out+='alias %s="runapp %s"\n'%(name,runnable)

    root.ids.frame.add_widget(
      MDRaisedButton(text=mApps.get(i).loadLabel(pm),
                      on_press=lambda ev:snack(mApps.get(i).loadLabel(pm)))
    )
    
    if file_uri == None:
      root.ids.data.text = _out
    
    



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
    
  #def on_stop(self):
    #sws.stop()

app = SomeApp()

app.run()
