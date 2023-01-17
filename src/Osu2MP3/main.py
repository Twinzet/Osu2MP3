import sys, glob, os, shutil
from PySide2.QtGui import QColor, QMovie
from PySide2.QtCore import QSize, QRunnable, QThreadPool, QObject, Signal, QByteArray, QBuffer
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QFileDialog, QLabel, QGraphicsOpacityEffect, QTextBrowser, QFrame, QProgressBar

class Signals(QObject):
    error = Signal(int)
    max = Signal(int)
    addIt = Signal()
    finished = Signal()
    currentPath = Signal(str)
    showLayout2 = Signal()

class Worker(QRunnable):

    def __init__(self, sourceFolder, destFolder):
        super().__init__()
        self.signal = Signals()
        self.sourceFolder = sourceFolder
        self.destFolder = destFolder

    def run(self):
        if self.sourceFolder != "Select path" and self.destFolder != "Select path":
            self.signal.showLayout2.emit()

            maxBar = len([initMax for initMax in os.listdir(self.sourceFolder)])
            self.signal.max.emit(maxBar)

            minFileSize = 200000 # Smallest file size allowed to be copied (Bytes)
            addItNow = 0

            os.chdir(self.sourceFolder)
            for file in glob.glob("**/*.mp3"): # Find all MP3 files located in "Songs"
                targetFile = f"{self.sourceFolder}/{file}" # Create a string with the file path

                newFile = file.split('\\')
                name = newFile[0]

                list_dir = os.listdir(self.destFolder)

                if f"{name}.mp3" not in list_dir:
                    if os.path.getsize(targetFile) > minFileSize: # Check file size
                        self.signal.currentPath.emit(f" > {name}")
                        self.signal.addIt.emit()
                        addItNow = addItNow + 1
                        targetFolder = f"{self.destFolder}/{name}.mp3"
                        shutil.copy(targetFile, targetFolder) # Copy file to the new folder
            
            if addItNow == 0:
                self.signal.currentPath.emit("\n  No new songs to transfer!")

            else:
                if addItNow == 1:
                    self.signal.currentPath.emit("\n  1 song transferred! (≧◡≦)\n")

                else:
                    self.signal.currentPath.emit(f"\n  {addItNow} songs transferred! (≧◡≦)\n")

            self.signal.finished.emit()

        else:
            if self.sourceFolder == "Select path" and self.destFolder != "Select path":
                self.signal.error.emit(0)

            if self.destFolder == "Select path" and self.sourceFolder != "Select path":
                self.signal.error.emit(1)

            if self.destFolder == "Select path" and self.sourceFolder == "Select path":
                self.signal.error.emit(2)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        dancePath = self.resource_path('dance.gif')
        folderIcon = self.resource_path('folderIcon.png')
        logoTitle = self.resource_path('logoTitle.png')
        osuBackground = self.resource_path('OsuBackground.png')
        pauseBack = self.resource_path('pause-back.png')
        pauseBack1 = self.resource_path('pause-back1.png')

        self.wWidth = 1024
        self.wHeight = 728

        self.setWindowTitle("Osu! to MP3")
        self.setFixedSize(QSize(self.wWidth, self.wHeight))

        self.layoutWidget = QWidget(self)

        self.sourceFolder = "Select path"
        self.destFolder = "Select path"

        self.backImage = QLabel(self.layoutWidget)
        self.backImage.setFixedSize(QSize(self.wWidth, self.wHeight))
        self.backImage.setStyleSheet(f"border-image: url({osuBackground});")

        frameDirHeight = self.wHeight * 0.97
        frameDirWidth = self.wWidth * 0.8
        self.frameBox = QLabel(self.layoutWidget)
        self.frameBox.setStyleSheet("background-color: black")
        self.frameBox.setFixedSize(QSize(frameDirWidth, frameDirHeight))
        self.frameBox.move((self.wWidth - frameDirWidth) / 2, (self.wHeight - frameDirHeight) / 2)

        self.titleLogo = QLabel(self.layoutWidget)
        self.titleLogo.setStyleSheet(f"Border-image: url({logoTitle})")
        self.titleLogo.setFixedSize(self.wWidth / 2.56, self.wHeight / 3.5)
        self.titleLogo.move(self.wWidth / 3.41, self.wHeight / 18.2)

        idealRations = self.wHeight / 26

        sourceFrameHeight = self.wHeight * 0.025
        sourceFrameWidth = self.wWidth * 0.6
        sourceFrameMove = self.wHeight / 2.4
        self.sourceFrame = QLabel(self.layoutWidget)
        self.sourceFrame.setText(" Select path")
        self.sourceFrame.setStyleSheet("background-color: white; color: grey")
        self.sourceFrame.setFixedSize(QSize(sourceFrameWidth, sourceFrameHeight))
        self.sourceFrame.move((self.wWidth - sourceFrameWidth) / 2, sourceFrameMove + idealRations)

        destFrameMove = self.wHeight / 1.8
        self.destFrame = QLabel(self.layoutWidget)
        self.destFrame.setText(" Select path")
        self.destFrame.setStyleSheet("background-color: white; color: grey")
        self.destFrame.setFixedSize(QSize(sourceFrameWidth, sourceFrameHeight))
        self.destFrame.move((self.wWidth - sourceFrameWidth) / 2, destFrameMove + idealRations)

        self.sourceLabel = QLabel(self.layoutWidget)
        self.sourceLabel.setText('Select your Osu! "Songs" folder containing your beatmaps:')
        self.sourceLabel.setStyleSheet("font-Size: 18px; color: white")
        self.sourceLabel.setFixedSize(QSize(sourceFrameWidth, sourceFrameHeight * 2))
        self.sourceLabel.move((self.wWidth - sourceFrameWidth) / 2, sourceFrameMove - sourceFrameHeight * 2 + idealRations)

        self.destLabel = QLabel(self.layoutWidget)
        self.destLabel.setText("Select the destination folder for your MP3s:")
        self.destLabel.setStyleSheet("font-Size: 18px; color: white")
        self.destLabel.setFixedSize(QSize(sourceFrameWidth, sourceFrameHeight * 2))
        self.destLabel.move((self.wWidth - sourceFrameWidth) / 2, destFrameMove - sourceFrameHeight * 2 + idealRations)

        self.error1 = QLabel(self.layoutWidget)
        self.error1.setText(" Invalid Path")
        self.error1.setStyleSheet("color:rgb(237, 67, 55)")
        self.error1.setFixedSize(QSize(sourceFrameWidth, sourceFrameHeight))
        self.error1.move((self.wWidth - sourceFrameWidth) / 2, sourceFrameMove + sourceFrameHeight + idealRations)
        self.error1.setVisible(False)

        self.error2 = QLabel(self.layoutWidget)
        self.error2.setText(" Invalid Path")
        self.error2.setStyleSheet("color:rgb(237, 67, 55)")
        self.error2.setFixedSize(QSize(sourceFrameWidth, sourceFrameHeight))
        self.error2.move((self.wWidth - sourceFrameWidth) / 2, destFrameMove + sourceFrameHeight + idealRations)
        self.error2.setVisible(False)

        self.darken = QGraphicsOpacityEffect(opacity=0.5)
        self.frameBox.setGraphicsEffect(self.darken)

        sourceDirSize = sourceFrameHeight * 1.4
        sourceDirMove = self.wHeight / 2.42
        self.sourceDirButton = QPushButton(self.layoutWidget)
        self.sourceDirButton.clicked.connect(self.sourceClicked)
        self.sourceDirButton.setFixedSize(QSize(sourceDirSize, sourceDirSize))
        self.sourceDirButton.move((self.wWidth + sourceFrameWidth) / 2 + self.wWidth / 204, sourceDirMove + idealRations)
        self.sourceDirButton.setStyleSheet(f"border-image: url({folderIcon});")

        destDirMove = self.wHeight / 1.82
        self.destDirButton = QPushButton(self.layoutWidget)
        self.destDirButton.clicked.connect(self.destClicked)
        self.destDirButton.setFixedSize(QSize(sourceDirSize, sourceDirSize))
        self.destDirButton.move((self.wWidth + sourceFrameWidth) / 2 + self.wWidth / 204, destDirMove + idealRations)
        self.destDirButton.setStyleSheet(f"border-image: url({folderIcon});")

        startButtonWidth = self.wWidth / 3.2
        startButtonHeight = self.wHeight / 10
        self.startButton = QPushButton(self.layoutWidget)
        self.startButton.clicked.connect(self.startProcess)
        self.startButton.setFixedSize(QSize(startButtonWidth, startButtonHeight))
        self.startButton.move((self.wWidth - startButtonWidth) / 2, self.wHeight / 1.4)
        self.startButton.setStyleSheet(f"font-size: 18px; color: white; border-radius: {startButtonWidth / 80}px; background:rgb(255, 102, 170)")
        self.startButton.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                color: white;
                border-radius: 4px;
                background:rgb(255, 102, 170);
            }
            QPushButton:hover {
                background:rgb(207, 40, 132);
            }
            QPushButton:hover:!pressed {
                background:rgb(218, 71, 152);
            }
        """)
        self.startButton.setText("Start!")

        cmdScrollHeight = self.wHeight * 0.7
        self.cmdScroll = QTextBrowser(self.layoutWidget)
        self.cmdScroll.setFixedSize(QSize(sourceFrameWidth, cmdScrollHeight))
        self.cmdScroll.move((self.wWidth - sourceFrameWidth) / 2 + self.wWidth / 17, self.wHeight / 18.2)
        self.cmdScroll.setStyleSheet("background:rgb(40,40,40)")
        self.cmdScroll.setTextColor(QColor(255,255,255))
        self.cmdScroll.setFontPointSize(11)
        self.cmdScroll.setFrameStyle(QFrame.NoFrame)
        self.cmdScroll.setVisible(False)

        self.danceFrame = QLabel(self.layoutWidget)
        self.danceFrame.setVisible(False)
        self.danceFrame.move(0, self.wHeight / 2.4)

        danceGif = open(os.path.join(dancePath), "rb").read()
        self.byteArray = QByteArray(danceGif)
        self.buffer = QBuffer(self.byteArray)
        self.dance = QMovie()
        self.dance.setDevice(self.buffer)
        self.dance.setCacheMode(QMovie.CacheAll)
        self.dance.setSpeed(100)
        self.danceFrame.setMovie(self.dance)
        self.dance.jumpToFrame(0)

        self.progressValue = 0
        self.progressBar = QProgressBar(self.layoutWidget)
        self.progressBar.setMinimum(0)
        self.progressBar.setFixedSize(QSize(sourceFrameWidth, sourceFrameHeight))
        self.progressBar.move((self.wWidth - sourceFrameWidth) / 2 + self.wWidth / 17, self.wHeight / 1.29)
        self.progressBar.setStyleSheet("QProgressBar::chunk " "{" "background:rgb(255, 102, 170);" "}")
        self.progressBar.setTextVisible(False)
        self.progressBar.setVisible(False)

        menuButtonWidth = self.wWidth / 2.5
        menuButtonHeight = self.wHeight / 6

        self.menuLabel = QLabel(self.layoutWidget)
        self.menuLabel.setFixedSize(menuButtonWidth * 0.7, menuButtonHeight * 0.7)
        self.menuLabel.move(self.wWidth / 2.5, self.wHeight / 1.2)
        self.menuLabel.setStyleSheet(f"border-image: url({pauseBack1});")
        self.menuLabel.setVisible(False) 

        menuStyle1 = """
            QPushButton {
                border-image: url(pause-back);
                border: none;
            }
            QPushButton:hover {
                border-image: url(pause-back1);
            }
        """
        menuStyle2 = menuStyle1.replace("pause-back", pauseBack)
        menuStyle = menuStyle2.replace("pause-back1", pauseBack1)

        self.menuButton = QPushButton(self.layoutWidget)
        self.menuButton.clicked.connect(self.showOldGui)
        self.menuButton.setFixedSize(menuButtonWidth * 0.7, menuButtonHeight * 0.7)
        self.menuButton.move(self.wWidth / 2.5, self.wHeight / 1.2)
        self.menuButton.setStyleSheet(menuStyle)
        self.menuButton.setVisible(False)

        self.setCentralWidget(self.layoutWidget)

    ### Use this function To attach files to the exe file (eg - png, txt, jpg etc) using pyinstaller
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        returnPath = os.path.join(base_path, relative_path)

        returnPath = returnPath.replace("\\", "/")

        return returnPath

    def sourceClicked(self):
        self.sourceFolder = str(QFileDialog.getExistingDirectory(self, 'Select Osu! "Songs" Folder'))

        if self.sourceFolder == "":
            self.sourceFolder = "Select path"
            self.sourceFrame.setStyleSheet("background-color: white; color: grey")

        else:
            self.sourceFrame.setStyleSheet("background-color: white; color: black")

        self.sourceFrame.setText(f" {self.sourceFolder}")

    def destClicked(self):
        self.destFolder = str(QFileDialog.getExistingDirectory(self, "Select Destination Folder"))

        if self.destFolder == "":
            self.destFolder = "Select path"
            self.destFrame.setStyleSheet("background-color: white; color: grey")

        else:
            self.destFrame.setStyleSheet("background-color: white; color: black")

        self.destFrame.setText(f" {self.destFolder}")

    def appendText(self, message):
        self.cmdScroll.append(message)

    def showOldGui(self):
        self.cmdScroll.clear()
        self.cmdScroll.setVisible(False)
        self.progressBar.setVisible(False)
        self.danceFrame.setVisible(False)
        self.menuButton.setVisible(False)
        self.menuLabel.setVisible(False)
        self.sourceLabel.setVisible(True)
        self.destLabel.setVisible(True)
        self.startButton.setVisible(True)
        self.sourceFrame.setVisible(True)
        self.sourceDirButton.setVisible(True)
        self.destFrame.setVisible(True)
        self.destDirButton.setVisible(True)
        self.dance.stop()

    def finishedTransfer(self):
        if self.progressValue != self.progressBar.maximum():
            self.progressBar.setValue(self.progressBar.maximum())

        self.menuButton.setVisible(True)
        self.menuLabel.setVisible(True)

    def userError(self, num):
        self.showOldGui()
        self.error1.setVisible(False)
        self.error2.setVisible(False)

        if num == 0 or num == 2:
            self.error1.setVisible(True)

        if num == 1 or num == 2:
            self.error2.setVisible(True)

    def progressBarMax(self, max):
        self.progressBar.setMaximum(max)

    def progressBarAdd(self):
        self.progressValue = self.progressValue+1
        self.progressBar.setValue(self.progressValue)

    def showLayout2(self):
        self.error1.setVisible(False)
        self.error2.setVisible(False)
        self.startButton.setVisible(False)
        self.sourceFrame.setVisible(False)
        self.sourceDirButton.setVisible(False)
        self.destFrame.setVisible(False)
        self.destDirButton.setVisible(False)
        self.sourceLabel.setVisible(False)
        self.destLabel.setVisible(False)
        self.cmdScroll.setVisible(True)
        self.progressBar.setVisible(True)
        self.danceFrame.setVisible(True)
        self.dance.start()

    def startProcess(self):
        self.worker = Worker(self.sourceFolder, self.destFolder)
        self.worker.signal.max.connect(self.progressBarMax)
        self.worker.signal.addIt.connect(self.progressBarAdd)
        self.worker.signal.error.connect(self.userError)
        self.worker.signal.finished.connect(self.finishedTransfer)
        self.worker.signal.currentPath.connect(self.appendText)
        self.worker.signal.showLayout2.connect(self.showLayout2)
        QThreadPool.globalInstance().start(self.worker)

app = QApplication(sys.argv)


window = MainWindow()
window.show()

if __name__ == "__main__":
    app.exec_()