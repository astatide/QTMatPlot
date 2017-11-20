#! /usr/bin/python3

# Stuff to get the window open.
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QTreeWidget, QTreeWidgetItem, QGraphicsAnchorLayout, QScrollArea, QLineEdit, QMenu, QAction
from PyQt5.QtGui import QIcon, QCursor
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.Qt import Qt

# Matplotlib stuff
import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure
import seaborn as sns
import h5py
import ast
import copy
sns.set_style('ticks')
sns.set_context('paper')
sns.axes_style({'font.family': ['monospace'],
                'font.sans-serif': ['monospace']
                })
sns.set(font='sans-serif', style='ticks')
#sns.set_palette('husl')
sns.set_palette('deep')

import yaml

# and here http://www.boxcontrol.net/embedding-matplotlib-plot-on-pyqt5-gui.html

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Button Functions
@pyqtSlot()
def button_test():
    print("We're clicking a button, wheee")

# Now, from that other site...
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=7, height=4, dpi=300, num=1, data=None, notify_func=None):
        self.data = data
        self.notify_func = notify_func
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # We want the axes cleared every time plot() is called


        #
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)'''

        #self.mpl_connect("scroll_event", self.scrolling)
        self.fig_dict = '''{
                            'type': 'plot', 
                            }'''
        self.dset_dict = '''{
                            'color': -1,
                            'alpha': 1, 
                            'loc': 'None',
                            'ylabel': '',
                            'xlabel': '',
                            'title': ''
                            }'''

        self.mpl_dict_lit = '''{
                                'FilesToLoad': 'IGNORE',
                                'Rows': 2, 
                                'Columns': 4,
                                'Datasets': 1,
                                'FigDefaults': {},
                                'DSetDefaults': {},
                                'dpi': 300,
                                'figsize': {
                                  'width': 7,
                                  'height': 4,
                                 },
                                'fontsize': {
                                  'fontsize': 6,
                                  'titlesize': 8,
                                  'ticksize': 3
                                 },
                                'Colors': {
                                  0: '#8dd3c7',
                                  1: '#ffffb3',
                                  2: '#bebada',
                                  3: '#fb8072',
                                  4: '#80b1d3',
                                  5: '#fdb462',
                                  6: '#a65628',
                                  7: '#f781bf'
                                 },
                                'Figures': {}
                               }'''
        self.mpl_dict = ast.literal_eval(self.mpl_dict_lit)
        self.mpl_dict['DSetDefaults'] = ast.literal_eval(self.dset_dict)
        self.mpl_dict['FigDefaults'] = ast.literal_eval(self.fig_dict)
        self.mpl_dict['FigDefaults']['data'] = {}
        self.compute_initial_figure()
        self.update_figure()
        ##timer = QtCore.QTimer(self)
        ##timer.timeout.connect(self.update_figure)
        ##timer.start(1000)

    def compute_initial_figure(self):
        self.updateFromDict(False)

    def plot(self, pd, index, ax):
        # pd is the plot dictionary
        print(pd)
        ax.tick_params(axis='both', labelsize=float(self.mpl_dict['fontsize']['fontsize']), length=self.mpl_dict['fontsize']['ticksize'])
        sk = dict(pd['data'][str(index)])
        if sk['ylabel'] is not None:
            ax.set_ylabel(sk['ylabel'], fontsize=float(self.mpl_dict['fontsize']['titlesize']), fontweight='bold')
        if sk['xlabel'] is not None:
            ax.set_xlabel(sk['xlabel'], fontsize=float(self.mpl_dict['fontsize']['titlesize']), fontweight='bold')
        if sk['title'] is not None:
            ax.set_title(sk['title'], fontsize=float(self.mpl_dict['fontsize']['titlesize']), fontweight='bold')
        if pd['data'][str(index)]['loc'] != 'None':
            if pd['type'] == 'plot':
                try:
                    subplot_kwargs = dict(pd['data'][str(index)])
                    del subplot_kwargs['loc']
                    del subplot_kwargs['xlabel']
                    del subplot_kwargs['title']
                    del subplot_kwargs['ylabel']
                    if subplot_kwargs['color'] == -1:
                        subplot_kwargs['color'] = self.mpl_dict['Colors'][str(index)]
                    handle = ax.plot(self.translate_location(pd['data'][str(index)]['loc']), **subplot_kwargs)
                    return handle
                except Exception as e:
                    if self.notify_func is not None:
                        self.notify_func(e)
                    else:
                        pass
            if pd['type'] == 'shade':
                try:
                    subplot_kwargs = dict(pd['data'][str(index)])
                    del subplot_kwargs['loc']
                    del subplot_kwargs['xlabel']
                    del subplot_kwargs['title']
                    del subplot_kwargs['ylabel']
                    if subplot_kwargs['color'] == -1:
                        subplot_kwargs['color'] = self.mpl_dict['Colors'][index]
                    elif str(subplot_kwargs['color'])[0] == "#":
                        pass
                    else:
                        subplot_kwargs['color'] = self.mpl_dict['Colors'][int(subplot_kwargs['color'])]
                    ax.plot(self.translate_location(pd['data'][str(index)]['loc'])['expected'][:], **subplot_kwargs)
                    subplot_kwargs['alpha'] = .3
                    handle = ax.fill_between(range(0, self.translate_location(pd['data'][str(index)]['loc'])['expected'].shape[0]), self.translate_location(pd['data'][str(index)]['loc'])['ci_ubound'][:], self.translate_location(pd['data'][str(index)]['loc'])['ci_lbound'][:], **subplot_kwargs)
                    return handle
                except Exception as e:
                    if self.notify_func is not None:
                        self.notify_func(e)
                    else:
                        pass
                #self.axes

    def updateFromDict(self, defaults):
        d = self.mpl_dict
        # Clears the figure before we plot more.
        self.fig.clear()
        self.axes = self.fig.subplots(nrows=int(d['Rows']), ncols=int(d['Columns']))
        self.fig.set_dpi(int(d['dpi']))
        self.fig.set_size_inches(float(d['figsize']['width']), float(d['figsize']['height']))
        # We check to see if we need to update the figures.
        # This should just occur on a rebuild, so if we haven't added anything, don't worry about it.
        for rows in range(0, int(self.mpl_dict['Rows'])):
            for cols in range(0, int(self.mpl_dict['Columns'])):
                if defaults:
                    # If we haven't changed the defaults, don't upstate the state.
                    if str((rows, cols)) not in self.mpl_dict['Figures']:
                        #self.mpl_dict['Figures'][str((rows,cols))] = ast.literal_eval(self.fig_dict)
                        self.mpl_dict['Figures'][str((rows,cols))] = copy.deepcopy(self.mpl_dict['FigDefaults'])
                else:
                    self.mpl_dict['Figures'][str((rows,cols))] = copy.deepcopy(self.mpl_dict['FigDefaults'])
                for dset in range(0, int(self.mpl_dict['Datasets'])):
                    if defaults:
                        if str(dset) not in self.mpl_dict['Figures'][str((rows,cols))]['data']:
                            #self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = ast.literal_eval(self.dset_dict)
                            self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = copy.deepcopy(self.mpl_dict['DSetDefaults'])
                    else:
                        self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = copy.deepcopy(self.mpl_dict['DSetDefaults'])

                # Throw in the axes object.
                #print(self.mpl_dict['Figures'][(rows,cols)])
                for dset in range(0, int(self.mpl_dict['Datasets'])):
                    self.plot(self.mpl_dict['Figures'][str((rows,cols))], dset, self.axes[rows,cols])

                



    def updateSize(self, height, width):
        pass

    def update_figure(self, defaults=True):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        # We call this whenever the dictionary is updated.
        self.updateFromDict(defaults)
        #l = [np.random.randint(0, 10) for i in range(4)]

        #self.axes.plot([0, 1, 2, 3], l, 'r')
        '''sns.set_style('ticks')
        sns.set_context('paper')
        sns.axes_style({'font.family': ['monospace'],
                        'font.sans-serif': ['monospace']
                        })
        sns.set(font='sans-serif', style='ticks')
        sns.set_palette('deep')
        sns.despine()'''
        #self.fig.tight_layout()
        self.draw()
        FigureCanvas.updateGeometry(self)

    def save_figure(self):
        self.fig.savefig("test.pdf")
        with open('test.yml', 'w') as outfile:
            yaml.dump(self.mpl_dict, outfile, default_flow_style=False)

    def load_yaml(self):
        test = yaml.load(open('test.yml', 'r'))
        if test != None:
            self.mpl_dict = test
            self.update_figure()

    def translate_location(self, location):
        data_loc = None
        location = ast.literal_eval(location)
        if len(location) == 1:
            data_loc = self.data[location[0]][:]
        elif len(location) == 2:
            try:
                data_loc = self.data[location[0]][:,int(location[1])]
            except:
                data_loc = self.data[location[0]][location[1]][:]
        elif len(location) == 3:
            try:
                data_loc = self.data[location[0]][:,int(location[1]), int(location[2])]
            except:
                data_loc = self.data[location[0]][location[1]][:,int(location[2])]
        elif len(location) == 4:
            try:
                data_loc = self.data[location[0]][:,int(location[1]), int(location[2]), int(location[3])]
            except:
                data_loc = self.data[location[0]][:,int(location[1]), int(location[2])][location[3]]
        return data_loc


class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 simple window - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # Widgets are movable.
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        kinetics = h5py.File('direct.h5', 'r')
        dc = MyMplCanvas(self.main_widget, width=10, height=8, dpi=100, data=kinetics, notify_func=self.notify)
        self.save_button = self.newButton(self, "Save", "Saves the Figure", (250,self.height-30), dc.save_figure, click_args=None)
        self.load_button = self.newButton(self, "Load Yaml", "Loads the Config", (250,self.height-30), dc.load_yaml, click_args=None)
        self.text = self.newTextBox(self, size=(0,0), pos=(self.save_button.button.width()+250, self.height-30), init_text="{}".format(kinetics))
        self.mplTree = self.newTree(self, dc.mpl_dict, pos=(self.width-250,0), size=(250,self.height-30), col=1, function=dc.update_figure, rows=True)
        self.dataTree = self.newTree(self, dict(kinetics), pos=(0, 0), size=(250,self.height-30), col=3, clickable=True, editable=False, function=self.text.showText, get_figures=self.mplTree.getFigures)

        # Try the scroll!
        self.scroll = QScrollArea(self.main_widget)
        #self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(False)
        scrollContent = QWidget(self.scroll)

        scrollLayout = QVBoxLayout(scrollContent)
        scrollContent.setLayout(scrollLayout)
        scrollLayout.addWidget(dc)
        self.scroll.setWidget(scrollContent)
        self.layout.addWidget(self.scroll)

        #self.layout.addWidget(dc)
        self.main_widget.move(250,0)
        self.main_widget.setGeometry(250, 0, self.width-500, (self.height-25))
        self.main_widget.setLayout(self.layout)
        #button = self.newButton(self, "Button!", "Nothing", (100,70), self.button_test, click_args=None)
        testDict = {'0': ['0', '1'], '1': {'A': ['2'], 'B': ['3', '4']}}
        #def __init__(self, parent, size, pos, init_text=""):
        #print(dir(layout))
        #layout.addChildWidget(self.dataTree)
        self.show()

    def notify(self, text):
        self.text.showText(str(text))

    def resizeEvent(self, event):
        # size().height/width should do it.
        self.resizeAll(event.size().height, event.size().width)
        pass

    def resizeAll(self, height, width):
        self.dataTree.tree.resize(self.dataTree.tree.width(), height()-30)
        self.mplTree.tree.setGeometry(width()-250, 0, 250, height()-30)
        self.main_widget.setGeometry(250, 0, width()-500, (height()-25))
        self.save_button.button.move(0,height()-30)
        self.load_button.button.move(self.save_button.button.width(),height()-30)
        self.text.textBox.setGeometry(self.save_button.button.width()+self.load_button.button.width(), height()-30, width()-self.save_button.button.width(), 30)

    def keyPressEvent(self, e):
        # This is our key press handler.  It's mostly just a stub right now.
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def wheelEvent(self, e):
        # This is what happens when we scroll.
        #print(self.tree.data)
        pass

    # Data loading; for now, just do hdf5

    # For displaying data in a tree.
    class newTree():
        def __init__(self, parent, data, pos, col=1, rows=True, size=None, editable=True, clickable=False, function=None, get_figures=None):
            self.tree = QTreeWidget(parent)
            self.tree.setColumnCount(col)
            self.parent = parent
            self.get_figures = get_figures
            self.col = col
            self.pos = pos
            self.size = size
            #A = QTreeWidgetItem(self.tree, ["A"])
            self.data = data
            if size:
                self.tree.setGeometry(pos[0], pos[1], size[0], size[1])
            self.function = function
            self.editable = editable
            #self.tree.move(pos[0], pos[1])
            # How should we handle this?  Like dictionaries, let's assume.
            self.rows = rows
            self.treeItemKeyDict = {}
            self.figures = None
            self.updateTree()
            if editable:
                self.tree.itemChanged.connect(self.onItemChanged)
            if clickable:
                self.tree.clicked.connect(self.onClicked)
            self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tree.customContextMenuRequested.connect(self.contextMenuEvent)

        def contextMenuEvent(self, event):
            menu = QMenu()
            e_action = QAction(str(event), self.tree)
            menu.addAction(e_action)
            menu.popup(QCursor.pos())
            print("NEW EVENT")
            #print(event)
            #print(dir(event))
            #print((event.x(), event.y()))
            #print(QCursor.pos())
            #print(self.tree.indexAt(QCursor.pos()))
            #print(dir(self.tree.indexAt(event)))
            horizontal = event
            horizontal.setX(0)
            #print(dir(horizontal))
            #print(self.tree.indexAt(event).data())
            #print(self.tree.indexAt(horizontal).data())
            #print(str(self.tree.indexAt(horizontal)))
            index = self.tree.indexAt(horizontal)
            print(self.tree.itemFromIndex(index))
            location = self.treeItemKeyDict[str(self.tree.itemFromIndex(index))]
            print(location)
            #print(self.tree.indexAt((event.x(), event.y())))

        def updateData(data):
            self.data = data
            self.updateTree()

        def updateTree(self):
            # Python 3 just uses items, not iteritems.
            #self.tree = QTreeWidget(self.parent)
            #self.tree.setColumnCount(self.col)
            #A = QTreeWidgetItem(self.tree, ["A"])
            if self.size:
                self.tree.setGeometry(self.pos[0], self.pos[1], self.size[0], self.size[1])
            if type(self.data) == dict:
                self.handleDict(self.data, self.tree)

        def getFigures(self):
            return self.figures

        def handleDict(self, dict_data, tree, key_list=[]):
            # We can actually have numerous structures, here.
            # Why not keep track of it, for now?
            # We want to do a reverse lookup
            for key, val in dict_data.items():
                keyTree = QTreeWidgetItem(tree, [str(key)])
                self.treeItemKeyDict[str(keyTree)] = key_list + [str(key)]
                if key == 'Figures':
                    self.figures = keyTree
                if type(val) == dict:
                    self.handleDict(val, keyTree, key_list + [str(key)])
                elif type(val) == h5py._hl.dataset.Dataset:
                    if len(val.shape) == 1:
                        # Here, we don't want to display everything in the list.  Just... let it be.
                        valTree = QTreeWidgetItem(keyTree, [str(val)])
                        self.treeItemKeyDict[str(valTree)] = key_list + [str(key)]
                        if hasattr(val, 'dtype'):
                            if len(val.dtype) > 1:
                                for iv in range(0, len(val.dtype)):
                                    dtypeTree = QTreeWidgetItem(valTree, [str(val.dtype.names[iv])])
                                    self.treeItemKeyDict[str(dtypeTree)] = key_list + [str(key)] + [str(val.dtype.names[iv])]
                    elif len(val.shape) > 1:
                        for n in range(1, len(val.shape)):
                            for i in range(0, n):
                                for j in range(0, n):
                                    if i != j:
                                        # Iterate through and add each dimension that isn't time to the list.
                                        valTree = QTreeWidgetItem(keyTree, [str(key), str(i), str(j)])
                                        self.treeItemKeyDict[str(valTree)] = key_list + [str(key), str(i), str(j)]
                                        if hasattr(val, 'dtype'):
                                            if len(val.dtype) > 1:
                                                for iv in range(0, len(val.dtype)):
                                                    dtypeTree = QTreeWidgetItem(valTree, [str(val.dtype.names[iv])])
                                                    self.treeItemKeyDict[str(dtypeTree)] = key_list + [str(key)] + [str(i), str(j)] + [str(val.dtype.names[iv])]
                else:
                    # We want this to be like rows, not columns
                    if self.rows:
                        if type(val) == list:
                            for iv, v in enumerate(val):
                                valTree = QTreeWidgetItem(keyTree, [str(v)])
                                self.treeItemKeyDict[str(valTree)] = key_list + [str(key)] + [iv]
                                if self.editable:
                                    valTree.setFlags(valTree.flags() | QtCore.Qt.ItemIsEditable)
                        else:
                            valTree = QTreeWidgetItem(keyTree, [str(val)])
                            self.treeItemKeyDict[str(valTree)] = key_list + [str(key)]
                            if self.editable:
                                valTree.setFlags(valTree.flags() | QtCore.Qt.ItemIsEditable)
                    else:
                        del self.treeItemKeyDict[str(keyTree)]
                        del keyTree
                        valTree = QTreeWidgetItem(tree, [str(key), str(val)])
                        self.treeItemKeyDict[str(valTree)] = key_list + [str(key)]
                        if self.editable:
                            valTree.setFlags(valTree.flags() | QtCore.Qt.ItemIsEditable)

        def onItemChanged(self, test):
            # This works.
            #print("Changed!")
            #print(self.treeItemKeyDict[str(test)])
            # Find the key in the data.
            #print(dir(test))
            val = self.data
            x = self.data
            # Recurse through the dictionary
            if self.rows:
                for key in self.treeItemKeyDict[str(test)]:
                    if type(x.get(key)) == dict:
                        val = val.get(key)
                        x = x.get(key)
                        print(key)
            else:
                print(self.treeItemKeyDict[str(test)])
                for key in self.treeItemKeyDict[str(test)]:
                    if type(x.get(key)) == dict:
                        val = val.get(key)
                        x = x.get(key)
                        print(key)
            # Because we return the child widget, this is fine.
            # You can't have non list data, so enforce list type.
            # Well, that won't work for mpl stuff, so.
            #try:
            val[key] = test.data(0,0)
            #except:
            #    val = test.data(0,0)
            #print(dir(test))
            # This just lets us see if we're changing a default.  UPDATE THIS ROUTINE IF YOU ADD MORE PARAMETERS.
            # But generally, they should be nested about 1 deep, so.
            try:
                oldkey = self.treeItemKeyDict[str(test)][-2]
            except:
                oldkey = self.treeItemKeyDict[str(test)][-1]
            defaults = True
            print(key, oldkey)
            # TEST code
            #print("TESTING")
            #print(dir(self.tree))
            if key == 'Rows' or key == 'Columns' or key == 'Datasets' or key == 'FilesToLoad' or oldkey == 'DSetDefaults' or oldkey == 'FigDefaults':
                defaults = False
            if self.function:
                self.function(defaults)
            if not defaults:
                self.tree.itemChanged.disconnect()
                self.tree.clear()
                self.updateTree()
                self.tree.itemChanged.connect(self.onItemChanged)
            # We also need to rebuild our tree, unfortunately.
            # Although this loops forever, so I'm missing something.
            # I'm not sure why it doesn't properly... update the whole thing?
            #print(test.data(0,0))

        def onClicked(self, test):
            #print(self.tree.selectedItems())
            #print(self.treeItemKeyDict)
            # This is the thing which will actually return our dataset.
            #print(self.treeItemKeyDict[str(self.tree.selectedItems()[0])])
            location = self.treeItemKeyDict[str(self.tree.selectedItems()[0])]
            print(str(self.tree.selectedItems()[0]))
            # One thing we don't know is precisely how to format this, but that's okay.
            # We could just change this later.
            # We should probably store how we formatted it with the reverse dictionary, but.
            if self.function:
                self.function(str(location))

    class newTextBox():
        def __init__(self, parent, size, pos, init_text=""):
            self.textBox = QLineEdit(parent)
            self.textBox.setText(init_text)

        def showText(self, text):
            self.textBox.setText(text)

    class newButton():
        def __init__(self, parent, label, tooltip, pos, function, click_args=None):
            # pos should be an x,y tooltip
            # Generic implementation of a button.
            # The function needs a pyqtSlot decorator, and should probably be pickable.
            self.button = QPushButton(label, parent)
            self.button.move(pos[0], pos[1])
            self.click_args = click_args
            self.function = function
            self.button.clicked.connect(self.function)

    # For our buttons.
    @pyqtSlot()
    def button_test(self):
        print("We're clicking a button, wheee")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


