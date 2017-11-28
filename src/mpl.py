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
from matplotlib import rcParams
#sns.set_style('ticks')
#sns.set_context('paper')
sns.set_palette('deep')
import traceback

import yaml

# and here http://www.boxcontrol.net/embedding-matplotlib-plot-on-pyqt5-gui.html

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import key_press_handler

#from matplotlib import rc
#rc('font',**{'family':'sans-serif','sans-serif':['Coolvetica']})
#rc('text', usetex=True)


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
class mplCanvas(FigureCanvas):
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
        # Accept drag/drop events  Although this doesn't seem to work.
        self.setAcceptDrops(True)
        # Can't remembr what this is for; qt, most likely.
        self.hoverAxes = None
        self.activeAxes = (0,0)
        self.setParent(parent)

        # Set the size policy such that we can't be squished, but will
        # instead simply grow and shrink with the dpi.
        # We call updateGeometry upon changing the dpi to ensure grow to our new window size.
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Fixed,
                QSizePolicy.Fixed)
        FigureCanvas.updateGeometry(self)

        # Initial update call.
        self.parent.mpl_dict['Update'] = True
        self.parent.mpl_dict['Resize'] = True
        #self.updateFromDict()
        self.update_figure()
        #self.parent.mpl_dict['Update'] = True
        #self.parent.mpl_dict['Resize'] = True
        # Some code for when we would like to do a movie later, maybe.
        ##timer = QtCore.QTimer(self)
        ##timer.timeout.connect(self.update_figure)
        ##timer.start(1000)

    def plot(self, pd, index, ax):
        # pd is the plot dictionary
        ax.tick_params(axis='both', labelsize=float(self.parent.mpl_dict['FontsTicks']['tickfontsize']), length=int(self.parent.mpl_dict['FontsTicks']['ticksize']))
        # Here's where we're going to handle dictionary inheritance.
        sk = dict(self.parent.mpl_dict['DSetDefaults'])
        fk = dict(self.parent.mpl_dict['FigDefaults'])
        for k, v in pd['data'][str(index)].items():
            if v is not None and v != "None":
                if k != 'color':
                    sk[k] = copy.copy(v)
                elif str(v) != "-1":
                    # Ignore the default color.
                    sk[k] = copy.copy(v)
        for k, v in pd.items():
            if k != "data":
                if v is not None and v != "None" and v != '':
                    fk[k] = copy.copy(v)
                #else:
                #    fk[k] = copy.copy(v)
        if fk['ylabel'] is not None:
            ax.set_ylabel(fk['ylabel'], fontsize=float(self.parent.mpl_dict['FontsTicks']['titlesize']), fontweight='bold', fontname=self.parent.mpl_dict['FontsTicks']['fontname'])
        if fk['xlabel'] is not None:
            ax.set_xlabel(fk['xlabel'], fontsize=float(self.parent.mpl_dict['FontsTicks']['titlesize']), fontweight='bold', fontname=self.parent.mpl_dict['FontsTicks']['fontname'])
        #if fk['title'] != '':
        ax.set_title(fk['title'], fontsize=float(self.parent.mpl_dict['FontsTicks']['titlesize']), fontweight='bold', fontname=self.parent.mpl_dict['FontsTicks']['fontname'])
        if sk['loc'] != 'None':
            loc = copy.deepcopy(sk['loc'])
            irange = copy.deepcopy(sk['range'])
            orange = None
            plotfuncstr = fk['type'].split('.')
            module = __import__(plotfuncstr[0])
            plotfunc = getattr(module, plotfuncstr[1])
            if sk['color'] == -1:
                sk['color'] = str(self.parent.mpl_dict['Colors'][index])
            elif str(sk['color'])[0] == "#":
                pass
            else:
                sk['color'] = str(self.parent.mpl_dict['Colors'][int(sk['color'])])
            del sk['loc']
            del sk['range']
            try:
                handle = plotfunc(ax, self.translate_location(loc), irange, orange, sk)
                return handle
            except Exception as e:
                tb = traceback.format_exc()
                if self.notify_func is not None:
                    self.notify_func(tb)
                    return None
                else:
                    return None

    def updateFromDict(self):
        d = self.parent.mpl_dict
        # Clears the figure before we plot more.
        if self.parent.mpl_dict['Update'] == True:
            # This means that we're updating from the defaults.
            self.fig.clear()
            #self.axes = self.fig.subplots(nrows=int(d['Rows']), ncols=int(d['Columns']))
            gridspec_kw = self.parent.mpl_dict['gridspec_kw']
            subplot_kw = self.parent.mpl_dict['subplot_kw']
            for k, v in gridspec_kw.items():
                try:
                    gridspec_kw[str(k)] = float(v)
                except:
                    pass
            for k, v in subplot_kw.items():
                try:
                    subplot_kw[str(k)] = ast.literal_eval(str(v))
                except:
                    pass
            if "PlotSize" in self.parent.mpl_dict:
                #print((self.parent.mpl_dict['GridRatio'][0]), (d['Columns']), (d['FigureSize']['width']))
                gridH = (float(ast.literal_eval(self.parent.mpl_dict['PlotSize'])[0]) * float(d['Columns']) / float(d['FigureSize']['width'])) / 2
                gridW = (float(ast.literal_eval(self.parent.mpl_dict['PlotSize'])[1]) * float(d['Rows']) / float(d['FigureSize']['height'])) / 2
                #if "Title" in self.parent.mpl_dict:
                th = (float(d['FigureSize']['height']) - float(d['Title']['height'])) / float(d['FigureSize']['height'])
                #else:
                #    th = .9
                gridspec_kw['top'] = th
                gridspec_kw['bottom'] = th - (2*gridW)
                gridspec_kw['left'] = 0.5 - gridH
                gridspec_kw['right'] = 0.5 + gridH
                self.parent.mpl_dict['gridspec_kw'] = gridspec_kw
                #for k in ['left', 'right']
            self.axes = self.fig.subplots(nrows=int(d['Rows']), ncols=int(d['Columns']), gridspec_kw=gridspec_kw, **subplot_kw)
            self.al = {}
            for rows in range(0, int(self.parent.mpl_dict['Rows'])):
                for cols in range(0, int(self.parent.mpl_dict['Columns'])):
                    # We need to update everything.
                    # So trigger a redraw.
                    self.parent.mpl_dict['Figures'][str((rows,cols))]['Update'] = True
                    self.axes[rows,cols]
            self.fig.set_dpi(int(d['dpi']))
            self.fig.set_size_inches(float(d['FigureSize']['width']), float(d['FigureSize']['height']))
            FigureCanvas.updateGeometry(self)
            self.parent.mpl_dict['Update'] = False
        if self.parent.mpl_dict['Resize'] == True:
            self.parent.mpl_dict['Resize'] = False
            self.fig.set_dpi(int(d['dpi']))
            self.fig.set_size_inches(float(d['FigureSize']['width']), float(d['FigureSize']['height']))
            FigureCanvas.updateGeometry(self)
        # We check to see if we need to update the figures.
        # This should just occur on a rebuild, so if we haven't added anything, don't worry about it.
        active = False
        plotted = False
        self.fig.suptitle(self.parent.mpl_dict['Title']['label'], fontsize=self.parent.mpl_dict['FontsTicks']['titlesize'], fontname=self.parent.mpl_dict['FontsTicks']['fontname'])
        self.handles = []
        self.labels = []
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
                        if dset == 0:
                            # Only clear this during the first new drawing pass
                            self.axes[rows,cols].clear()
                        self.handles.append(self.plot(self.parent.mpl_dict['Figures'][str((rows,cols))], dset, self.axes[rows,cols]))
                        #handle, label = self.axes[rows,cols].get_legend_handles_labels()
                        #self.handles.append(handle)
                        if self.parent.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)]['label'] != "None":
                            self.labels.append(self.parent.mpl_dict['Figures'][str((rows,cols))]['data'][str(dset)]['label'])
                        #self.labels.append(self.parent.mpl_dict['Figures'][str((rows,cols))]['Label'])
                        plotted = True
                self.parent.mpl_dict['Figures'][str((rows,cols))]['Update'] = False
        # Update which dset is active.
        if self.parent.mpl_dict['Active'] is not None:
            self.setOpenDSet(self.parent.mpl_dict['Active'])
        self.plotLegend()
            #if plotted:
            #    self.fig.tight_layout()

    def plotLegend(self):
        new_handles = []
        for handle in self.handles:
            if handle is not None:
                new_handles.append(handle)
        try:
            #handles, legends = self.fig.get_legend_handles_labels
            # Because I like it.
            #self.fig.legend(new_handles, self.labels, loc="lower center", ncol=len(self.labels))
            if self.parent.mpl_dict['Legend']['ncol'] != 'Auto':
                ncol = int(self.parent.mpl_dict['Legend']['ncol'])
            else:
                ncol = len(self.labels)
            prop={'family': self.parent.mpl_dict['FontsTicks']['fontname'],'weight':'roman'}
            self.fig.legend(new_handles, self.labels, loc=self.parent.mpl_dict['Legend']['loc'], ncol=ncol, fontsize=self.parent.mpl_dict['FontsTicks']['legendsize'], prop=prop)
            #self.fig.legend()
        except Exception as e:
            print(e)

    def mouseMoveEvent(self, event):
        # translate into MPL coordinates
        coord = event.pos()
        x = coord.x()
        y = coord.y()
        h = float(self.parent.mpl_dict['FigureSize']['height'])
        w = float(self.parent.mpl_dict['FigureSize']['width'])
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
            self.setOpenDSet(self.parent.mpl_dict['Active'])
            # We want to change the active dset, too.
            #self.parent.dsetTree.data = self.parent.mpl_dict['Figures'].get(str(self.hoverAxes))
            #if self.parent.mpl_dict['ActiveDSet'] == None:
            # For some reason, doing this screws everything up.  Have to look into that.
            #self.parent.mpl_dict['keyTree.Active'].setText(1, str(self.hoverAxes))
            #self.activeAxes = self.hoverAxes
            #FigureCanvas.mousePressEvent(self, event)
            self.parent.refreshWidgets()
            self.update_figure()

    def dragEnterEvent(self, event):
        print(event)

    def dragMoveEvent(self, event):
        print(event)

    def dropEvent(self, event):
        print(event)

    def setOpenDSet(self, fig):
        if fig != "None":
            self.parent.mpl_dict['ActiveDSet'] = 0
            for dset in range(0, int(self.parent.mpl_dict['Datasets'])):
                if self.parent.mpl_dict['Figures'][str(fig)]['data'][str(dset)]['loc'] == "None":
                    self.parent.mpl_dict['ActiveDSet'] = str(dset)
                    break

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
        #FigureCanvas.updateGeometry(self)
        self.draw()

    def translate_location(self, location):
        loc = self.data
        df = False
        for ii, i in enumerate(ast.literal_eval(location)):
            try:
                if "pandas_type" in loc[i].attrs:
                    # This is a pandas dataset!
                    # We need to treat it a bit differently.
                    #tree_dict[key] = dict_data.get(item)
                    # This should handle it, despite being loaded as an HDF5.
                    try:
                        import pandas as pd
                        import os
                        f = pd.HDFStore(ast.literal_eval(location)[0], mode='r')
                        loc = f[os.path.join('/',*ast.literal_eval(location)[1:ii+1])]
                        df = True
                        f.close()
                        return loc
                    except Exception as e:
                        print(e)
                    # Is it a string?
            except:
                pass
            try:
                if df == True:
                    raise Exception
                else:
                    loc = loc[i]
            except:
                # Definitely a tuple.  Unless it isn't.
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
        try:
            return loc.flatten()
        except:
            return loc


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
