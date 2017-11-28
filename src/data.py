#! /usr/bin/python3

# Stuff to get the window open.
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QTreeWidget, QTreeWidgetItem, QGraphicsAnchorLayout, QScrollArea, QLineEdit, QMenu, QAction, QDockWidget, QMainWindow, QHBoxLayout, QTextEdit, QFileDialog
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
import os
import _pickle as pickle
import pandas as pd
# and here http://www.boxcontrol.net/embedding-matplotlib-plot-on-pyqt5-gui.html

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import key_press_handler

class dataLoader():
    def __init__(self, parent, fileList):
        # We want this to handle loading and structuring data.
        self.fileList = fileList
        self.dataStructure = {}
        # Parent is our parent widget (the main app)
        self.parent = parent
        pass
    def loadFile(self, filename):
        pass

    def loadAllFiles(self, filename):
        pass

    def loadNewFile(self, filename=None):
        if filename == False or filename == None:
            filename, _ = QFileDialog.getOpenFileName(self.parent, 'Open Data File', os.getcwd())
        if filename != '':
            try:
                newFile = self.loadHDF5(filename)
            except:
                #try:
                newFile = self.loadPickle(filename)
                '''except:
                    try:
                        newFile = self.loadYaml(filename)
                    except:
                        # Okay, so that didn't work.  Fail out.
                        filename = None'''
            if filename is not None:
                self.fileList.append(str(filename))
                self.dataStructure[filename] = newFile
            else:
                pass

    def loadNewYaml(self):
        filename, _ = QFileDialog.getOpenFileName(self.parent, 'Open Yaml File', os.getcwd())
        if filename != '':
            self.parent.load_yaml(filename)
            self.parent.mpl_dict['keyTree'] = {}
            self.parent.mplTree.data = self.parent.mpl_dict
            self.parent.dataTree.parent.mpl_dict = self.parent.mpl_dict
            #self.parent.mpl_dict['FigDefaults']['data'] = {}
            #self.parent.updateFromDict(defaults=False, firstrun=False)
            self.parent.refreshWidgets(new=True)
            #self.parent.mpl_dict = self.parent.dataTree.data
            #self.parent.mplTree.updateTree(True)
            #self.parent.dataTree.updateTree()
            #self.parent.refreshWidgets(new=True)

    def loadHDF5(self, filename):
        try:
            # Pandas dataframe
            # Huh.  This doesn't fail, though.
            #f = pd.HDFStore(filename)
            #return f
            raise Exception
        except:
            # NOT a Pandas Dataframe
            f = h5py.File(filename, 'r')
            return dict(f)

    def loadPickle(self, filename):
        try:
            # Appropriate for Python3 pickles
            f = pickle.load( open(filename, 'rb') )
        except:
            # Is it a python2?
            f = pickle.load( open(filename, 'rb'), encoding='latin1' )
        return f

    def loadYaml(self, filename):
        f = yaml.load( open(filename, 'r') )
        return f


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
