'''
Parses pipe delimited tables for either easy human readable lists or dictionary type data.

Syntax examples:

| item   |
| item 2 |
| item 3 |

|--------|
| item   |
| item 2 |
| item 3 |
|--------|

|--------|
| header |
|--------|
| item   |
| item 2 |
| item 3 |
|--------|

|--------|
| header |
|--------|
| item   |
| item 2 |
| item 3 |
|--------|
| totals |
|--------|

Data can be formatted as 2 dimensional arrays as well, but can be interoperated as either a list or dictionary for whichever use you need. 

|--------|--------|--------|
| key1   | key2   | key3   |
|--------|--------|--------|
| value1 | value2 | value3 |
|--------|--------|--------|

If it is interpreted as a dictionary, there will be 2 sets of data to choose from. 
One will be a list of dictionary with key value pairs for each row.
The second will be a list of dictionaries with the key matching to a list of items found in the column.
A list with the order of the original headers will be provided.


The system should be able to handle unlabeled headers and inconsistent row lengths as well as unlabeled headers in any order

| test  |
| test2 | test 3 |
| test4 |
| test5 | test6  |

|-----------|
| header    |
|-----------|-----------------------------|
| data      | data under unlabeled header |
| more data |
| moar data | something else              |
|-----------|-----------------------------|

|--|------------------|
|  | test             |
|--|------------------|
|  | like a checklist |
|--|------------------|


Everything is handled as a string. Casting shall be up to the developer.

'''

class Table:
  def __init__(self, _str, _as_list = True):
    self.data    = None
    self.as_list = _as_list
    self.headers = []

    self.cols = 0
    _in = _str.split('\n')
    # Trim the tail off if it is blank like in a direct file read
    if _in[-1] == '':
      _in = _in[:-1]

    # Loop over the lines
    for i in _in:
      if i.startswith('|'):
        # Length - 2 to account for leading | symbol's
        _cols = len(i.split('|'))-2

        # Only increase self.cols if the current column count is larger than previous
        if _cols > self.cols:
          self.cols = _cols

    # As list {{{
    if self.as_list:

      # If table is a single column, treat as a single dimensional list
      if self.cols == 1:
        self.data = []
        for i in _in:
          if len(i) and i[:2] not in ['|-','|:']:
            self.data.append(i.split('|')[1].strip())
          elif len(i) and i[:2] in ['|-','|:']:
            self.data.append('__pad__') # __pad__ is a placeholder for separator lines
      
      # If table has multiple columns, treat as a multiple dimension list
      elif self.cols > 1:
        self.data = []
        for i in _in:
          if len(i) and i[:2] not in ['|-','|:']:
            self.data.append([j.strip() for j in i.split('|')[1:-1]])
          elif len(i) and i[:2] in ['|-','|:']:
            self.data.append(['__pad__'])
        
        # Fill the tail end to make the rows even
        for i in self.data:
          while len(i) < self.cols:
            i.append('')
    # }}}

    # As dictionary {{{
    else:
      # Short references to use for searches
      self._cols = {}
      self._rows = []
      self._top_pad = False
      self.data = [self._rows, self._cols]

      # Loop over the lines
      for i in _in:
        # Ignore blank and visual lines
        if len(i) and i[:2] not in ['|-','|:']:

          # If no headers are defined yet, take the first non blank, non visual separation and define your headers
          if not self.headers:
            self.headers = [j.strip() for j in i.split('|')[1:-1]] 

            # Plug in the blanks at the tail end.
            while len(self.headers) < self.cols:
              self.headers.append('')

            # Give the empty headers a name
            empty_count = 0
            while '' in self.headers:
              self.headers[self.headers.index('')] = '_unamed_'+str(empty_count)
              empty_count += 1

            # Make blank lists for each column to use
            for j in self.headers:
              self._cols[j] = []
          else:
            # For non header lines, do this 
            _line = [j.strip() for j in i.split('|')[1: -1]]
            while len(_line) < self.cols:
              _line.append('')

            # Zip up the headers and lines 
            _merged = dict(zip(self.headers, _line))

            # Add each row item to the respective column.
            for j in self.headers:
              self._cols[j].append(_merged[j])

            # Finally add the row to the data.
            self.data[0].append(_merged)
        elif len(i) and i[:2] in ['|-','|:']:
          if not self.headers:
            self._top_pad = True
          else:
            self._rows.append({'pad':'__pad__'})
    # }}}

  # Returns neat tables with padding {{{
  def to_formatted_string(self, _alignments=[]):
    _out = ''
    if not self.as_list:
      _widths = {}
      _paddings = []
      for k,v in self._cols.items():
        _widths[k] = len(k)
        for i in v:
          if len(i) > _widths[k]:
            _widths[k] = len(i)
        _paddings.append('{:-<'+str(_widths[k]+2)+'}')
        _widths[k] = '{:'+str(_widths[k])+'}'

      # Space out headers.
      _headers = [v.format(k) for k,v in _widths.items()]

      _padding = '|'+'|'.join([i.format('') for i in _paddings])+'|\n'

      if self._top_pad:
        _out += _padding
      _out += '| '+' | '.join(_headers)+' |\n'
      for i in self._rows:
        if 'pad' in i and i['pad'] == '__pad__':
          _out += _padding
        else:
          _values = [v.format(i[k]) for k,v in _widths.items()]
          _out += '| '+' | '.join(_values)+' |\n'

    else:
      if self.cols == 1:
        _width = 0
        for i in self.data:
          if len(i)>_width:
            _width = len(i)
        _pads = '{:-<'+str(_width+2)+'}'
        _width = '{:'+str(_width)+'}'
        _padding = '|'+_pads.format('')+'|\n'

        for i in self.data:
          if i == '__pad__':
            _out += _padding
          else:
            _out += '| '+_width.format(i)+' |\n'
      else:
        _widths = []
        _paddings = []
        while len(_widths) < self.cols:
          _widths.append(0)
        for i in self.data:
          _index = 0 
          for j in range(len(i)):
            if len(i[j]) > _widths[j]:
              _widths[j] = len(i[j])

        for i in range(len(_widths)):
          _paddings.append('{:-<'+str(_widths[i]+2)+'}')
          _widths[i] = '{:'+str(_widths[i])+'}'

        _padding = '|'+'|'.join([i.format('') for i in _paddings])+'|\n'


        _values = []
        for i in self.data:
          _values.append([ _widths[j].format(i[j]) for j in range(len(_widths))])
          #_values = [v.format(i[k]) for k,v in _widths.items()]
        for i in _values:
          if i[0] == '__pad__':
            _out += _padding
          else:
            _out += '| '+' | '.join(i)+' |\n'

    return _out
  # }}}

  # Returns minimal spaced table return {{{
  def to_string(self):
    _out = ''
    if not self.as_list:
      _out = '| '+' | '.join(self.headers)+' |\n'
      _out += '|-|\n'
      for i in self._rows:
        _out += '| '+' | '.join(i.values())+' |\n'
    else:
      if self.cols == 1:
        for i in self.data:
          _out += '| %s |\n'%i
      else:
        for i in self.data:
          _out += '| '+' | '.join(i)+' |\n'
    return _out
  # }}}



'''
f = open('contacts.txt')
table_in = f.read()
f.close()

table = Table(table_in, False)

print(table.to_formatted_string())
'''
