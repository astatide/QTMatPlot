#! /usr/bin/python3

# Stuff to get the window open.
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy, QPushButton, QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot

# Matplotlib stuff
import matplotlib as mpl
import numpy as np
from matplotlib.figure import Figure

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
        self.main_widget = QWidget(self)
        l = QVBoxLayout(self.main_widget)
        sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(sc)
        button = self.newButton(self, "Button!", "Nothing", (100,70), self.button_test, click_args=None)
        testDict = {'0': ['0', '1'], '1': {'A': '2', 'B': ['3', '4']}}
        self.tree = self.newTree(self, testDict, pos=(100, 75))
        self.show()

    def keyPressEvent(self, e):
        # This is our key press handler.  It's mostly just a stub right now.
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def wheelEvent(self, e):
        # This is what happens when we scroll.
        print(self.tree.data)

    class newTree():
        def __init__(self, parent, data, pos, col=1, rows=True, editable=True):
            self.tree = QTreeWidget(parent)
            self.tree.itemChanged.connect(self.onItemChanged)
            self.tree.setColumnCount(col)
            #A = QTreeWidgetItem(self.tree, ["A"])
            self.data = data
            self.editable = editable
            self.tree.move(pos[0], pos[1])
            # How should we handle this?  Like dictionaries, let's assume.
            self.rows = rows
            self.treeItemKeyDict = {}
            self.updateTree()
            print(self.treeItemKeyDict)

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
                else:
                    # We want this to be like rows, not columns
                    if self.rows:
                        for v in val:
                            valTree = QTreeWidgetItem(keyTree, [str(v)])
                            #key_list.append(val)
                            self.treeItemKeyDict[str(valTree)] = key_list + [str(key)]
                            if self.editable:
                                valTree.setFlags(valTree.flags() | QtCore.Qt.ItemIsEditable)
                    else:
                        valTree = QTreeWidgetItem(keyTree, val)
                        #key_list.append(val)
                        self.treeItemKeyDict[str(valTree)] = key_list + [str(key)]
                        if self.editable:
                            valTree.setFlags(valTree.flags() | QtCore.Qt.ItemIsEditable)

        def onItemChanged(self, test):
            print("Changed!")
            print(self.treeItemKeyDict[str(test)])



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


