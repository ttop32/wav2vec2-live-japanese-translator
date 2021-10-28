# https://clay-atlas.com/us/blog/2021/03/04/pyqt5-cn-hide-title-bar-move-interface/
# https://stackoverflow.com/questions/62807295/how-to-resize-a-window-from-the-edges-after-adding-the-property-qtcore-qt-framel


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.moveFlag = False
        self.initUI()
# https://clay-atlas.com/us/blog/2021/03/04/pyqt5-cn-hide-title-bar-move-interface/
# https://stackoverflow.com/questions/62807295/how-to-resize-a-window-from-the-edges-after-adding-the-property-qtcore-qt-framel


import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.moveFlag = False
        self.initUI()

    def initUI(self):
        self.resize(900, 300)
        self.setWindowTitle('wav2vec2-live-japanese-translator')
        self.setWindowOpacity(0.8)      #make transparent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)   #no frame and always on top
        self.center() #make center window position

        #set style
        self.setStyleSheet("""
        QMainWindow {
            border-radius: 20px;
            background-color: Black;
            }
        QTextEdit{
            border: 0;
            color: White;
            background-color: Black;
            font-size: 18pt;
            }
        QPushButton{
            font-size: 14pt;
            font-weight: bold;
            color: White;
            background-color: Black;
            }
        QPushButton:hover {
             background-color: Red;
             }
        QComboBox{
            border : 1px solid White;
            border-radius: 2px;
            font-size: 12pt;
            color: White;
            background-color: Black;
            }
        QLabel{
            color: White;
            font-size: 12pt;
            }
        QComboBox {
            width:350px;
            }
        QScrollBar:vertical {
            height:0px;
            }
        """)




        #close button
        btn1 = QPushButton("X")
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.close)





        #top menu
        label1 = QLabel(' Device: ', self)
        label2 = QLabel(' Lang: ', self)
        label3 = QLabel(' Model: ', self)
        self.cb1 = QComboBox()
        self.cb2 = QComboBox()
        self.cb3 = QComboBox()

        #main text display
        self.text_area = QTextEdit()
        self.text_area.setTextInteractionFlags (Qt.NoTextInteraction)


        #x layout, top menu and main text display
        xLayout = QHBoxLayout()
        xLayout.addWidget(label1)
        xLayout.addWidget(self.cb1)
        xLayout.addWidget(label2)
        xLayout.addWidget(self.cb2)
        xLayout.addWidget(label3)
        xLayout.addWidget(self.cb3)
        xLayout.addStretch(1)
        xLayout.addWidget(btn1)

        #top menu and close button
        yLayout = QVBoxLayout()
        yLayout.addLayout(xLayout)
        yLayout.addWidget(self.text_area)

        #main widget
        centralWidget = QWidget()
        centralWidget.setObjectName("centralWidget")
        centralWidget.setLayout(yLayout)
        self.setCentralWidget(centralWidget)


        #====================window rsize side
        self.sideGrips = [
            SideGrip(self, Qt.LeftEdge),
            SideGrip(self, Qt.TopEdge),
            SideGrip(self, Qt.RightEdge),
            SideGrip(self, Qt.BottomEdge),
        ]
        # corner grips should be "on top" of everything, otherwise the side grips
        # will take precedence on mouse events, so we are adding them *after*;
        # alternatively, widget.raise_() can be used
        self.cornerGrips = [QSizeGrip(self) for i in range(4)]





    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


    def setupComboBox(self,comboBox,dataDict,default,callback):
        comboBox.addItems(dataDict.keys())
        comboBox.setCurrentIndex(list(dataDict.keys()).index(default))
        comboBox.activated[str].connect(callback)

    @pyqtSlot(str)
    def setTextAppend(self,text):
        self.text_area.append(text)

    def setText(self,text):
        self.text_area.clear()
        self.text_area.append(text)


    #=================================================window move using drag
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()
    def mouseReleaseEvent(self, event):
        self.moveFlag = False

    #==========================window resizeable
    @property
    def gripSize(self):
        return 8

    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()

    def updateGrips(self):
        # self.setContentsMargins(*[self.gripSize] * 4)

        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(self.gripSize, self.gripSize,
            -self.gripSize, -self.gripSize)

        # top left
        self.cornerGrips[0].setGeometry(
            QRect(outRect.topLeft(), inRect.topLeft()))
        # top right
        self.cornerGrips[1].setGeometry(
            QRect(outRect.topRight(), inRect.topRight()).normalized())
        # bottom right
        self.cornerGrips[2].setGeometry(
            QRect(inRect.bottomRight(), outRect.bottomRight()))
        # bottom left
        self.cornerGrips[3].setGeometry(
            QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized())

        # left edge
        self.sideGrips[0].setGeometry(
            0, inRect.top(), self.gripSize, inRect.height())
        # top edge
        self.sideGrips[1].setGeometry(
            inRect.left(), 0, inRect.width(), self.gripSize)
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(),
            inRect.top(), self.gripSize, inRect.height())
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize, inRect.top() + inRect.height(),
            inRect.width(), self.gripSize)

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.updateGrips()


#window reszie class
class SideGrip(QWidget):
    def __init__(self, parent, edge):
        QWidget.__init__(self, parent)
        if edge == Qt.LeftEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.TopEdge:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.RightEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
    def initUI(self):
        self.resize(900, 300)
        self.setWindowTitle('wav2vec2-live-japanese-translator')
        self.setWindowOpacity(0.8)      #make transparent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)   #no frame and always on top
        self.center() #make center window position

        #set style
        self.setStyleSheet("""
        QMainWindow {
            border-radius: 20px;
            background-color: Black;
            }
        QTextEdit{
            border: 0;
            color: White;
            background-color: Black;
            font-size: 18pt;
            }
        QPushButton{
            font-size: 14pt;
            font-weight: bold;
            color: White;
            background-color: Black;
            }
        QPushButton:hover {
             background-color: Red;
             }
        QComboBox{
            border : 1px solid White;
            border-radius: 2px;
            font-size: 12pt;
            color: White;
            background-color: Black;
            }
        QLabel{
            color: White;
            font-size: 12pt;
            }
        QScrollBar:vertical {
            height:0px;
            }
        """)




        #close button
        btn1 = QPushButton("X")
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.close)

        #top menu
        label1 = QLabel(' Device: ', self)
        label2 = QLabel(' Lang: ', self)
        self.cb1 = QComboBox()
        self.cb2 = QComboBox()

        #main text display
        self.text_area = QTextEdit()
        self.text_area.setTextInteractionFlags (Qt.NoTextInteraction)


        #x layout, top menu and main text display
        xLayout = QHBoxLayout()
        xLayout.addWidget(label1)
        xLayout.addWidget(self.cb1)
        xLayout.addWidget(label2)
        xLayout.addWidget(self.cb2)
        xLayout.addStretch(1)
        xLayout.addWidget(btn1)

        #top menu and close button
        yLayout = QVBoxLayout()
        yLayout.addLayout(xLayout)
        yLayout.addWidget(self.text_area)

        #main widget
        centralWidget = QWidget()
        centralWidget.setObjectName("centralWidget")
        centralWidget.setLayout(yLayout)
        self.setCentralWidget(centralWidget)


        #====================window rsize side
        self.sideGrips = [
            SideGrip(self, Qt.LeftEdge),
            SideGrip(self, Qt.TopEdge),
            SideGrip(self, Qt.RightEdge),
            SideGrip(self, Qt.BottomEdge),
        ]
        # corner grips should be "on top" of everything, otherwise the side grips
        # will take precedence on mouse events, so we are adding them *after*;
        # alternatively, widget.raise_() can be used
        self.cornerGrips = [QSizeGrip(self) for i in range(4)]





    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


    def setupComboBox(self,comboBox,dataDict,default,callback):
        comboBox.addItems(dataDict.keys())
        comboBox.setCurrentIndex(list(dataDict.keys()).index(default))
        comboBox.activated[str].connect(callback)

    @pyqtSlot(str)
    def setTextAppend(self,text):
        self.text_area.append(text)

    def setText(self,text):
        self.text_area.clear()
        self.text_area.append(text)


    #=================================================window move using drag
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()
    def mouseReleaseEvent(self, event):
        self.moveFlag = False

    #==========================window resizeable
    @property
    def gripSize(self):
        return 8

    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()

    def updateGrips(self):
        # self.setContentsMargins(*[self.gripSize] * 4)

        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(self.gripSize, self.gripSize,
            -self.gripSize, -self.gripSize)

        # top left
        self.cornerGrips[0].setGeometry(
            QRect(outRect.topLeft(), inRect.topLeft()))
        # top right
        self.cornerGrips[1].setGeometry(
            QRect(outRect.topRight(), inRect.topRight()).normalized())
        # bottom right
        self.cornerGrips[2].setGeometry(
            QRect(inRect.bottomRight(), outRect.bottomRight()))
        # bottom left
        self.cornerGrips[3].setGeometry(
            QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized())

        # left edge
        self.sideGrips[0].setGeometry(
            0, inRect.top(), self.gripSize, inRect.height())
        # top edge
        self.sideGrips[1].setGeometry(
            inRect.left(), 0, inRect.width(), self.gripSize)
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(),
            inRect.top(), self.gripSize, inRect.height())
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize, inRect.top() + inRect.height(),
            inRect.width(), self.gripSize)

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.updateGrips()


#window reszie class
class SideGrip(QWidget):
    def __init__(self, parent, edge):
        QWidget.__init__(self, parent)
        if edge == Qt.LeftEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.TopEdge:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.RightEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
