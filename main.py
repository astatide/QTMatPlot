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
from src import *

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

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'QTMatPlot - ajoshpratt@gmail.com'
        self.left = 10
        self.top = 10
        self.width = 1280
        self.height = 800
        self.load_yaml()
        print(self.mpl_dict)
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
        self.dc = mplCanvas(self.main_widget, data_parent=self, width=10, height=8, dpi=100, data={'direct.h5': kinetics}, notify_func=self.notify)
        self.save_button = newButton(self, "Save", "Saves the Figure", (250,self.height-30), self.save_figure, click_args=None)
        self.load_button = newButton(self, "Load Yaml", "Loads the Config", (250,self.height-30), self.load_yaml, click_args=None)
        self.text = newTextBox(self, size=(0,0), pos=(self.save_button.button.width()+250, self.height-30), init_text="{}".format(kinetics))
        #self.text.textBox.setGeometry(self.save_button.button.width()+self.load_button.button.width(), self.height-30, self.width-self.save_button.button.width(), 15)
        self.text.textBox.resize(self.width-self.save_button.button.width(), 15)
        self.mplTree = newTree(self, self.mpl_dict, pos=(self.width-250,0), size=(250,self.height-30), col=1, function=self.updateFromDict, rows=True)
        self.dataTree = newTree(self, {'direct.h5': dict(kinetics)}, pos=(0, 0), size=(250,self.height-30), col=3, clickable=True, editable=False, function=self.text.showText, function2=self.updateFromDict, get_figures=self.mplTree.getFigures, mpl=self.mpl_dict)
        # Do up some docks for everything!
        self.setCentralWidget(self.main_widget)

        self.mpldock = QDockWidget("Plotting Dictionary", self)
        self.mpllayout = QVBoxLayout(self.mpldock)
        self.mplwidget = QWidget(self)
        # Create buttons...
        self.addValue = newButton(self, "+", "Adds a new key: value", (0,0), self.addToDict, click_args=None)
        self.delValue = newButton(self, "-", "Deletes key: value pair", (0,0), self.delFromDict, click_args=None)
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
        self.loadData = newButton(self, "Load Data", "Adds a new key: value", (640,0), self.addToDict, click_args=None)
        self.sendData = newButton(self, "Plot", "Plot Active Dataset", (640,0), self.dataTree.reassignMplFromHighlightedData, click_args=None)
        #self.dataButtonlayout = QHBoxLayout(self.datawidget)
        #self.dataButtonwidget = QWidget(self)
        #self.dataButtonwidget.setLayout(self.dataButtonlayout)
        #self.dataButtonlayout.addWidget(self.loadData.button)
        #self.dataButtonlayout.addWidget(self.delValue.button)
        self.datalayout.addWidget(self.dataTree.tree)
        #self.datalayout.addWidget(self.dataButtonwidget)
        self.datalayout.addWidget(self.sendData.button)
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
        self.dc.update_figure()
        self.updateFromDict(True)

    def addToDict(self):
        try:
            for i in range(0,99):
                if 'New: {}'.format(i) not in self.mpl_dict:
                    self.mplTree.addItem(self.mplTree.tree.selectedItems()[0].parent(), ddict=['New: {}'.format(i), None])
                    break
        except:
            for i in range(0,99):
                if 'New: {}'.format(i) not in self.mpl_dict:
                    self.mplTree.addItem(self.mplTree.tree.topLevelItem(0), ddict=['New: {}'.format(i), None])
                    break
        self.mplTree.updateTree()

    def delFromDict(self):

        self.mplTree.removeItem(self.mplTree.tree.selectedItems()[0])


    def save_figure(self):
        self.fig.savefig("test.pdf")
        save_dict = remove_trees(self.mpl_dict)
        with open('test.yml', 'w') as outfile:
            yaml.dump(save_dict, outfile, default_flow_style=False)


    def load_yaml(self, default='src/default.yaml'):
        test = yaml.load(open(default, 'r'))
        print(test)
        #if test != None:
        # We want to push a lot of this to later.
        self.mpl_dict = copy.deepcopy(test)
        self.mpl_dict['Update'] = True
        #self.mplTree.tree.clear()
        #self.dataTree.tree.clear()
        #self.mplTree.data = self.mpl_dict
        #self.dataTree.parent.mpl_dict = self.mpl_dict
        #self.dc.parent.mpl_dict = self.mpl_dict
        #self.refreshWidgets(new=True)

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
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
