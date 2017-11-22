from jnius import autoclass, PythonJavaClass, java_method, cast
#from android import activity

from android.runnable import run_on_ui_thread
Toast = autoclass('android.widget.Toast')
context = autoclass('org.kivy.android.PythonActivity').mActivity
NotificationBuilder = autoclass('android.app.Notification$Builder')
#service = autoclass('org.kivy.android.PythonActivity').mService
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Notification = autoclass('android.app.Notification')

@run_on_ui_thread
def notify(title,text='', _index=0):
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
  
  notification_service.notify(_index, notification_builder.build())
  

@run_on_ui_thread
def toast(text, length_long=False):
  duration = Toast.LENGTH_LONG if length_long else Toast.LENGTH_SHORT
  String = autoclass('java.lang.String')
  c = cast('java.lang.CharSequence', String(text))
  t = Toast.makeText(context, c, duration)
  t.show()
