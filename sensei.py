#!/usr/bin/env python
import threading
import cv2
import numpy as np
import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
import psutil


class Capture(QThread):

    def __init__(self, window):
        self.capturing = False
        self.window = window
        self.cascPath = 'face.xml'
        self.cascPath = self.pyInstallerResourcePath(self.cascPath)
        self.faceCascade = cv2.CascadeClassifier(self.cascPath)
        # cv2.namedWindow('Sensei')
        # cv2.setMouseCallback('Sensei', self.mouse)
        # self.cam.set(3, self.screenwidth)
        # self.cam.set(4, self.screenheight)
        self.currPosX = None
        self.currPosY = None
        self.click_point_x = None
        self.click_point_y = None
        self.calibrated_width = []
        self.width = 0
        pathtofile = self.pyInstallerResourcePath('emoticon.png')
        self.emoji = cv2.imread(pathtofile)
        if self.emoji is None:
            print "failed to decode image"
        else:
            self.emoji = cv2.cvtColor(self.emoji, cv2.COLOR_BGR2GRAY)
        self.scale = 0.5
        self.color = (0, 0, 255)
        self.tickCount = 0
        self.seconds = 5
        self.level = 1

    def startCapture(self):
        print "pressed start"
        self.stop_event = threading.Event()

        self.cam = cv2.VideoCapture(0)
        self.screenwidth = 320
        self.screenheight = 480
        self.capturing = True
        self.c_thread = threading.Thread(
            target=self.play, args=(self.stop_event,))
        self.c_thread.start()

    def eventListener(self, stop_event):
        state = True
        while state and not stop_event.isSet():
            for i in range(10, 100):
                time.sleep(i * 0.01)
                print '.' * i

    def endCapture(self):
        print "pressed End"
        self.capturing = False

    def quitCapture(self):
        print "pressed Quit"
        self.capturing = False
        if self.cam is not None:
            self.cam.release()
        self.level = -1
        self.stop_event.set()
        QCoreApplication.quit()
        me = os.getpid()
        print "here"
        kill_proc_tree(me)

    def mouse(self):
        self.calibrated_width.append(self.width)
        self.level = 2
        print self.calibrated_width[0]

    # def mouse(self, event, x, y, flags, param):
        # if event == cv2.EVENT_MOUSEMOVE and not self.currPosX:
        #     self.currPosX, self.currPosY = x, y
        #     print x, y
        # if event == cv2.EVENT_LBUTTONUP and not self.click_point_x:
        #     # click_point_x, click_point_y = x, y
        #     self.calibrated_width.append(self.width)
        #     print "width", self.calibrated_width[0]

    def reset_mouse(self):
        self.click_point_x = -1
        self.click_point_y = -1

    def notify(self, title, subtitle, message):
        t = '-title {!r}'.format(title)
        s = '-subtitle {!r}'.format(subtitle)
        m = '-message {!r}'.format(message)
        os.system('terminal-notifier {}'.format(' '.join([m, t, s])))

    def play(self, stop_event):
        while (self.level == 1):
            success, frame = self.cam.read()
            self.tickCount += 1

            # if frameId % multiplier == 0:
            #     pass
            # else:
            #     continue
            # # Capture frame-by-frame
            print "before gray"
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # mask = np.zeros_like(gray)
            faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=2,
                minSize=(100, 100),
                #         flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                flags=0
            )

            for (x, y, w, h) in faces:
                self.width = w
                print "w1", w
                # cv2.rectangle(mask, (4 * screenwidth / 5, screenheight / 2), (4 *
                # screenwidth / 5, screenheight / 2), color=244, -1)

                # mask[y:y + h, x:x + w] = 190
                # mask = cv2.blur(mask, (24, 24))
                # if self.emoji is not None:
                # if y + self.emoji.shape[1] < self.screenheight and x +
                # self.emoji.shape[0] < self.screenwidth:

                #         mask[y:y + self.emoji.shape[0],
                #              x:x + self.emoji.shape[1]] = self.emoji

                # cv2.putText(mask, "Select proper distance",
                #             (1 * self.screenwidth / 5 + 10, 2 * self.screenheight / 3 + 20), cv2.FONT_HERSHEY_SIMPLEX, self.scale, color=200)
                # cv2.putText(mask, np.array_str(w), (x, y + 50),
                #             cv2.FONT_HERSHEY_SIMPLEX, self.scale, self.color)
                if len(faces) < 1:
                    print "no faces found"
                else:
                    self.calibrated_width.append(w)
                # cv2.putText(mask, "Sit back",
                #             (1 * self.screenwidth / 5 + 10, 2 * self.screenheight / 3 + 20), cv2.FONT_HERSHEY_SIMPLEX, self.scale, color=200)
            # Display the resulting frame
            # cv2.imshow('Sensei', mask)
            if len(self.calibrated_width) > 0:
                print "to level 2"
                self.level += 1

        while (self.level == 2):
            print "==level 2=="
            self.window.start_button.hide()
            self.window.callibrate_button.show()
            self.tickCount += 1
            # Only sample frame every x ticks

            print "next"
            self.cam = cv2.VideoCapture(0)
            success, frame = self.cam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.tickCount += 1
            faces = self.faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(100, 100),
                                                      # flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                                                      flags=0
                                                      )

            for (x, y, w, h) in faces:
                print "w", w, "calibrated_width", self.calibrated_width[0]
                if w > self.calibrated_width[0] * 1.2:
                    # Calling the function
                    print w, self.calibrated_width[0]
                    self.notify(title='Sensei',
                                subtitle='Whack!',
                                message='Sit up strait, grasshopper')
                else:
                    # cv2.rectangle(gray, (x, y), (x + w, y + h),
                    #               (0, 255, 0), 2)
                    pass
            time.sleep(10)

    def pyInstallerResourcePath(self, relativePath):
        basePath = getattr(sys, '_MEIPASS', os.path.abspath('.'))
        return os.path.join(basePath, relativePath)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.window = Window(self)
        self.setCentralWidget(self.window)
        self.cvImage = cv2.imread(r'emoticon.png')
        height, width, byteValue = self.cvImage.shape
        byteValue = byteValue * width
        cv2.cvtColor(self.cvImage, cv2.COLOR_BGR2RGB, self.cvImage)
        self.mQImage = QImage(self.cvImage, width, height,
                              byteValue, QImage.Format_RGB888)

        # For menu (non-Mac)
        # exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        # exitAction.setShortcut('Ctrl+Q')
        # exitAction.setStatusTip('Exit application')
        # exitAction.triggered.connect(QtGui.qApp.quit)
        self.statusBar()
        menubar = self.menuBar()

        # menubar.setNativeMenuBar(False)
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAction)
        # End menu

        self.show()
        self.raise_()
        # menubar = self.menuBar()
        # fileMenu = menubar.addMenu('&File')
        # fileMenu.addAction(exitAction)

    # def paintEvent(self, _):
    #     painter = QPainter(self)
    #     painter.begin(self)
    #     # painter.drawImage(0, 0, self.mQImage)
    #     painter.end()


class Window(QWidget):

    def __init__(self, parent=None):

        super(Window, self).__init__(parent)
        layout = QVBoxLayout(self)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon('emoticon.png'))
        self.trayIcon.setVisible(True)
        traySignal = "activated(QSystemTrayIcon::ActivationReason)"
        QObject.connect(self.trayIcon, SIGNAL(
            traySignal), self.__icon_activated)
        self.sysTrayMenu = QMenu(self)
        exitAction = QAction(QIcon('emoticon.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        act = self.sysTrayMenu.addAction(exitAction)
        self.setWindowTitle('Sensei - Settings')

        self.capture = Capture(self)
        self.start_button = QPushButton('Calibrate', self)
        self.start_button.clicked.connect(self.capture.startCapture)

        self.callibrate_button = QPushButton('Recalibrate', self)
        self.callibrate_button.clicked.connect(self.capture.mouse)
        self.callibrate_button.hide()

        self.end_button = QPushButton('End', self)
        self.end_button.clicked.connect(self.capture.endCapture)

        self.quit_button = QPushButton('Quit', self)
        self.quit_button.clicked.connect(self.capture.quitCapture)

        layout.addWidget(self.start_button)
        layout.addWidget(self.callibrate_button)
        layout.addWidget(self.end_button)
        layout.addWidget(self.quit_button)

        self.setGeometry(100, 100, 200, 200)
        self.show()
        self.raise_()

    def closeEvent(self, event):
        if self.okayToClose():
            # user asked for exit
            self.trayIcon.hide()
            event.accept()
        else:
            #"minimize"
            self.hide()
            self.trayIcon.show()
            event.ignore()

    def __icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def myEventListener(self, stop_event):
        state = True
        while state and not stop_event.isSet():
            for i in range(10, 100):
                time.sleep(i * 0.01)
                print '.' * i

    def cancel(self):
        self.stop_event.set()
        self.close()


def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()


def main():
    import sys
    app = QApplication(sys.argv)
    # window = Window()
    mainWindow = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


# def pyInstallerResourcePath(relativePath):
#     basePath = getattr(sys, '_MEIPASS', os.path.abspath('.'))
#     return os.path.join(basePath, relativePath)

# pdb.set_trace()
