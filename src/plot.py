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

#handle = plotfunc(ax, self.translate_location(loc), irange, orange, **sk)
def shade(ax, data, irange, index, sk):
    if index != 'BF':
        handle, = ax.plot(data['expected'][:], **sk)
    # I used timepoint in the dataframe.
    #print(data['timepoint'])
    #handle, = ax.plot(data['timepoint'], data['expected'][:], **sk)
    sk['alpha'] = .3
    #ax.fill_between(data['timepoint'], data['ci_ubound'][:], data['ci_lbound'][:], **sk)
    # But what I really need is just a black range for BF.
    if index != 'BF':
        ax.fill_between(range(0, data['expected'][:].shape[0]), data['ci_ubound'][:], data['ci_lbound'][:], **sk)
    else:
        point = data['expected'].shape[0]-1
        handle = ax.axhspan(data['ci_ubound'][point], data['ci_lbound'][point], **sk)
    return handle

def bar_bf(ax, data, irange, index, sk):
    print(data['efficiency_BF'])
    point = data['efficiency_BF'].shape[0]-1
    if int(index) == 1:
        ax.axhline(y=1, color='black', alpha=1, lw=.4, zorder=0)
    #sk['log'] = True
    handle, = ax.bar(int(index), data['efficiency_BF'][:][point], **sk)
    # I used timepoint in the dataframe.
    #print(data['timepoint'])
    #handle, = ax.plot(data['timepoint'], data['expected'][:], **sk)
    #sk['alpha'] = .3
    #ax.fill_between(data['timepoint'], data['ci_ubound'][:], data['ci_lbound'][:], **sk)
    return handle

def bar_ss(ax, data, irange, index, sk):
    print(data['efficiency_EQ vs. SS'])
    point = data['efficiency_EQ vs. SS'].shape[0]-1
    if int(index) == 1:
        ax.axhline(y=1, color='black', alpha=1, lw=.4, zorder=0)
    #sk['log'] = True
    handle, = ax.bar(int(index), data['efficiency_EQ vs. SS'][:][point], **sk)
    # I used timepoint in the dataframe.
    #print(data['timepoint'])
    #handle, = ax.plot(data['timepoint'], data['expected'][:], **sk)
    #sk['alpha'] = .3
    #ax.fill_between(data['timepoint'], data['ci_ubound'][:], data['ci_lbound'][:], **sk)
    return handle

def bar_color(ax, data, irange, index, sk):
    print(data['efficiency_Color vs. Non Color'])
    point = data['efficiency_Color vs. Non Color'].shape[0]-1
    if int(index) == 1:
        ax.axhline(y=1, color='black', alpha=1, lw=.4, zorder=0)
    #sk['log'] = True
    handle, = ax.bar(int(index), data['efficiency_Color vs. Non Color'][:][point], **sk)
    # I used timepoint in the dataframe.
    #print(data['timepoint'])
    #handle, = ax.plot(data['timepoint'], data['expected'][:], **sk)
    #sk['alpha'] = .3
    #ax.fill_between(data['timepoint'], data['ci_ubound'][:], data['ci_lbound'][:], **sk)
    return handle
