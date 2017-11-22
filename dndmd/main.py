import feedbacks

import Entity
from Entity import async,sync

#data is not used here
#reprisents cells of the grid
class nGrid(Entity.Node):
  def _can_enter(self, _entity, _dir):
    if (_entity.__class__ == eCharacter and 
        len([_ for _ in self.contents if _.__class__ in [eCharacter]]) == 0):
      return True
    return False

  def _can_exit(self, _entity, _dir):
    return True

  def __init__(self, 
               can_enter = None, 
               on_enter = None, 
               can_exit = None, 
               on_exit = None,
               contents = None):
    
    #common cell behaviors
    if can_enter is None:
      #conditions to enter and leave
      #also events on enter and leave
      self.can_enter = self._can_enter
    else:
      self.can_enter=can_enter
    self.on_enter = on_enter
    
    if can_exit is None:
      self.can_exit = self._can_exit
    else:
      self.can_exit = can_exit
    self.on_exit = on_exit
    
    if not contents:
      contents = list()
    self.contents = contents


class cGrid(Entity.Component):
  def __init__(self, x, y, **kwargs):
    super(cGrid,self).__init__()
    self.x,self.y = x,y
    self.ngrid = nGrid(**kwargs)


class cMap_interactive(Entity.Component):
  def __init__(self, _textures,
                    x=0,y=0,
                    scale=Entity.Node(128), **kwargs):
    super(cMap_interactive, self).__init__()
    self.pos = Entity.nPoint(x,y)
    self.textures=Entity.Node(_textures)
    
    self.widget=Entity.Node(mappable_interactive(
                            pos=(x*scale.data,y*scale.data),
                            size=(scale.data,scale.data),
                            **kwargs
                           ))
                           
class cMap(Entity.Component):
  def __init__(self, _textures=None,
                    x=0,y=0,
                    scale=Entity.Node(128), **kwargs):
    super(cMap, self).__init__()
    self.pos = Entity.nPoint(x,y)
    self.textures=Entity.Node(_textures)
    
    self.widget=Entity.Node(mappable(
                            pos=(x*scale.data,y*scale.data),
                            size=(scale.data,scale.data),
                            **kwargs
                           ))
    
    

class sMap(Entity.System):
  def __init__(self, _stage,
                    scale=64):
    super(sMap, self).__init__()
    
    self.component_filter = [cMap,cMap_interactive]
    self.stage=_stage
    self.scale=Entity.Node(dp(scale))
    
  def add(self, _comp):
    self.nodes.append([_comp.pos,
                       _comp.textures,
                       _comp.widget
                      ])
    
    self.stage.add_widget(_comp.widget.data)
    
  def remove(self, _comp):
    self.nodes.remove([_comp.pos,
                       _comp.textures,
                       _comp.widget
                      ])
    
    self.stage.remove_widget(_comp.widget.data)
    
  def tick(self, _delta = 0):
    for _ in self.nodes:
      if _[0].updated:
        _[2].data.pos = (_[0].x*self.scale.data,_[0].y*self.scale.data)
      if _[1].updated:
        _[2].data.texture=_[1].data[0]

#placeholder
class cAnim(Entity.Component):pass
class sAnim(Entity.System):
  def __init__(self,_rate,_updater):
    super(sAnim,self).__init__()
    self.component_filter=[cAnim]
    self.rate=_rate
    self.updater=_updater
    self.objs={}
  
  def add(self,_comp):
    #self.nodes.append(_comp.parent.cmappable.textures)
    self.objs[_comp.parent]=Entity.cUpdate(lambda _:self.flip(_comp.parent),self.rate,True)
    self.updater.add(self.objs[_comp.parent])
    
  def remove(self,_comp):
    #self.nodes.remove(_comp.parent.cmappable.textures)
    self.updater.remove(self.objs[_comp.parent])
    del self.objs[_comp.parent]
    
  def flip(self,_data):
    if len(_data.cmappable.textures.data)>1:
      _temp = _data.cmappable.textures.data.pop(0)
      _data.cmappable.textures.data.append(_temp)
      _data.cmappable.textures.updated=True
      
class sGrid(Entity.System):
  #Static directions
  NORTH=0b1
  SOUTH=0b10
  EAST=0b100
  WEST=0b1000
  TELE=0b10000
  MOVE=0b100000
  ANY=0b1000000
  
  def __init__(self, w, h):
    super(sGrid,self).__init__()
    self.component_filter=[cMap,cMap_interactive,cGrid]
    self.grid=[]
    for _ in range(h):
      self.grid.append([])
    for _ in self.grid:
      for __ in range(w):
        _.append(nGrid())
    self.w=w
    self.h=h

  def add(self,_comp):
    if _comp.__class__==cGrid:
      self.grid[_comp.y][_comp.x]=_comp.ngrid
    elif _comp.__class__ in (cMap,cMap_interactive) and _comp.parent.__class__!=eGrid:
      self.grid[_comp.pos.y][_comp.pos.x].contents.append(_comp.parent)
  
  def remove(self,_comp):
    if _comp.__class__==cGrid:
      self.grid[_comp.y][_comp.x]=nGrid()
    elif _comp.__class__ in (cMap,cMap_interactive) and _comp.parent.__class__!=eGrid:
      self.grid[_comp.pos.y][_comp.pos.x].contents.remove(_comp.parent)
      
  def tele(self, _what, next_pos):
    _where=self.TELE
    cur_pos=self.grid[_what.cmappable.pos.y][_what.cmappable.pos.x]
    new_pos=self.grid[next_pos[1]][next_pos[0]]
    if cur_pos.can_exit(_what,_where) and new_pos.can_enter(_what,_where):
      if cur_pos.on_exit:cur_pos.on_exit(_what,_where)
      cur_pos.contents.remove(_what)
      new_pos.contents.append(_what)
      _what.cmappable.pos.x=next_pos[0]
      _what.cmappable.pos.y=next_pos[1]
      if new_pos.on_enter:new_pos.on_enter(_what,_where)
    
  
  #_what should be nPoint of location
  def move(self, _what, _where):
    cur_pos=self.grid[_what.cmappable.pos.y][_what.cmappable.pos.x]
    next_pos=Entity.nPoint(_what.cmappable.pos.x,_what.cmappable.pos.y)
    
    
    if _where & self.NORTH:
      next_pos.y+=1
    if _where & self.SOUTH:
      next_pos.y-=1
    if _where & self.EAST:
      next_pos.x+=1
    if _where & self.WEST:
      next_pos.x-=1
    
    if (next_pos.x<self.w and next_pos.x>=0 and
        next_pos.y<self.h and next_pos.y>=0):
      new_pos=self.grid[next_pos.y][next_pos.x]
      if cur_pos.can_exit(_what,_where) and new_pos.can_enter(_what,_where):
        if cur_pos.on_exit:cur_pos.on_exit(_what,_where)
        cur_pos.contents.remove(_what)
        new_pos.contents.append(_what)
        _what.cmappable.pos.x=next_pos.x
        _what.cmappable.pos.y=next_pos.y
        if new_pos.on_enter:new_pos.on_enter(_what,_where)
        return True
    return False


  #gets tiles that fir within a range and specific conditions
  def get_range(self,x,y,r,
                results,
                condition=None):
    r-=1
    if (x >= self.w or y >= self.h or
        x < 0 or y < 0 or r==0):
      return results

    if condition is not None:
      if not condition(x,y,self.grid[y][x]) and results!=[]:
        return results
    
    if (x,y) not in results:
      results.append((x,y))
      
    self.get_range(x-1,y,r,results,condition)
    self.get_range(x,y-1,r,results,condition)
    self.get_range(x+1,y,r,results,condition)
    self.get_range(x,y+1,r,results,condition)
    
    return results
    
  def get_paths(self,x,y,r,
                results,
                condition=None,
                _paths=None):
    r-=1
    if (x >= self.w or y >= self.h or
        x < 0 or y < 0 or r==0):
      return results

    if condition is not None:
      if not condition(x,y,self.grid[y][x]) and results!={}:
        return results
    
    if _paths is not None and (x,y) not in _paths:
      _paths.append((x,y))


    if (x,y) not in results:
      results[(x,y)]=_paths
    else:
      if len(_paths) < len(results[(x,y)]):
        results[(x,y)]=_paths
      else:
        return results
        
    
    if _paths is None:
      self.get_paths(x-1,y,r,results,condition,list())
      self.get_paths(x,y-1,r,results,condition,list())
      self.get_paths(x+1,y,r,results,condition,list())
      self.get_paths(x,y+1,r,results,condition,list())
    else:
      self.get_paths(x-1,y,r,results,condition,_paths[:])
      self.get_paths(x,y-1,r,results,condition,_paths[:])
      self.get_paths(x+1,y,r,results,condition,_paths[:])
      self.get_paths(x,y+1,r,results,condition,_paths[:])
      
    return results
  
  def to_dir(self,_start, _coords):
    _path=[(_start.x,_start.y)]+_coords
    _dirs = []
    for _ in range(len(_path)-1):
      if _path[_][0] > _path[_+1][0]:
        _dirs.append(self.WEST)
      if _path[_][0] < _path[_+1][0]:
        _dirs.append(self.EAST)
      if _path[_][1] > _path[_+1][1]:
        _dirs.append(self.SOUTH)
      if _path[_][1] < _path[_+1][1]:
        _dirs.append(self.NORTH)

    return _dirs
    
class eGrid(Entity.Entity):
  def __init__(self,x,y,_textures,**kwargs):
    super(eGrid,self).__init__()
    
    
    self.cmappable=cMap(_textures,x,y,mapper.scale,
        texture=_textures[0]
      )
      
    self.cgrid=cGrid(x,y,**kwargs)
    
    self.components=[
      self.cmappable,
      self.cgrid,
      cAnim()
    ]
    
class eMove_to(Entity.Entity):
  def __init__(self,x,y,scale,action):
    super(eMove_to,self).__init__()
    self.action=action

    self.cmappable=cMap_interactive([hl_tex],x,y,scale,on_release=self.tap,
                                  texture=hl_tex)
    self.cmappable.widget.data.opacity=0.75
    self.components=(
      self.cmappable,
      #cTouch(self.cmappable.pix, tap=self.tap),
      cAnim()
    )

  def tap(self,_ev):
    self.action(_ev,self.cmappable.pos.x,self.cmappable.pos.y)
    #game.remove(self)

class eCharacter(Entity.Entity):
  def __init__(self,x,y,_textures):
    super(eCharacter,self).__init__()
    
    self.moves=None
    
    self.cmappable = cMap_interactive(_textures,x,y,mapper.scale,
        on_release=self.tap,
        texture=_textures[0]
      )
    
    self.components=[
      Entity.cUpdate(self.tick,5000,True),
      self.cmappable,
      cAnim()
    ]

    
  def tick(self,_delta):
    #snack('hi')
    #snack(str(root.width))
    pass
  
  @async
  def tap(self, _ev):
    if not self.moves:
      self.moves=[]
      
      self.paths=grid.get_paths(self.cmappable.pos.x,self.cmappable.pos.y,8,{},self._filter)
    
      self._add_moves()
    
    else:
      for _ in self.moves:
        game.remove(_)
      self.moves=None

  @sync
  def _add_moves(self):
    for _ in self.paths:
      if _ !=(self.cmappable.pos.x,self.cmappable.pos.y):
        self.moves.append(eMove_to(_[0],_[1],mapper.scale,self.move_to))
    for _ in self.moves:
      game.add(_)

  def _filter(self,x,y,_nGrid):
    return _nGrid.can_enter(self,sGrid.MOVE)
    
  def move_to(self,ev,x,y):
    #grid.tele(self,(x,y))
    
    _dirs = grid.to_dir(self.cmappable.pos, self.paths[(x,y)])
    
    for _ in _dirs:
      if not grid.move(self,_):
        break
    for _ in self.moves:
      game.remove(_)
    self.moves=None
    
class sCleanup(Entity.System):
  def __init__(self):
    super(sCleanup,self).__init__()
    self.component_filter=[cMap,cMap_interactive]
    
  def add(self,_comp):
    self.nodes.append([_comp.pos,
                       _comp.textures,
                      ])
  def remove(self,_comp):
    self.nodes.remove([_comp.pos,
                       _comp.textures,
                      ])
    
  def tick(self,_delta=0):
    for _ in self.nodes:
      for __ in _:
        __.updated=False


timer,mapper,game=None,None,None
grid,sanim=None,None

#start timer loop
#@mainthread
def start():
  Clock.schedule_interval(lambda _dt:game.tick(_dt*1000), 0.1)
  
  global timer,mapper,game
  global grid,sanim
  
  timer = Entity.sUpdate()
  mapper = sMap(root.ids.frame)
  grid = sGrid(15,15)
  sanim=sAnim(500,timer)
  
  game = Entity.Engine([
    timer,
    grid,
    mapper,
    sCleanup(),
    sanim
  ])
  
  test_map = eval(open('assets/maps/test.txt').read())[::-1]
  
  water_textures=[ground_tex['water1']]
  ground_textures=[ground_tex['grass1']]
  
  
  for y in range(len(test_map)):
    for x in range(len(test_map[0])):
      if test_map[y][x]=='w':
        game.add(eGrid(x,y,water_textures,
                      can_enter=lambda _en,_dir:False))
      elif test_map[y][x]=='g':
        #pass
        game.add(eGrid(x,y,ground_textures))
        
  
  game.add(eGrid(2,3,[ground_tex['grass1'],ground_tex['water1']],
    can_exit=lambda _en,_dir:_dir==sGrid.SOUTH,
    on_enter=lambda _en,_dir:snack('traped. You can only escape south')
  ))
  game.add(eCharacter(1,1,[test_tex['nuRabbit']]))
  

##################
#Kivy stuff
##################
from kivy.lang import Builder

from kivy.app import App
from kivy.clock import Clock
from kivy.atlas import Atlas

from kivy.metrics import dp

from kivy.uix.widget import Widget
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

from kivymd.theming import ThemeManager
from kivymd.snackbar import Snackbar
from kivymd.card import MDCard
from kivymd.selectioncontrols import MDSwitch
from kivymd.ripplebehavior import CircularRippleBehavior
from kivymd.ripplebehavior import RectangularRippleBehavior
from kivymd.navigationdrawer import NavigationLayout
from kivymd.navigationdrawer import MDNavigationDrawer
from kivymd.navigationdrawer import NavigationDrawerToolbar
from kivymd.textfields import MDTextField
from kivymd.label import MDLabel

kv = '''
NavigationLayout:
  MDNavigationDrawer:
    id:drawer
    #NavigationDrawerToolbar:
    #  title: "Navigation Drawer"
    BoxLayout:
      orientation: 'vertical'
      padding:dp(8),dp(8),dp(8),dp(8)
      MDTextField:
        multiline: True
        hint_text: 'Name'
        text:'Dakun Skye'
      BoxLayout:
        orientation: 'horizontal'
        size_hint:1,None
        MDLabel:
          font_style: 'Subhead'
          theme_text_color: 'Primary'
          text: "Some Option"
          size_hint:None,None
          width:self.parent.width-dp(48)
        
        MDSwitch:
          size_hint:None,None
          width:dp(32)
          on_active:app.fb.toast(str(self.active))
      Widget:
  RelativeLayout:
    orientation: 'vertical'
    RelativeLayout:
      ScatterLayout:
        size_hint:None,None
        size: 15*dp(64),15*dp(64)
        #pos:(0,-self.height+root.height)
        MDCard:
          id:frame
    
    #Toolbar:
    #  title: 'DnD_MD'
    #  md_bg_color: app.theme_cls.primary_color
    #  background_palette: 'Primary'
    #  background_hue: '500'
    #  pos_hint:{'top':1}
    #  left_action_items: [['menu', lambda x: app.root.toggle_nav_drawer()]]
        
<mappable_interactive>:
  #source: 'icon.png'
  size_hint:None,None
  allow_stretch:True
  #pos: root.width/2-self.width/2,root.height/2-self.height/2
  ripple_scale:1.5
  #on_release: app.snack('squeek squeek squeek squeek')
  
<mappable>:
  size_hint:None,None
  allow_stretch:True
  
  
'''

class mappable_interactive(ButtonBehavior, CircularRippleBehavior, Image):
  #allow dragging off of a target to cancel the click
  def on_touch_up(self, touch):
    if self.collide_point(*touch.pos):
      return super(mappable_interactive, self).on_touch_up(touch)
    return False
    
class mappable(Image):
  pass

#fix for scaling textures up
def atlas_nearest(_atlas):
  for _ in _atlas.original_textures:
    _.mag_filter='nearest'
  return _atlas

ground_tex = atlas_nearest(Atlas('assets/images/ground/ground.atlas'))
test_tex = atlas_nearest(Atlas('assets/images/test/test.atlas'))
hl_tex = ground_tex['highlight']

def snack(text):
  Snackbar(text=str(text)).show()

root = None

class DndApp(App):
  theme_cls = ThemeManager()
  def build(self):
    global root
    self.snack=snack
    self.fb=feedbacks
    self.theme_cls.theme_style = 'Dark'
    
    root = Builder.load_string(kv)
    
    start()
        
    return root

app = DndApp()

app.run()
