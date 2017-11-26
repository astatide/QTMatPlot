#! /usr/bin/python3

# Stuff to get the window open.
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QTreeWidget, QTreeWidgetItem, QGraphicsAnchorLayout, QScrollArea, QLineEdit, QMenu, QAction, QDockWidget, QMainWindow, QHBoxLayout, QTextEdit, QComboBox
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
import numba as nb

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
        self.data = data
        self.data['keyTree'] = {}
        if size:
            self.tree.setGeometry(pos[0], pos[1], size[0], size[1])
        if mpl:
            self.mpl = mpl
        self.function = function
        self.function2 = function2
        self.editable = editable
        # Deprecated
        self.rows = rows
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
        location = self.getParentItems(self.tree.selectedItems()[0])
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

    def reassignMplFromHighlightedData(self):
        #print(self.tree.selectedItems())
        location = self.getParentItems(self.tree.selectedItems()[0])
        self.reassignMpl(location)

    def reassignMpl(self, location):
        # This function reassigns a plot to be the dataset in location.
        key = self.parent.mpl_dict['Active']
        if key is not None:
            dset = str(self.parent.mpl_dict['ActiveDSet'])
            self.parent.mpl_dict['Figures'][str(key)]['data'][dset]['loc'] = str(location)
            self.parent.mpl_dict['Figures'][str(key)]['Update'] = True
            self.parent.mpl_dict['keyTree']['Figures'][str(key)]['data'][dset]['keyTree.loc'].setText(1, str(location))
            self.parent.refreshWidgets()

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
                # Blow the tree away.
                self.tree.clear()
                # Also, delete the keys in the tree.
                #self.parent.mpl_dict['keyTree'] = {}
            self.handleDict(self.data, self.tree, tree_dict=self.data['keyTree'], new=new)
        self.tree.itemChanged.connect(self.onItemChanged)

    def getFigures(self):
        return self.figures

    def handleDict(self, dict_data, tree, tree_dict={},new=False):
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
                try:
                    keyTree = tree_dict['keyTree.{}'.format(key)]
                    keyTree.setText(0, str(key))
                except Exception:
                    keyTree = QTreeWidgetItem(tree, [str(key)])
                    keyTree.oldValue = [str(key)]
                    tree_dict['keyTree.{}'.format(key)] = keyTree
                '''if 'keyTree.{}'.format(key) not in tree_dict or new:
                    keyTree = QTreeWidgetItem(tree, [str(key)])
                    keyTree.oldValue = [str(key)]
                    tree_dict['keyTree.{}'.format(key)] = keyTree
                else:
                    keyTree = tree_dict['keyTree.{}'.format(key)]
                    keyTree.setText(0, str(key))'''
                if key == 'Figures':
                    self.figures = keyTree
                if type(val) == h5py._hl.group.Group:
                        #tree_dict[key] =
                        # This is a normal HDF5 group.  Treat it appropriately.
                    if key not in tree_dict:
                        tree_dict[key] = {}
                    self.handleDict(val, keyTree, new=new, tree_dict=tree_dict[key])
                if type(val) == dict:
                    if key not in tree_dict:
                        tree_dict[key] = {}
                    self.handleDict(val, keyTree, new=new, tree_dict=tree_dict[key])
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
                    if key not in tree_dict:
                        tree_dict[key] = {}
                    self.handleDict(sdict, keyTree, new=new, tree_dict=tree_dict[key])
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
        # This function recurses through the parent widgets, getting the text in
        # column 1, and appending it to a list.  It's specific for this
        # implementation in that we're storing keys as the 1st column text;
        # ergo, this returns the set of keys to go through either the item or
        # tree dictionary (here, keyTree)
        if ret_list == None:
            ret_list = []
        if widget is not None:
            # There's a parent class.  Duh.
            self.getParentItems(widget.parent(), ret_list)
            ret_list.append(widget.text(0))
        return ret_list

    def getParentDict(self, ddict, keys, ret=None):
        # This function returns the pointer of the actual data item at the last
        # key point.  Useful for avoiding pointer problems with dictionaries.
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

    def changeItem(self, item):
        # This deletes both the key and the item in the original dictionary.
        # Then, it recreates it.
        keys = self.getParentItems(item)
        dictItem = self.getParentDict(self.data, keys)
        treeItem = self.getParentDict(self.parent.mpl_dict['keyTree'], keys)

        # Now, we delete both the item, and the key.
        # oldValue is something I've appended to the QTreeWidgetItem to keep
        # track of things in the dictionary.  We lose that after we change things.
        del dictItem[item.oldValue[0]]

        # Now we try deleting the widget.  We rely on our main function to recreate
        # QTreeWidgetItems as necessary; it's only necessary that we remove it.
        try:
            item.parent().removeChild(item)
        except:
            self.tree.takeTopLevelItem(int(self.tree.indexFromItem(treeItem['keyTree.{}'.format(item.oldValue[0])]).row()))
        # Now, remove the widget from the keyTree; this way, it'll be recreated.
        try:
            del treeItem['keyTree.{}'.format(item.oldValue[0])]
        except:
            pass
        # Now, we add the new key: pair value into the original dictionary.
        # Once we call the update function, it'll regenerate the QTreeWidgetItem
        # This doesn't seem to work for things in the top level?
        #if len(keys) > 1:
        dictItem[item.data(0,0)] = item.data(1,0)
        #else:
        #    self.parent.mpl_dict[item.data(0,0)] = item.data(1,0)
        print(item.data(0,0), item.data(1,0), dictItem[item.data(0,0)])
        item.oldValue = [item.data(0,0), item.data(1,0)]
        #self.removeItem(item)
        #self.addItem(item)

    def removeItem(self, item):
        # This deletes both the key and the item in the original dictionary.
        keys = self.getParentItems(item)
        dictItem = self.getParentDict(self.data, keys)
        treeItem = self.getParentDict(self.parent.mpl_dict['keyTree'], keys)

        # Now, we delete both the item, and the key.
        # oldValue is something I've appended to the QTreeWidgetItem to keep
        # track of things in the dictionary.  We lose that after we change things.
        del dictItem[item.oldValue[0]]

        # Now we try deleting the widget.  We rely on our main function to recreate
        # QTreeWidgetItems as necessary; it's only necessary that we remove it.
        try:
            item.parent().removeChild(item)
        except:
            self.tree.takeTopLevelItem(int(self.tree.indexFromItem(treeItem['keyTree.{}'.format(item.oldValue[0])]).row()))
        # Now, remove the widget from the keyTree; this way, it'll be recreated.
        try:
            del treeItem['keyTree.{}'.format(item.oldValue[0])]
        except:
            pass

    def addItem(self, item, ddict = None):
        # This deletes both the key and the item in the original dictionary.
        # Then, it recreates it.
        keys = self.getParentItems(item)
        dictItem = self.getParentDict(self.data, keys)
        treeItem = self.getParentDict(self.parent.mpl_dict['keyTree'], keys)

        # Now, we add the new key: pair value into the original dictionary.
        # Once we call the update function, it'll regenerate the QTreeWidgetItem
        print(ddict, keys)
        if ddict is None:
            dictItem[item.data(0,0)] = item.data(1,0)
            print(item.data(0,0), item.data(1,0), dictItem[item.data(0,0)])
            item.oldValue = [item.data(0,0), item.data(1,0)]
        else:
            dictItem[ddict[0]] = ddict[1]

    def onItemChanged(self, test):
        # This works.
        keys = self.getParentItems(test)
        self.changeItem(test)
        new = False
        redraw = False
        updatedKeys = None
        # TEST code
        # These are a bunch of checks to see if we need to update the subplots or the figure.
        '''if  keys[-1] == 'Rows' or keys[-1] == 'Columns' or keys[-1] == 'Datasets' or keys[-1] == 'FilesToLoad':
            # trigger a redraw of everything, including the widget.
            new = True
            self.parent.mpl_dict['Update'] = True
        # We need to check if our inner key is one of the fig or deset defaults.
        # This fails if our list isn't that large, though.
        if len(keys) >= 2:
            key = keys[-2]
        else:
            key = keys[-1]
        # We'll just trigger a redraw for these.
        if  key == 'DSetDefaults' or key == 'FigDefaults':
            #defaults = True
            redraw = True
            #self.parent.mpl_dict['Update'] = True
            #updatedKeys = [key]
        if key == 'figsize' or key == 'fontsize' or key == 'gridspec_kw' or key == 'subplot_kw' or 'GridRatio':
            # Trigger a redraw and a full figure update.
            self.parent.mpl_dict['Update'] = True
            new = True
        if keys[-1] == 'width' or keys[-1] == 'height' or keys[-1] == 'dpi':
            # Just triggering a resize.
            self.parent.mpl_dict['Resize'] = True
        if keys[0] == 'Figures':
            # We do need to trigger a total redraw.
            self.parent.mpl_dict['Update'] = True
            self.parent.mpl_dict['Figures'][str(keys[1])]['Update'] = True'''
        new = True
        self.parent.mpl_dict['Update'] = True
        if keys[0] == 'Datasets':
            print(self.parent.mpl_dict)
        if keys[0] == 'Figures':
            # We do need to trigger a total redraw.
            print("YES!")
            print(str(keys[1]))
            self.parent.mpl_dict['Figures'][str(keys[1])]['Update'] = True
        #self.updateTree()
        # This function definitly needs updating.
        if self.function:
            self.function()

    def onClicked(self, test):
        # This is the thing which will actually return our dataset.
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
        self.button = QPushButton(label, parent)
        self.button.move(pos[0], pos[1])
        self.click_args = click_args
        self.function = function
        self.button.clicked.connect(self.function)

class newComboBox():
    def __init__(self, parent, items, function):
        self.parent = parent
        self.comboBox = QComboBox()
        self.items = items
        new_items = []
        for item in items:
            new_items.append(str(item))
        self.comboBox.addItems(new_items)
        self.function = function
        self.comboBox.currentIndexChanged.connect(self.changeActiveDSet)

    def reInit(self, items):
        self.comboBox.clear()
        new_items = []
        for item in items:
            new_items.append(str(item))
        self.comboBox.addItems(new_items)

    def changeActiveDSet(self):
        self.parent.mpl_dict['ActiveDSet'] = self.comboBox.currentText()

    # For our buttons.
    @pyqtSlot()
    def button_test(self):
        print("We're clicking a button, wheee")
