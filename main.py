#! /usr/bin/python3

# Stuff to get the window open.
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QTreeWidget, QTreeWidgetItem, QGraphicsAnchorLayout
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

# Matplotlib stuff
import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure
import h5py

# and here http://www.boxcontrol.net/embedding-matplotlib-plot-on-pyqt5-gui.html

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

# Button Functions
@pyqtSlot()
def button_test():
    print("We're clicking a button, wheee")

# Now, from that other site...
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def compute_initial_figure(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        self.axes.plot(t, s)


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [np.random.randint(0, 10) for i in range(4)]

        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()
        FigureCanvas.updateGeometry(self)

class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 simple window - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # Widgets are movable.
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        #layout = QGraphicsAnchorLayout()
        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.layout.addWidget(sc)
        self.main_widget.move(250,0)
        #button = self.newButton(self, "Button!", "Nothing", (100,70), self.button_test, click_args=None)
        testDict = {'0': ['0', '1'], '1': {'A': ['2'], 'B': ['3', '4']}}
        kinetics = h5py.File('direct.h5', 'r')
        self.dataTree = self.newTree(self, dict(kinetics), pos=(0, 0), size=(250,self.height/2), col=3, clickable=True, editable=False)
        self.mplTree = self.newTree(self, testDict, pos=(0,self.height/2), size=(250,self.height/2), col=1)
        #print(dir(layout))
        #layout.addChildWidget(self.dataTree)
        self.show()

    def resizeEvent(self, event):
        # size().height/width should do it.
        self.resizeAll(event.size().height, event.size().width)
        pass

    def resizeAll(self, height, width):
        self.dataTree.tree.resize(self.dataTree.tree.width(), height()/2)
        self.mplTree.tree.setGeometry(0, height()/2, 250, height()/2)

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
        def __init__(self, parent, data, pos, col=1, rows=True, size=None, editable=True, clickable=False):
            self.tree = QTreeWidget(parent)
            self.tree.setColumnCount(col)
            print(dir(self.tree))
            #A = QTreeWidgetItem(self.tree, ["A"])
            self.data = data
            if size:
                self.tree.setGeometry(pos[0], pos[1], size[0], size[1])
            self.editable = editable
            #self.tree.move(pos[0], pos[1])
            # How should we handle this?  Like dictionaries, let's assume.
            self.rows = rows
            self.treeItemKeyDict = {}
            self.updateTree()
            print(dir(self.tree))
            if editable:
                self.tree.itemChanged.connect(self.onItemChanged)
            if clickable:
                self.tree.clicked.connect(self.onClicked)

        def updateData(data):
            self.data = data
            self.updateTree()

        def updateTree(self):
            # Python 3 just uses items, not iteritems.
            if type(self.data) == dict:
                self.handleDict(self.data, self.tree)

        def handleDict(self, dict_data, tree, key_list=[]):
            # We can actually have numerous structures, here.
            # Why not keep track of it, for now?
            # We want to do a reverse lookup
            for key, val in dict_data.items():
                keyTree = QTreeWidgetItem(tree, [str(key)])
                self.treeItemKeyDict[str(keyTree)] = key_list + [str(key)]
                if type(val) == dict:
                    self.handleDict(val, keyTree, key_list + [str(key)])
                elif type(val) == h5py._hl.dataset.Dataset:
                    if len(val.shape) == 1:
                        # Here, we don't want to display everything in the list.  Just... let it be.
                        valTree = QTreeWidgetItem(keyTree, [str(val)])
                        self.treeItemKeyDict[str(valTree)] = key_list + [str(key)]
                        if hasattr(val, 'dtype'):
                            if len(val.dtype) > 1:
                                print(len(val.dtype))
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
                                                    self.treeItemKeyDict[str(dtypeTree)] = key_list + [str(key)] + [str(val.dtype.names[iv])] + [str(i), str(j)]
                else:
                    # We want this to be like rows, not columns
                    if self.rows:
                        for iv, v in enumerate(val):
                            valTree = QTreeWidgetItem(keyTree, [str(v)])
                            #key_list.append(val)
                            self.treeItemKeyDict[str(valTree)] = key_list + [str(key)] + [iv]
                            if self.editable:
                                valTree.setFlags(valTree.flags() | QtCore.Qt.ItemIsEditable)
                    else:
                        valTree = QTreeWidgetItem(keyTree, val)
                        #key_list.append(val)
                        self.treeItemKeyDict[str(valTree)] = key_list + [str(key)]
                        if self.editable:
                            valTree.setFlags(valTree.flags() | QtCore.Qt.ItemIsEditable)

        def onItemChanged(self, test):
            # This works.
            #print("Changed!")
            #print(self.treeItemKeyDict[str(test)])
            # Find the key in the data.
            #print(dir(test))
            val = self.data
            # Recurse through the dictionary
            for key in self.treeItemKeyDict[str(test)]:
                if type(val) == dict:
                    val = val.get(key)
            print(val)
            # Because we return the child widget, this is fine.
            print(val, key)
            # You can't have non list data, so enforce list type.
            val[key] = test.data(0,0)
            print(test.data(0,0), self.data)
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
            print(location)
            if len(location) == 1:
                print(self.data[location[0]][:])
            elif len(location) == 2:
                try:
                    print(self.data[location[0]][:,int(location[1])])
                except:
                    print(self.data[location[0]][location[1]][:])
            elif len(location) == 3:
                try:
                    print(self.data[location[0]][:,int(location[1]), int(location[2])])
                except:
                    print(self.data[location[0]][location[1]][:,int(location[2])])
            elif len(location) == 4:
                try:
                    print(self.data[location[0]][:,int(location[1]), int(location[2]), int(location[3])])
                except:
                    print(self.data[location[0]][location[1]][:,int(location[2]), int(location[3])])


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


