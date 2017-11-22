#! /usr/bin/python3

# Stuff to get the window open.
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QTreeWidget, QTreeWidgetItem, QGraphicsAnchorLayout, QScrollArea, QLineEdit, QMenu, QAction, QDockWidget, QMainWindow, QHBoxLayout
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
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import key_press_handler

# Button Functions
@pyqtSlot()
def button_test():
    print("We're clicking a button, wheee")

# Now, from that other site...
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, data_parent=None, width=7, height=4, dpi=300, num=1, data=None, notify_func=None):
        self.data = data
        self.notify_func = notify_func
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # Oddly, we don't care
        self.parent = data_parent
        FigureCanvas.__init__(self, self.fig)
        # Track the mouse position.
        self.setMouseTracking(True)
        # Can't remembr what this is for; qt, most likely.
        self.hoverAxes = None
        self.activeAxes = None
        self.setParent(parent)

        # Set the size policy such that we can't be squished, but will 
        # instead simply grow and shrink with the dpi.
        # We call updateGeometry upon changing the dpi to ensure grow to our new window size.
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Fixed,
                QSizePolicy.Fixed)
        FigureCanvas.updateGeometry(self)

        # Initial update call.
        self.update_figure()
        # Some code for when we would like to do a movie later, maybe.
        ##timer = QtCore.QTimer(self)
        ##timer.timeout.connect(self.update_figure)
        ##timer.start(1000)

    def plot(self, pd, index, ax):
        # pd is the plot dictionary
        ax.tick_params(axis='both', labelsize=float(self.parent.mpl_dict['fontsize']['fontsize']), length=self.parent.mpl_dict['fontsize']['ticksize'])
        if pd['ylabel'] is not None:
            ax.set_ylabel(pd['ylabel'], fontsize=float(self.parent.mpl_dict['fontsize']['titlesize']), fontweight='bold')
        if pd['xlabel'] is not None:
            ax.set_xlabel(pd['xlabel'], fontsize=float(self.parent.mpl_dict['fontsize']['titlesize']), fontweight='bold')
        if pd['title'] is not None:
            ax.set_title(pd['title'], fontsize=float(self.parent.mpl_dict['fontsize']['titlesize']), fontweight='bold')
        if pd['data'][str(index)]['loc'] != 'None':
            if pd['type'] == 'plot':
                try:
                    subplot_kwargs = dict(pd['data'][str(index)])
                    del subplot_kwargs['loc']
                    del subplot_kwargs['range']
                    for k in subplot_kwargs.keys():
                        if type(k) == str and len(k) >= 6:
                            if k[0:7] == 'valTree' or k[0:7] == 'keyTree':
                                del subplot_kwargs[k]
                    if subplot_kwargs['color'] == -1:
                        subplot_kwargs['color'] = self.parent.mpl_dict['Colors'][str(index)]
                    handle = ax.plot(self.translate_location(pd['data'][str(index)]['loc']), **subplot_kwargs)
                    return handle
                except Exception as e:
                    if self.notify_func is not None:
                        self.notify_func(e)
                    else:
                        pass
            if pd['type'] == 'shade':
                #try:
                if True:
                    subplot_kwargs = {}
                    for key,val in pd['data'][str(index)].items():
                        if type(key) == str and len(key) >= 6:
                            if key[0:7] != 'valTree' and key[0:7] != 'keyTree':
                                if key[0:7] != 'valtree' and key[0:7] != 'keytree':
                                    subplot_kwargs[key] = val
                        else:
                            subplot_kwargs[key] = val
                    print(subplot_kwargs)
                    del subplot_kwargs['loc']
                    del subplot_kwargs['range']
                    if subplot_kwargs['color'] == -1:
                        subplot_kwargs['color'] = str(self.parent.mpl_dict['Colors'][index])
                    elif str(subplot_kwargs['color'])[0] == "#":
                        pass
                    else:
                        subplot_kwargs['color'] = self.parent.mpl_dict['Colors'][int(subplot_kwargs['color'])]
                    ax.plot(self.translate_location(pd['data'][str(index)]['loc'])['expected'][:], **subplot_kwargs)
                    subplot_kwargs['alpha'] = .3
                    handle = ax.fill_between(range(0, self.translate_location(pd['data'][str(index)]['loc'])['expected'].shape[0]), self.translate_location(pd['data'][str(index)]['loc'])['ci_ubound'][:], self.translate_location(pd['data'][str(index)]['loc'])['ci_lbound'][:], **subplot_kwargs)
                    return handle
                '''except Exception as e:
                    if self.notify_func is not None:
                        self.notify_func(e)
                    else:
                        pass'''
                #self.axes

    def updateFromDict(self):
        d = self.parent.mpl_dict
        # Clears the figure before we plot more.
        if self.parent.mpl_dict['Update'] == True:
            self.fig.clear()
            self.axes = self.fig.subplots(nrows=int(d['Rows']), ncols=int(d['Columns']))
            self.al = {}
            for rows in range(0, int(self.parent.mpl_dict['Rows'])):
                for cols in range(0, int(self.parent.mpl_dict['Columns'])):
                    self.al[(rows,cols)] = [0,0]
            self.fig.set_dpi(int(d['dpi']))
            self.fig.set_size_inches(float(d['figsize']['width']), float(d['figsize']['height']))
            FigureCanvas.updateGeometry(self)
            self.parent.mpl_dict['Update'] = False
        print(self.parent.mpl_dict['Update'])
        # We check to see if we need to update the figures.
        # This should just occur on a rebuild, so if we haven't added anything, don't worry about it.
        active = False
        plotted = False
        for rows in range(0, int(self.parent.mpl_dict['Rows'])):
            for cols in range(0, int(self.parent.mpl_dict['Columns'])):
                # Throw in the axes object.
                for dset in range(0, int(self.parent.mpl_dict['Datasets'])):
                    if self.parent.mpl_dict['Active'] == str((rows,cols)):
                        self.axes[rows,cols].spines['bottom'].set_color("r")
                        self.axes[rows,cols].spines['left'].set_color("r")
                    else:
                        self.axes[rows,cols].spines['bottom'].set_color("black")
                        self.axes[rows,cols].spines['left'].set_color("black")
                    if self.parent.mpl_dict['Figures'][str((rows,cols))]['Update'] == True:
                        self.axes[rows,cols].clear()
                        self.plot(self.parent.mpl_dict['Figures'][str((rows,cols))], dset, self.axes[rows,cols])
                        self.parent.mpl_dict['Figures'][str((rows,cols))]['Update'] = False
                        plotted = True
            if plotted:
                self.fig.tight_layout()
                    

    def mouseMoveEvent(self, event):
        # translate into MPL coordinates
        coord = event.pos()
        x = coord.x()
        y = coord.y()
        h = float(self.parent.mpl_dict['figsize']['height'])
        w = float(self.parent.mpl_dict['figsize']['width'])
        dpi = float(self.parent.mpl_dict['dpi'])
        for box, i, j in self.returnAxesPos():
            pnts = box.get_points()
            # pnts: [[x0, y0], [x1, y1]]
            x1 = pnts[0,0]
            x2 = pnts[1,0]
            y1 = pnts[0,1]
            y2 = pnts[1,1]
            # THIS is the correct transformation.
            #print([[x1, (h*dpi)-y2], [x2, (h*dpi)-y1]], x, y)

            if x > x1 and x < x2 and y > (h*dpi)-y2 and y < (h*dpi)-y1:
                self.hoverAxes = str((i,j))

    def mousePressEvent(self, event):
        if self.hoverAxes is not None:
            self.parent.mpl_dict['Active'] = self.hoverAxes
            # For some reason, doing this screws everything up.  Have to look into that.
            #self.parent.mpl_dict['keyTree.Active'].setText(1, str(self.hoverAxes))
            #self.activeAxes = self.hoverAxes
            FigureCanvas.mousePressEvent(self, event)
            self.update_figure()

    def returnAxesPos(self):
        return_list = []
        for i in range(0, self.axes.shape[0]):
            for j in range(0, self.axes.shape[1]):
                #print(dir(self.axes[i,j]))
                #return_list.append((self.axes[i,j].get_position(), i, j))
                return_list.append((self.axes[i,j].get_window_extent(), i, j))
        return return_list


    def updateSize(self, height, width):
        pass

    def update_figure(self, defaults=True):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        # We call this whenever the dictionary is updated.
        self.updateFromDict()
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
        self.draw()
        FigureCanvas.updateGeometry(self)

    def save_figure(self):
        self.fig.savefig("test.pdf")
        with open('test.yml', 'w') as outfile:
            yaml.dump(self.parent.mpl_dict, outfile, default_flow_style=False)

    def load_yaml(self):
        test = yaml.load(open('test.yml', 'r'))
        if test != None:
            self.parent.mpl_dict = test
            self.update_figure()

    def translate_location(self, location):
        data_loc = None
        try:
            location = ast.literal_eval(location)
        except:
            pass
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


class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 simple window - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.fig_dict = '''{
                            'type': 'plot', 
                            'Update': True,
                            'ylabel': '',
                            'xlabel': '',
                            'title': ''
                            }'''
        self.dset_dict = '''{
                            'loc': 'None',
                            'range': 'None',
                            'color': -1,
                            'alpha': 1, 
                            }'''

        self.mpl_dict_lit = '''{
                                'FilesToLoad': 'IGNORE',
                                'Update': True,
                                'Active': 'None',
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
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # Widgets are movable.
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        kinetics = h5py.File('direct.h5', 'r')
        self.updateFromDict(False, firstrun=True)
        self.dc = MyMplCanvas(self.main_widget, data_parent=self, width=10, height=8, dpi=100, data=kinetics, notify_func=self.notify)
        self.save_button = self.newButton(self, "Save", "Saves the Figure", (250,self.height-30), self.dc.save_figure, click_args=None)
        self.load_button = self.newButton(self, "Load Yaml", "Loads the Config", (250,self.height-30), self.dc.load_yaml, click_args=None)
        self.text = self.newTextBox(self, size=(0,0), pos=(self.save_button.button.width()+250, self.height-30), init_text="{}".format(kinetics))
        self.mplTree = self.newTree(self, self.mpl_dict, pos=(self.width-250,0), size=(250,self.height-30), col=1, function=self.updateFromDict, rows=True)
        self.dataTree = self.newTree(self, dict(kinetics), pos=(0, 0), size=(250,self.height-30), col=3, clickable=True, editable=False, function=self.text.showText, function2=self.updateFromDict, get_figures=self.mplTree.getFigures, mpl=self.mpl_dict)
        # Do up some docks for everything!
        self.setCentralWidget(self.main_widget)

        self.mpldock = QDockWidget("Plotting Dictionary", self)
        self.mpldock.setWidget(self.mplTree.tree)

        self.datadock = QDockWidget("Dataset", self)
        self.datadock.setWidget(self.dataTree.tree)

        # Create the dock, create a new widget, create a layout for that widget, then add all the widgets into that widget, then add that widget to th dock.  Ha
        self.textdock = QDockWidget("", self)
        self.bwidget = QWidget(self)
        self.toolbar = NavigationToolbar(self.dc, self.bwidget)
        self.dc.mpl_connect('key_press_event', self.on_key_press)
        self.blayout = QHBoxLayout(self.textdock)
        self.blayout.addWidget(self.text.textBox)
        self.blayout.addWidget(self.save_button.button)
        self.blayout.addWidget(self.load_button.button)
        self.blayout.addWidget(self.toolbar)
        self.bwidget.setLayout(self.blayout)
        # Remove title bar.
        self.textdock.setTitleBarWidget(QWidget())
        self.textdock.setWidget(self.bwidget)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.mpldock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.datadock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.textdock)
        # Try the scroll!
        self.scroll = QScrollArea(self.main_widget)
        #self.scroll.setWidgetResizable(False)
        self.scroll.setWidgetResizable(True)
        scrollContent = QWidget(self.scroll)

        scrollLayout = QVBoxLayout(scrollContent)
        scrollContent.setLayout(scrollLayout)
        scrollLayout.addWidget(self.dc)
        self.scroll.setWidget(scrollContent)
        self.layout.addWidget(self.scroll)

        '''self.main_widget.move(250,0)
        self.main_widget.setGeometry(250, 0, self.width-500, (self.height-25))'''
        self.main_widget.setLayout(self.layout)
        #button = self.newButton(self, "Button!", "Nothing", (100,70), self.button_test, click_args=None)
        testDict = {'0': ['0', '1'], '1': {'A': ['2'], 'B': ['3', '4']}}
        #def __init__(self, parent, size, pos, init_text=""):
        #layout.addChildWidget(self.dataTree)
        self.show()

    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.dc, self.toolbar)

    def notify(self, text):
        self.text.showText(str(text))

    def refreshWidgets(self):
        self.mplTree.parent.mpl_dict = self.mpl_dict
        self.dataTree.parent.mpl_dict = self.mpl_dict
        self.dc.parent.mpl_dict = self.mpl_dict
        # Danger; recursion.
        self.mplTree.updateTree()
        #self.dataTree.updateTree()
        self.dc.update_figure()
        #pass

    def updateFromDict(self, defaults=False, firstrun=False):
        d = self.mpl_dict
        # Clears the figure before we plot more.
        # We check to see if we need to update the figures.
        # This should just occur on a rebuild, so if we haven't added anything, don't worry about it.
        for rows in range(0, int(self.mpl_dict['Rows'])):
            for cols in range(0, int(self.mpl_dict['Columns'])):
                if defaults:
                    # If we haven't changed the defaults, don't upstate the state.
                    if str((rows, cols)) not in self.mpl_dict['Figures']:
                        #self.mpl_dict['Figures'][str((rows,cols))] = ast.literal_eval(self.fig_dict)
                        new_dict = {}
                        for key, val in self.mpl_dict['FigDefaults'].items():
                            if type(key) == str and len(key) >= 6:
                                if key[0:7] != 'keyTree' and key[0:7] != 'valTree':
                                    new_dict[key] = val
                            else:
                                new_dict[key] = val
                        if str((rows,cols)) not in self.mpl_dict['Figures']:
                            new = True
                        else:
                            new = False
                        tree_dict = {}
                        if not new:
                            for key, val in self.mpl_dict['Figures'][str((rows,cols))].items():
                                if type(key) == str and len(key) >= 6:
                                    if key[0:7] == 'keyTree' and key[0:7] == 'valTree':
                                        tree_dict[key] = val
                        self.mpl_dict['Figures'][str((rows,cols))] = copy.deepcopy(new_dict)
                        self.mpl_dict['Figures'][str((rows,cols))].update(tree_dict)
                else:
                    new_dict = {}
                    for key, val in self.mpl_dict['FigDefaults'].items():
                        if type(key) == str and len(key) >= 6:
                            if key[0:7] != 'keyTree' and key[0:7] != 'valTree':
                                new_dict[key] = val
                        else:
                            new_dict[key] = val
                    if str((rows,cols)) not in self.mpl_dict['Figures']:
                        new = True
                    else:
                        new = False
                    tree_dict = {}
                    if not new:
                        for key, val in self.mpl_dict['Figures'][str((rows,cols))].items():
                            if type(key) == str and len(key) >= 6:
                                if key[0:7] == 'keyTree' and key[0:7] == 'valTree':
                                    tree_dict[key] = val
                    self.mpl_dict['Figures'][str((rows,cols))] = copy.deepcopy(new_dict)
                    self.mpl_dict['Figures'][str((rows,cols))].update(tree_dict)
                for dset in range(0, int(self.mpl_dict['Datasets'])):
                    if defaults:
                        if str(dset) not in self.mpl_dict['Figures'][str((rows,cols))]['data']:
                            #self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = ast.literal_eval(self.dset_dict)
                            new_dict = {}
                            for key, val in self.mpl_dict['DSetDefaults'].items():
                                if type(key) == str and len(key) >= 6:
                                    if key[0:7] != 'keyTree' and key[0:7] != 'valTree':
                                        new_dict[key] = val
                                else:
                                    new_dict[key] = val
                            if str(dset) not in self.mpl_dict['Figures'][str((rows,cols))]['data']:
                                new = True
                            else:
                                new = False
                            tree_dict = {}
                            if not new:
                                for key, val in self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)].items():
                                    if type(key) == str and len(key) >= 6:
                                        if key[0:7] == 'keyTree' and key[0:7] == 'valTree':
                                            tree_dict[key] = val
                            self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = copy.deepcopy(new_dict)
                            self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)].update(tree_dict)
                    else:
                        #self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = copy.copy(self.mpl_dict['DSetDefaults'])
                        new_dict = {}
                        for key, val in self.mpl_dict['DSetDefaults'].items():
                            if type(key) == str and len(key) >= 6:
                                if key[0:7] != 'keyTree' and key[0:7] != 'valTree':
                                    new_dict[key] = val
                            else:
                                new_dict[key] = val
                        # We don't really want to create new keys, so.
                        if str(dset) not in self.mpl_dict['Figures'][str((rows,cols))]['data']:
                            new = True
                        else:
                            new = False
                        tree_dict = {}
                        if not new:
                            for key, val in self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)].items():
                                if type(key) == str and len(key) >= 6:
                                    if key[0:7] == 'keyTree' and key[0:7] == 'valTree':
                                        tree_dict[key] = val
                        self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = copy.deepcopy(new_dict)
                        self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)].update(tree_dict)

                # Throw in the axes object.
                #print(self.mpl_dict['Figures'][(rows,cols)])
        #self.dc.update_figure(defaults)
        if not firstrun:
            self.refreshWidgets()

    '''def resizeEvent(self, event):
        # size().height/width should do it.
        self.resizeAll(event.size().height, event.size().width)
        pass'''

    def resizeAll(self, height, width):
        #self.dataTree.tree.resize(self.dataTree.tree.width(), height()-30)
        #self.mplTree.tree.setGeometry(width()-250, 0, 250, height()-30)
        #self.main_widget.setGeometry(250, 0, width()-500, (height()-25))
        self.main_widget.setGeometry(0, 0, width(), (height()-25))
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
        def __init__(self, parent, data, pos, col=1, rows=True, size=None, editable=True, clickable=False, function=None, get_figures=None, mpl=None, function2=None):
            self.tree = QTreeWidget(parent)
            self.tree.setColumnCount(col+1)
            self.parent = parent
            self.get_figures = get_figures
            self.col = col+1
            self.pos = pos
            self.size = size
            print(self.tree.setSizePolicy)
            self.tree.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
                #QSizePolicy.Expanding,
            #A = QTreeWidgetItem(self.tree, ["A"])
            self.data = data
            if size:
                self.tree.setGeometry(pos[0], pos[1], size[0], size[1])
            if mpl:
                self.mpl = mpl
            self.function = function
            self.function2 = function2
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
            print("NEW EVENT")
            # Just get the horizontal value; we want anything in this row.
            horizontal = event
            horizontal.setX(0)
            index = self.tree.indexAt(horizontal)
            location = self.treeItemKeyDict[str(self.tree.itemFromIndex(index))]
            # Now we have the actual menu item we need to send to the dictionary.  That's location.
            # Now, create the menu...
            self.menu = QMenu()
            # Add a series of actions.  So far, we just want this simple: subplots, and datasets.  Send em on!
            self.itemDict = {}
            i = 0
            # This is misguided, as basically QT doesn't want to send any particular functions.
            #for key,val in self.parent.mpl_dict['Figures'].items():
            #    if type(val) == dict:
            #        for dkey,dval in val['data'].items():
            #            if type(dval) != QTreeWidgetItem:
            dkey = self.parent.mpl_dict['Active']
            send_action = QAction("Send: {}".format(str(dkey)), self.tree)
            #send_action.triggered.connect(lambda key, dkey, location : self.reassignMpl(key, dkey, location))
            #onSend = { 'key': key, 'dkey': dkey, 'location': location }
            #self.itemDict[i] = onSend
            # Sort of works?  In a "doesn't work" type of way.
            #send_action.triggered.connect(lambda: self.reassignMpl(key, dkey, location))
            send_action.triggered.connect(lambda: self.reassignMpl(location))
            self.menu.addAction(send_action)
            #i += 1
            #e_action = QAction(str(event), self.tree)
            #self.menu.addAction(e_action)
            #print(self.menu.activeAction())
            self.menu.popup(QCursor.pos())

        def reassignMpl(self, location):
            #print(i)
            #print(self.menu.actionAt(i))
            #print(i.i)
            #key = self.itemDict[i.i]['key']
            #dkey = self.itemDict[i.i]['dkey']
            #location = self.itemDict[i.i]['location']
            #tmp = self.mpl.get(['Figures'][key]['data'][dkey]) 
            #tmp = self.parent.mpl_dict.get('Figures')
            #tmp = tmp.get(key)
            #tmp = tmp.get('data')
            #tmp = tmp.get(dkey)
            #tmp['loc'] = location
            # Forc dictionary update?
            #d = copy.deepcopy(self.parent.mpl_dict)
            #print(key, dkey, location)
            #self.parent.mpl_dict['Figures'][str(key)]['data'][str(dkey)]['loc'] = location
            #self.parent.mpl_dict['Figures'][str(key)]['data'][str(dkey)]['valTree.loc'].setText(0, str(location))
            key = self.parent.mpl_dict['Active']
            self.parent.mpl_dict['Figures'][str(key)]['data']['0']['loc'] = location
            self.parent.mpl_dict['Figures'][str(key)]['Update'] = True
            self.parent.mpl_dict['Figures'][str(key)]['data']['0']['keyTree.loc'].setText(1, str(location))
            #self.parent.mpl_dict = copy.deepcopy(d)

            #tmp = self.parent.mpl_dict.get(['Figures'][key]['data'])
            #tmp[dkey]['loc'] = location
            self.parent.refreshWidgets()
            #self.function2()

        def updateData(data):
            self.data = data
            self.updateTree()

        def updateTree(self):
            # Python 3 just uses items, not iteritems.
            #self.tree = QTreeWidget(self.parent)
            #self.tree.setColumnCount(self.col)
            #A = QTreeWidgetItem(self.tree, ["A"])
            try:
                self.tree.itemChanged.disconnect()
            except:
                pass
            #self.tree.clear()
            #if self.size:
            #    self.tree.setGeometry(self.pos[0], self.pos[1], self.size[0], self.size[1])
            if type(self.data) == dict:
                self.handleDict(self.data, self.tree)
            self.tree.itemChanged.connect(self.onItemChanged)

        def getFigures(self):
            return self.figures

        def handleDict(self, dict_data, tree, key_list=[]):
            # We can actually have numerous structures, here.
            # Why not keep track of it, for now?
            # We want to do a reverse lookup
            ddc = copy.copy(dict_data)
            con = False
            for key, val in ddc.items():
                if type(key) == str and len(key) >= 6:
                    if key[0:7] != 'keyTree' and key[0:7] != 'valTree':
                        con = True
                    else:
                        con = False
                else:
                    con = True
                if con:
                    if 'keyTree.{}'.format(key) not in dict_data:
                        keyTree = QTreeWidgetItem(tree, [str(key)])
                        dict_data['keyTree.{}'.format(key)] = keyTree
                        self.treeItemKeyDict[str(keyTree)] = key_list + [str(key)]
                    else:
                        keyTree = dict_data['keyTree.{}'.format(key)]
                        keyTree.setText(0, str(key))
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
                                    if self.editable:
                                        keyTree.setFlags(keyTree.flags() | QtCore.Qt.ItemIsEditable)
                                    keyTree.setText(iv+1, str(v))
                                    self.col += iv
                            else:
                                if self.editable:
                                    keyTree.setFlags(keyTree.flags() | QtCore.Qt.ItemIsEditable)
                                keyTree.setText(1, str(val))
                        else:
                            del self.treeItemKeyDict[str(keyTree)]
                            del keyTree
                            valTree = QTreeWidgetItem(tree, [str(key), str(val)])
                            self.treeItemKeyDict[str(valTree)] = key_list + [str(key)]
                            if self.editable:
                                valTree.setFlags(valTree.flags() | QtCore.Qt.ItemIsEditable)
            self.tree.setColumnCount(self.col)

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
            else:
                for key in self.treeItemKeyDict[str(test)]:
                    if type(x.get(key)) == dict:
                        val = val.get(key)
                        x = x.get(key)
            # Because we return the child widget, this is fine.
            # You can't have non list data, so enforce list type.
            # Well, that won't work for mpl stuff, so.
            #try:
            val[key] = test.data(1,0)
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
            # TEST code
            #print("TESTING")
            #print(dir(self.tree))
            if key == 'width' or key == 'height' or key == 'dpi' or key == 'Rows' or key == 'Columns' or key == 'Datasets' or key == 'FilesToLoad' or oldkey == 'DSetDefaults' or oldkey == 'FigDefaults':
                defaults = False
                self.parent.mpl_dict['Update'] = True
            print(key, oldkey)
            keys = self.treeItemKeyDict[str(test)]
            print(keys)
            if keys[0] == 'Figures':
                self.parent.mpl_dict['Figures'][str(keys[1])]['Update'] = True
            if self.function:
                self.function(defaults)
            #if not defaults:
            #    self.tree.itemChanged.disconnect()
            #    self.tree.clear()
            self.updateTree()
            #    self.tree.itemChanged.connect(self.onItemChanged)
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


