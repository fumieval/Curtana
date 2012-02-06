import sys
import PyQt4.QtCore as Q 
import PyQt4.QtGui as G
import random
import threading
import time

from curtana.common import userstream

def main(): 
    app = G.QApplication(sys.argv) 
    w = MyWindow() 
    w.show()
    try:
        client = userstream.Client("fumieval")
    except:
        return
    Listener(client, w).start()
    sys.exit(app.exec_())
    
class Listener(threading.Thread):
    def __init__(self, client, window):
        self.client = client
        self.window = window
        threading.Thread.__init__(self)
        self.daemon = True
    def run(self):
        for data in self.client:
            if "user" in data and "id" in data:
                self.window.model.rotate("hoge")
                self.window.statuslist.reset()
                


class MyWindow(G.QWidget): 
    def __init__(self, *args): 
        G.QWidget.__init__(self, *args) 

        # create table
        
        self.model = TimeLineModel(500, self)
        
        self.statuslist = G.QListView(self)
        self.statuslist.setFlow(G.QListView.TopToBottom)
        self.statuslist.setModel(self.model)
        
        button = G.QPushButton("append", self)
        button.clicked.connect(self.refresh)
        # layout
        layout = G.QVBoxLayout()
        layout.addWidget(self.statuslist) 
        layout.addWidget(button)
        self.setLayout(layout)
    def refresh(self):
        self.statuslist.reset()
        
class TimeLineModel(Q.QAbstractListModel): 
    def __init__(self, size, parent=None, *args): 
        Q.QAbstractListModel.__init__(self, parent, *args) 
        self.log = []
        self.size = size
 
    def rowCount(self, parent=Q.QModelIndex()): 
        return len(self.log) 
 
    def data(self, index, role): 
        if index.isValid() and role == Q.Qt.DisplayRole:
            return Q.QVariant(self.log[index.row()])
        else: 
            return Q.QVariant()
    
    def rotate(self, item):
        self.log.insert(0, item)
        if len(self.log) > self.size:
            self.log.pop()


####################################################################
if __name__ == "__main__": 
    main()