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

class dataLoader():
    def __init__(self, fileList):
        pass

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


