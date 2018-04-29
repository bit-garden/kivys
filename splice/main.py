import copy

class Node:
  SIMPLE=0
  EXTEND=2
  DELETE=3
  SPLIT=4

  LEFT=0
  RIGHT=1

  def __init__(self, _kind = SIMPLE):
    self.kind = _kind
    self.children = []
    self.parent = None

  def has_slot(self):
    if len(self.children)==1 and self.children[0].kind==self.SPLIT:
      return False
    elif len(self.children)<2:
      return True
    else:
      return False


  def add_child(self, _child, _side=RIGHT):
    if _child.kind == self.SPLIT and len(self.children) == 0:
      self.children.append(_child)
      _child.parent=self
    elif len(self.children) < 2 \
        and not (len(self.children)==1 \
        and self.children[0].kind == self.SPLIT):
      if _side == self.RIGHT:
        self.children.append(_child)
      else:
        self.children.insert(0,_child)
      _child.parent=self
    else:
      return False
    return True

  def remove_child(self, _child):
    if _child in self.children:
      self.children.remove(_child)
      _child.parent=None
      return True
    return False

  def action(self):
    if self.kind == self.SPLIT:
      self.kind = self.SIMPLE
      self.parent.children.append(
          copy.deepcopy(self.parent.children[0])
      )
    elif self.kind == self.EXTEND:
      self.kind = self.SIMPLE
      self.parent.remove_child(self)
      _temp = Node()
      self.parent.add_child(_temp)
      _temp.add_child(self)

    elif self.kind == self.DELETE:
      self.parent.remove_child(self)

  def __repr__(self):
    return f'{self.kind}:{self.children}'

class Splice_game:
  def __init__(self):
    self.nodes = []
    self.root_node = Node()
    self.moves = 4
    self.history = []
    self.goal=''

  def add_node(self, _node, _where):
    if _where.add_child(_node):
      self.nodes.append(_node)
      print(self.root_node)
      return True

    print(f'Cannot add node({_node}) to ({_where})')
    return False

  def remove_node(self, _node):
    if _node.parent is not None:
      _node.parent.remove_child(_node)
      self.nodes.remove(_node)
      print(self.root_node)
      return True

    print(f'Cannot remove node({_node})')
    return False

  def get_moves(self):
    return [i for i in self.nodes if i.has_slot()]

  def get_actionable(self, _node, _results=[]):
    if len(_node.children)==0:
      return _results

    for i in _node.children:
      if i.kind != Node.SIMPLE:
        _results.append(i)

    if len(_results) != 0:
      return _results

    for n in _node.children:
      self.get_actionable(n)

    return _results
   

game = Splice_game()
game.add_node(Node(), game.root_node)
game.add_node(Node(Node.EXTEND), game.nodes[0])
game.add_node(Node(), game.nodes[0])

print(game.get_moves())

print(game.get_actionable(game.root_node))
