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

fig_dict = '''{
                    'type': 'shade',
                    'Update': True,
                    'ylabel': '',
                    'xlabel': '',
                    'title': '',
                    'height': 'None',
                    'width': 'None',
                    }'''
dset_dict = '''{
                    'loc': 'None',
                    'range': 'None',
                    'color': -1,
                    'alpha': 1,
                    }'''

mpl_dict_lit = '''{
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
mpl_dict = ast.literal_eval(mpl_dict_lit)
mpl_dict['DSetDefaults'] = ast.literal_eval(dset_dict)
mpl_dict['FigDefaults'] = ast.literal_eval(fig_dict)


with open('default.yml', 'w') as outfile:
    yaml.dump(mpl_dict, outfile, default_flow_style=False)
