from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout

from kivymd.button import MDRaisedButton
from kivymd.card import MDCard
from kivymd.textfields import MDTextField

from kivymd.theming import ThemeManager

from jnius import autoclass, PythonJavaClass, java_method, cast
from android import activity
from android.runnable import run_on_ui_thread
Toast = autoclass('android.widget.Toast')
context = autoclass('org.renpy.android.PythonActivity').mActivity
NotificationBuilder = autoclass('android.app.Notification$Builder')
service = autoclass('org.renpy.android.PythonService').mService
PythonActivity = autoclass('org.renpy.android.PythonActivity')
Notification = autoclass('android.app.Notification')

@run_on_ui_thread
def notif(title,text):
  Drawable = autoclass("{}.R$drawable".format(context.getPackageName()))
  icon = getattr(Drawable, 'icon')
  
  String = autoclass('java.lang.String')
  t = cast('java.lang.CharSequence', String(title))
  c = cast('java.lang.CharSequence', String(text))
  
  notification_service = context.getSystemService(PythonActivity.NOTIFICATION_SERVICE)
  notification_builder = NotificationBuilder(context)
  
  notification_builder.setContentTitle(t)
  notification_builder.setContentText(c)
  notification_builder.setSmallIcon(icon)
  
  notification_service.notify(1, notification_builder.build())
  

@run_on_ui_thread
def toast(text, length_long=False):
  duration = Toast.LENGTH_LONG if length_long else Toast.LENGTH_SHORT
  String = autoclass('java.lang.String')
  c = cast('java.lang.CharSequence', String(text))
  t = Toast.makeText(context, c, duration)
  t.show()

class MyFirstWidget(StackLayout):
  pass

class DndApp(App):
  theme_cls = ThemeManager()
  
  def build(self):
    self.toast=toast
    self.notif=notif
    return MyFirstWidget()

DndApp().run()

