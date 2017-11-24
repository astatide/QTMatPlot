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
