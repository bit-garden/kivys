from kivy.atlas import Atlas
import os

path='assets/images/test/'

os.chdir(path)

Atlas.create('test',os.listdir('.'),1024)