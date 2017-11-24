#! /usr/bin/python3

# Stuff to get the window open.
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QTreeWidget, QTreeWidgetItem, QGraphicsAnchorLayout, QScrollArea, QLineEdit, QMenu, QAction, QDockWidget, QMainWindow, QHBoxLayout, QTextEdit
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

def remove_trees(idict, odict=None):
    if odict == None:
        odict = {}
    for key, val in idict.items():
        if type(key) == str and len(key) >= 6:
            if key[0:7] != 'valTree' and key[0:7] != 'keyTree' and key != 'Update':
                if type(val) == dict:
                    odict[key] = copy.deepcopy(remove_trees(val))
                else:
                    odict[key] = copy.deepcopy(val)
        else:
            if type(val) == dict:
                odict[key] = copy.deepcopy(remove_trees(val))
            else:
                odict[key] = copy.deepcopy(val)
    return odict


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
        ax.tick_params(axis='both', labelsize=float(self.parent.mpl_dict['fontsize']['fontsize']), length=int(self.parent.mpl_dict['fontsize']['ticksize']))
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
                    '''del subplot_kwargs['loc']
                    del subplot_kwargs['range']
                    for k in subplot_kwargs.keys():
                        if type(k) == str and len(k) >= 6:
                            if k[0:7] == 'valTree' or k[0:7] == 'keyTree':
                                del subplot_kwargs[k]'''
                    subplot_kwargs = remove_trees(subplot_kwargs)
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
                    '''subplot_kwargs = {}
                    for key,val in pd['data'][str(index)].items():
                        if type(key) == str and len(key) >= 6:
                            if key[0:7] != 'valTree' and key[0:7] != 'keyTree':
                                if key[0:7] != 'valtree' and key[0:7] != 'keytree':
                                    subplot_kwargs[key] = val
                        else:
                            subplot_kwargs[key] = val'''
                    subplot_kwargs = dict(pd['data'][str(index)])
                    subplot_kwargs = remove_trees(subplot_kwargs)
                    del subplot_kwargs['loc']
                    del subplot_kwargs['range']
                    if subplot_kwargs['color'] == -1:
                        subplot_kwargs['color'] = str(self.parent.mpl_dict['Colors'][index])
                    elif str(subplot_kwargs['color'])[0] == "#":
                        pass
                    else:
                        subplot_kwargs['color'] = self.parent.mpl_dict['Colors'][subplot_kwargs['color']]
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
            # This means that we're updating from the defaults.
            self.fig.clear()
            #self.axes = self.fig.subplots(nrows=int(d['Rows']), ncols=int(d['Columns']))
            gridspec_kw = self.parent.mpl_dict['gridspec_kw']
            subplot_kw = self.parent.mpl_dict['subplot_kw']
            self.axes = self.fig.subplots(nrows=int(d['Rows']), ncols=int(d['Columns']), gridspec_kw=gridspec_kw, **subplot_kw)
            self.al = {}
            for rows in range(0, int(self.parent.mpl_dict['Rows'])):
                for cols in range(0, int(self.parent.mpl_dict['Columns'])):
                    # We need to update everything.
                    # So trigger a redraw.
                    self.parent.mpl_dict['Figures'][str((rows,cols))]['Update'] = True
                    self.axes[rows,cols]
            self.fig.set_dpi(int(d['dpi']))
            self.fig.set_size_inches(float(d['figsize']['width']), float(d['figsize']['height']))
            FigureCanvas.updateGeometry(self)
            self.parent.mpl_dict['Update'] = False
        if self.parent.mpl_dict['Resize'] == True:
            self.parent.mpl_dict['Resize'] = False
            self.fig.set_dpi(int(d['dpi']))
            self.fig.set_size_inches(float(d['figsize']['width']), float(d['figsize']['height']))
            FigureCanvas.updateGeometry(self)
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
                    if 'Update' not in self.parent.mpl_dict['Figures'][str((rows,cols))]:
                        self.parent.mpl_dict['Figures'][str((rows,cols))]['Update'] = True
                    if self.parent.mpl_dict['Figures'][str((rows,cols))]['Update'] == True:
                        self.axes[rows,cols].clear()
                        self.plot(self.parent.mpl_dict['Figures'][str((rows,cols))], dset, self.axes[rows,cols])
                        self.parent.mpl_dict['Figures'][str((rows,cols))]['Update'] = False
                        plotted = True
            #if plotted:
            #    self.fig.tight_layout()
                    

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

            if x > x1 and x < x2 and y > (h*dpi)-y2 and y < (h*dpi)-y1:
                self.hoverAxes = str((i,j))

    def mousePressEvent(self, event):
        if self.hoverAxes is not None:
            self.parent.mpl_dict['Active'] = self.hoverAxes
            # For some reason, doing this screws everything up.  Have to look into that.
            #self.parent.mpl_dict['keyTree.Active'].setText(1, str(self.hoverAxes))
            #self.activeAxes = self.hoverAxes
            #FigureCanvas.mousePressEvent(self, event)
            self.update_figure()

    def returnAxesPos(self):
        return_list = []
        for i in range(0, self.axes.shape[0]):
            for j in range(0, self.axes.shape[1]):
                #return_list.append((self.axes[i,j].get_position(), i, j))
                return_list.append((self.axes[i,j].get_window_extent(), i, j))
        return return_list


    def updateSize(self, height, width):
        pass

    def update_figure(self, defaults=True):
        self.updateFromDict()
        FigureCanvas.updateGeometry(self)
        self.draw()

    def translate_location_old(self, location):
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

    def translate_location(self, location):
        loc = self.data
        for i in ast.literal_eval(location):
            try:
                # Is it a string?
                loc = loc[i]
            except:
                # Definitely a tuple.
                t = ast.literal_eval(i)
                try:
                    # Some complicated slicing, here.
                    # THIS IS FOR A 3D DATASET.
                    if t[0] > t[1]:
                        #index = (slice(None, None, None), slice(t[0], None, None), slice(t[0], t[1], None))
                        index = (slice(None, None, None), slice(t[0], None, t[0]-t[1]), slice(t[1], t[0], t[0]-t[1]))
                    else:
                        #index = (slice(None, None, None), slice(t[0], t[1], None), slice(t[0], None, None))
                        index = (slice(None, None, None), slice(t[0], t[1], t[1]-t[0]), slice(t[1], None, t[1]-t[0]))
                except:
                    # Some complicated slicing, here.
                    # THIS IS FOR A 2D DATASET.
                    # In this case, we only have t[0], which is either 0, or not.
                    # We don't really have the dimensions here, but.
                    if t > 0:
                        index = (slice(None, None, None), slice(t, None, None))
                    else:
                        index = (slice(None, None, None), slice(t, t+1, None))
                loc = loc[index]
        return loc.flatten()


class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 simple window - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.fig_dict = '''{
                            'type': 'shade', 
                            'Update': True,
                            'ylabel': '',
                            'xlabel': '',
                            'title': '',
                            'height': 'None',
                            'width': 'None',
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
                                'Resize': True,
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
                                'gridspec_kw': {
                                  'left': 0.1,
                                  'right': 0.9,
                                  'bottom': 0.1,
                                  'top': 0.9,
                                  'wspace': 0.3,
                                  'hspace': 0.3,
                                 },
                                'subplot_kw': {
                                  'sharey': True,
                                  'sharex': True,
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
                                'Figures': {},
                                'keyTree': {}
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
        self.updateFromDict(True, firstrun=True)
        self.dc = MyMplCanvas(self.main_widget, data_parent=self, width=10, height=8, dpi=100, data={'direct.h5': kinetics}, notify_func=self.notify)
        self.save_button = self.newButton(self, "Save", "Saves the Figure", (250,self.height-30), self.save_figure, click_args=None)
        self.load_button = self.newButton(self, "Load Yaml", "Loads the Config", (250,self.height-30), self.load_yaml, click_args=None)
        self.text = self.newTextBox(self, size=(0,0), pos=(self.save_button.button.width()+250, self.height-30), init_text="{}".format(kinetics))
        #self.text.textBox.setGeometry(self.save_button.button.width()+self.load_button.button.width(), self.height-30, self.width-self.save_button.button.width(), 15)
        self.text.textBox.resize(self.width-self.save_button.button.width(), 15)
        self.mplTree = self.newTree(self, self.mpl_dict, pos=(self.width-250,0), size=(250,self.height-30), col=1, function=self.updateFromDict, rows=True)
        self.dataTree = self.newTree(self, {'direct.h5': dict(kinetics)}, pos=(0, 0), size=(250,self.height-30), col=3, clickable=True, editable=False, function=self.text.showText, function2=self.updateFromDict, get_figures=self.mplTree.getFigures, mpl=self.mpl_dict)
        # Do up some docks for everything!
        self.setCentralWidget(self.main_widget)

        self.mpldock = QDockWidget("Plotting Dictionary", self)
        self.mpllayout = QVBoxLayout(self.mpldock)
        self.mplwidget = QWidget(self)
        # Create buttons...
        self.addValue = self.newButton(self, "+", "Adds a new key: value", (0,0), self.addToDict, click_args=None)
        self.delValue = self.newButton(self, "-", "Deletes key: value pair", (0,0), self.delFromDict, click_args=None)
        # Add a new layout for them.
        self.mplButtonlayout = QHBoxLayout(self.mplwidget)
        self.mplButtonwidget = QWidget(self)
        self.mplButtonwidget.setLayout(self.mplButtonlayout)
        self.mplButtonlayout.addWidget(self.addValue.button)
        self.mplButtonlayout.addWidget(self.delValue.button)
        
        self.mpllayout.addWidget(self.mplTree.tree)
        self.mpllayout.addWidget(self.mplButtonwidget)
        self.mplwidget.setLayout(self.mpllayout)
        self.mpldock.setWidget(self.mplwidget)

        # Now the data dock...
        self.datadock = QDockWidget("Dataset", self)
        self.datalayout = QVBoxLayout(self.datadock)
        self.datawidget = QWidget(self)
        # Create buttons
        self.loadData = self.newButton(self, "Load Data", "Adds a new key: value", (640,0), self.addToDict, click_args=None)
        #self.dataButtonlayout = QHBoxLayout(self.datawidget)
        #self.dataButtonwidget = QWidget(self)
        #self.dataButtonwidget.setLayout(self.dataButtonlayout)
        #self.dataButtonlayout.addWidget(self.loadData.button)
        #self.dataButtonlayout.addWidget(self.delValue.button)
        self.datalayout.addWidget(self.dataTree.tree)
        #self.datalayout.addWidget(self.dataButtonwidget)
        self.datalayout.addWidget(self.loadData.button)
        self.datawidget.setLayout(self.datalayout)
        self.datadock.setWidget(self.datawidget)

        # Create the dock, create a new widget, create a layout for that widget, then add all the widgets into that widget, then add that widget to th dock.  Ha
        self.textdock = QDockWidget("", self)
        self.bwidget = QWidget(self)
        #self.toolbar = NavigationToolbar(self.dc, self.bwidget)
        #self.dc.mpl_connect('key_press_event', self.on_key_press)
        self.blayout = QHBoxLayout(self.textdock)
        self.blayout.addWidget(self.text.textBox)
        self.blayout.addWidget(self.save_button.button)
        self.blayout.addWidget(self.load_button.button)
        #self.blayout.addWidget(self.toolbar)
        #self.bwidget.setMinimumHeight((self.width-self.save_button.button.width(), 30))
        #self.text.textBox.setMinimumHeight((10))
        #self.text.textBox.setMaximumHeight((10))
        self.bwidget.setLayout(self.blayout)
        # Remove title bar.
        self.textdock.setTitleBarWidget(QWidget())
        self.textdock.setWidget(self.bwidget)
        self.textdock.resize(self.width-self.save_button.button.width(), 30)

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

    def addToDict(self):
        keys = self.mplTree.returnHighlightedDictionary()
        if keys is not None and len(keys) > 1:
            ddict = self.mplTree.getParentDict(self.mpl_dict, keys[:-1])
        else:
            ddict = self.mpl_dict
        for i in range(0, 99):
            if 'New.{}'.format not in ddict:
                ddict['New.{}'.format(i)] = 'None'
                break
            else:
                print(ddict['New.{}'.format(i)])
                pass
        self.mplTree.updateTree()

    def delFromDict(self):
        print("DELETING")
        keys = self.mplTree.returnHighlightedDictionary()
        if keys is not None:
            ddict = self.mplTree.getParentDict(self.mpl_dict, keys[:-1])
        else:
            ddict = self.mpl_dict
        print(ddict[keys[-1]], keys[-1])
        print(self.mpl_dict)
        del ddict[keys[-1]]
        if keys[-1] in ddict:
            print("STILL HERE")
        test = self.mplTree.tree.selectedItems()[0]
        try:
            self.mplTree.tree.takeTopLevelItem(int(self.mplTree.tree.indexFromItem(test).row()))
        except:
            test.parent().removeChild(test)
        self.mplTree.updateTree()

    def save_figure(self):
        self.fig.savefig("test.pdf")
        save_dict = remove_trees(self.mpl_dict)
        with open('test.yml', 'w') as outfile:
            yaml.dump(save_dict, outfile, default_flow_style=False)


    def load_yaml(self):
        test = yaml.load(open('test.yml', 'r'))
        if test != None:
            self.mpl_dict = copy.deepcopy(test)
            self.mpl_dict['Update'] = True
            self.mplTree.tree.clear()
            self.dataTree.tree.clear()
            self.mplTree.data = self.mpl_dict
            self.dataTree.parent.mpl_dict = self.mpl_dict
            self.dc.parent.mpl_dict = self.mpl_dict
            self.refreshWidgets(new=True)
            #self.update_figure()

    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
        key_press_handler(event, self.dc, self.toolbar)

    def notify(self, text):
        self.text.showText(str(text))

    def refreshWidgets(self, new=False):
        self.mplTree.parent.mpl_dict = self.mpl_dict
        self.dataTree.parent.mpl_dict = self.mpl_dict
        self.dc.parent.mpl_dict = self.mpl_dict
        # Danger; recursion.
        '''if new:
            self.mplTree.tree.clear()
            self.dataTree.tree.clear()'''
        self.mplTree.updateTree(new)
        # Well, it no longer seems to die, but.
        # If we want to update this, we're going to have to call a clear function.
        #self.dataTree.updateTree(new)
        self.dc.update_figure()
        #pass

    def updateFromDict(self, defaults=True, firstrun=False, updatedKeys=None):
        d = self.mpl_dict
        for rows in range(0, int(self.mpl_dict['Rows'])):
            for cols in range(0, int(self.mpl_dict['Columns'])):
                if not defaults:
                    # If we haven't changed the defaults, don't upstate the state.
                    if str((rows, cols)) not in self.mpl_dict['Figures']:
                        new_dict = {}
                        for key, val in self.mpl_dict['FigDefaults'].items():
                            new_dict[key] = val
                        self.mpl_dict['Figures'][str((rows,cols))] = copy.deepcopy(new_dict)
                    for dset in range(0, int(self.mpl_dict['Datasets'])):
                        if str(dset) not in self.mpl_dict['Figures'][str((rows,cols))]['data']:
                            new_dict = {}
                            for key, val in self.mpl_dict['DSetDefaults'].items():
                                new_dict[key] = val
                            self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = copy.deepcopy(new_dict)
                # Here, we're updating the defaults.
                else:
                    # Here, we're updating from the defaults.
                    new_dict = {}
                    for key, val in self.mpl_dict['FigDefaults'].items():
                        if updatedKeys == None:
                            new_dict[key] = copy.deepcopy(val)
                        else:
                            for uKey in updatedKeys:
                                if key == uKey:
                                    new_dict[key] = copy.deepcopy(val)
                                else:
                                    new_dict[key] = copy.deepcopy(self.mpl_dict['Figures'][str((rows,cols))][key])
                    self.mpl_dict['Figures'][str((rows,cols))] = new_dict
                    self.mpl_dict['Figures'][str((rows,cols))]['Update'] = True
                    for dset in range(0, int(self.mpl_dict['Datasets'])):
                        new_dict = {}
                        for key, val in self.mpl_dict['DSetDefaults'].items():
                            if updatedKeys == None:
                                new_dict[key] = copy.deepcopy(val)
                            else:
                                for uKey in updatedKeys:
                                    if key == uKey:
                                        new_dict[key] = copy.deepcopy(val)
                                    else:
                                        new_dict[key] = copy.deepcopy(self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)][key])
                        # We don't really want to create new keys, so.
                        tree_dict = {}
                        self.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)] = copy.deepcopy(new_dict)

                # Throw in the axes object.
        #self.dc.update_figure(defaults)
        if not firstrun:
            self.refreshWidgets(new=defaults)

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
        pass

    # Data loading; for now, just do hdf5

    # For displaying data in a tree.
    class newTree():
        def __init__(self, parent, data, pos, col=1, rows=True, size=None, editable=True, clickable=False, function=None, get_figures=None, mpl=None, function2=None):
            self.tree = QTreeWidget(parent)
            self.tree.setColumnCount(col+1)
            self.tree.setSortingEnabled(True)
            self.tree.sortByColumn(0, 0)
            self.parent = parent
            self.get_figures = get_figures
            self.col = col+1
            self.pos = pos
            self.size = size
            self.tree.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
                #QSizePolicy.Expanding,
            #A = QTreeWidgetItem(self.tree, ["A"])
            self.data = data
            self.data['keyTree'] = {}
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
            self.menu.popup(QCursor.pos())

        def reassignMpl(self, location):
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
            #self.parent.mpl_dict['Figures'][str(key)]['data'][str(dkey)]['loc'] = location
            #self.parent.mpl_dict['Figures'][str(key)]['data'][str(dkey)]['valTree.loc'].setText(0, str(location))
            key = self.parent.mpl_dict['Active']
            self.parent.mpl_dict['Figures'][str(key)]['data']['0']['loc'] = location
            self.parent.mpl_dict['Figures'][str(key)]['Update'] = True
            self.parent.mpl_dict['keyTree']['Figures'][str(key)]['data']['0']['keyTree.loc'].setText(1, str(location))
            #self.parent.mpl_dict = copy.deepcopy(d)

            #tmp = self.parent.mpl_dict.get(['Figures'][key]['data'])
            #tmp[dkey]['loc'] = location
            self.parent.refreshWidgets()
            #self.function2()

        def updateData(data):
            self.data = data
            self.updateTree()

        def updateTree(self, new=False):
            # Python 3 just uses items, not iteritems.
            try:
                self.tree.itemChanged.disconnect()
            except:
                pass
            if type(self.data) == dict:
                if new:
                    self.tree.clear()
                self.handleDict(self.data, self.tree, tree_dict=self.data['keyTree'], new=new)
            self.tree.itemChanged.connect(self.onItemChanged)

        def getFigures(self):
            return self.figures

        def handleDict(self, dict_data, tree, key_list=[], tree_dict={},new=False):
            # We can actually have numerous structures, here.
            # Why not keep track of it, for now?
            # We want to do a reverse lookup
            ddc = copy.copy(dict_data)
            con = False
            for key, val in sorted(ddc.items(), key= lambda x: str(x)):
                if type(key) == str and len(key) >= 6:
                    if key[0:7] != 'keyTree' and key[0:7] != 'valTree':
                        con = True
                    else:
                        con = False
                else:
                    con = True
                if con:
                    if 'keyTree.{}'.format(key) not in tree_dict or new:
                        keyTree = QTreeWidgetItem(tree, [str(key)])
                        keyTree.oldValue = [str(key)]
                        tree_dict['keyTree.{}'.format(key)] = keyTree
                        self.treeItemKeyDict[str(keyTree)] = key_list + [str(key)]
                    else:
                        keyTree = tree_dict['keyTree.{}'.format(key)]
                        keyTree.setText(0, str(key))
                    if key == 'Figures':
                        self.figures = keyTree
                    if type(val) == dict:
                        if key not in tree_dict:
                            tree_dict[key] = {}
                        #self.handleDict(val, keyTree, key_list + [str(key)], new=new, tree_dict=tree_dict[key])
                        self.handleDict(val, keyTree, key_list + [str(key)], new=new, tree_dict=tree_dict[key])
                    elif type(val) == h5py._hl.dataset.Dataset:
                        # Let's handle 2 and 3 dimensional data for now.  Anything more than that and it just... well, it won't plot anyway.
                        # I know this shouldn't go into the handlDict function, but hey.  At least rename it.
                        sdict = {}
                        if len(val.shape) == 2:
                            # Assume time is the first dimension.
                            for i in range(0, val.shape[1]):
                                if val.dtype.names is not None:
                                    sdict[i] = {}
                                    for iv, v in enumerate(val.dtype.names):
                                        # Why the fuck is this so slow?
                                        sdict[i][v] = str(val.shape)
                                else:
                                    sdict[i] = str(val.shape)
                        if len(val.shape) == 3:
                            # Assume time is the first dimension.
                            for i in range(0, val.shape[1]):
                                for j in range(0, val.shape[2]):
                                    if val.dtype.names is not None:
                                        sdict[(i,j)] = {}
                                        for iv, v in enumerate(val.dtype.names):
                                            # Why the fuck is this so slow?
                                            sdict[(i,j)][v] = str(val.shape)
                                    else:
                                        sdict[(i,j)] = str(val.shape)
                                        #self.handleDict({ val.name : str(val.shape) }, keyTree, key_list + [str(key)], new=new)
                        if key not in tree_dict:
                            tree_dict[key] = {}
                        self.handleDict(sdict, keyTree, key_list + [str(key)], new=new, tree_dict=tree_dict[key])
                    else:
                        # We want this to be like rows, not columns
                        if self.rows:
                            if type(val) == list:
                                for iv, v in enumerate(val):
                                    if self.editable:
                                        keyTree.setFlags(keyTree.flags() | QtCore.Qt.ItemIsEditable)
                                    keyTree.setText(iv+1, str(v))
                                    keyTree.oldValue.append((str(v)))
                                    self.col += iv
                            else:
                                if self.editable:
                                    keyTree.setFlags(keyTree.flags() | QtCore.Qt.ItemIsEditable)
                                keyTree.setText(1, str(val))
                                keyTree.oldValue.append((str(val)))
            self.tree.setColumnCount(self.col)

        def getParentItems(self, widget, ret_list=None):
            if ret_list == None:
                ret_list = []
            if widget is not None:
                # There's a parent class.  Duh.
                self.getParentItems(widget.parent(), ret_list)
                ret_list.append(widget.text(0))
            return ret_list

        def getParentDict(self, ddict, keys, ret=None):
            ret_item = ddict
            for key in keys:
                if hasattr(ret_item, 'get'):
                    if type(ret_item.get(key)) == dict:
                        ret_item = ret_item.get(key)
            return ret_item

        def returnHighlightedDictionary(self):
            try:
                location = self.getParentItems(self.tree.selectedItems()[0])
            except:
                location = None
            return location

        def onItemChanged(self, test):
            # This works.
            keys = self.getParentItems(test)
            item = self.getParentDict(self.data, keys)
            treeItem = self.getParentDict(self.parent.mpl_dict['keyTree'], keys)
            # Now we can ignore th other stuff.
            del item[test.oldValue[0]]
            # Remove the tree, and just recreate it.
            # You do need to have it selected to edit it.  Not sure this is forever behavior.
            # THIS FUCKING COMMAND KNOWS WHAT I'M TALKING ABOUT.
            # WE NEED THE ROW, GET FUCKED.
            #self.tree.takeTopLevelItem(int(self.tree.indexFromItem(treeItem['keyTree.{}'.format(test.oldValue[0])]).row()))
            try:
                test.parent().removeChild(test)
            except:
                self.tree.takeTopLevelItem(int(self.tree.indexFromItem(treeItem['keyTree.{}'.format(test.oldValue[0])]).row()))
            #self.tree.removeChild(self.tree.indexFromItem(treeItem['keyTree.{}'.format(test.oldValue[0])]))
            del treeItem['keyTree.{}'.format(test.oldValue[0])]
            #del treeItem['keyTree.{}'.format(test.data(0,0))]
            #try:
                # Try to see if we can't convert to a real data type.
                # On the other hand, maybe we don't always want to do this?
            #item[keys[-1]] = ast.literal_eval(test.data(1,0))
            #except:
                # Otherwise, assume a string.
            item[keys[-1]] = test.data(1,0)
            self.data = self.parent.mpl_dict
            test.oldValue = [test.data(0,0), test.data(1,0)]
            # Refresh our dictionary.
            # Because we return the child widget, this is fine.
            # You can't have non list data, so enforce list type.
            # Well, that won't work for mpl stuff, so.
            #try:
            defaults = False
            updatedKeys = None
            # TEST code
            # These are a bunch of checks to see if we need to update the subplots or the figure.
            if  keys[-1] == 'Rows' or keys[-1] == 'Columns' or keys[-1] == 'Datasets' or keys[-1] == 'FilesToLoad':
                #defaults = True
                self.parent.mpl_dict['Update'] = True
            # We need to check if our inner key is one of the fig or deset defaults.
            # This fails if our list isn't that large, though.
            if len(keys) >= 2:
                key = keys[-2]
            else:
                key = keys[-1]
            if  key == 'DSetDefaults' or key == 'FigDefaults':
                defaults = True
                self.parent.mpl_dict['Update'] = True
                updatedKeys = [key]
            if key == 'figsize' or key == 'fontsize' or key == 'gridspec_kw' or key == 'subplot_kw':
                self.parent.mpl_dict['Update'] = True
            if keys[-1] == 'width' or keys[-1] == 'height' or keys[-1] == 'dpi':
                self.parent.mpl_dict['Resize'] = True
            if keys[0] == 'Figures':
                # We do need to trigger a total redraw.
                self.parent.mpl_dict['Update'] = True
                self.parent.mpl_dict['Figures'][str(keys[1])]['Update'] = True
            if self.function:
                self.function(defaults=defaults, updatedKeys=updatedKeys)
            self.updateTree(defaults)

        def onClicked(self, test):
            # This is the thing which will actually return our dataset.
            #location = self.treeItemKeyDict[str(self.tree.selectedItems()[0])]
            location = self.getParentItems(self.tree.selectedItems()[0])
            # One thing we don't know is precisely how to format this, but that's okay.
            # We could just change this later.
            # We should probably store how we formatted it with the reverse dictionary, but.
            if self.function:
                self.function(str(location))

    class newTextBox():
        def __init__(self, parent, size, pos, init_text=""):
            self.textBox = QLineEdit(parent)
            #self.textBox = QTextEdit(parent)
            self.textBox.setText(init_text)
            if size and pos:
                self.textBox.setGeometry(pos[0], pos[1], size[0], size[1])

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


