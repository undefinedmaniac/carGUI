import sys
import time
import vlc
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.Qt import *

global fileBrowserOpen
fileBrowserOpen = False
global dialogBoxOpen
dialogBoxOpen = False


class CarGUI(QtGui.QMainWindow):

    def __init__(self):

        super(CarGUI, self).__init__()
        self.setGeometry(100, 100, 1024, 600)
        self.setWindowTitle('carGUI')
        self.setWindowIcon(QtGui.QIcon('resources\Music_Icon.ico'))

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.darkGray)

        self.setPalette(palette)

        self.flash = True

        self.controlBar = ToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.controlBar)

        self.mainWidget = MainWidget(self)
        self.setCentralWidget(self.mainWidget)

        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('CDE'))

        self.setFocusPolicy(Qt.NoFocus)
        self.show()

        # Start the periodic function
        timer = QTimer(self)
        timer.timeout.connect(self.periodic)
        timer.start(500)

        #self.mediaPlayer(0, 0, "C:/Non-Synced Files/CarGUI/carGUI V1/Music/Boulevard of Broken Dreams by Green Day Lyrics.mp3")

    def periodic(self):

        # Update the clock
        ampm = time.strftime("%p")
        hour = time.strftime("%I")
        minute = time.strftime("%M")
        if hour[0] == '0':
            hour = hour[1]
        if self.flash == True:
            value = '{}:{} {}'.format(hour, minute, ampm)
            self.flash = False
        else:
            value = '{} {} {}'.format(hour, minute, ampm)
            self.flash = True
        self.mainWidget.osTimeClock.setText(value)


class MainWidget(QtGui.QWidget):

    def __init__(self, mainWindow):

        QWidget.__init__(self)

        self.create_main_widget(mainWindow)

    def create_main_widget(self, mainWindow):

        mainVBox = QtGui.QVBoxLayout()
        mainHBox = QtGui.QHBoxLayout()
        centerLayout = QtGui.QGridLayout()
        menuLayout = QtGui.QGridLayout()

        # Create the clock font and clock
        clockFont = QtGui.QFont('Courier', 25, QtGui.QFont.Bold)

        self.osTimeClock = QtGui.QLabel()
        self.osTimeClock.setFont(clockFont)

        # Create the QTableWidget
        headers = ('Title', 'Artist', 'Album', 'Year')
        headerpos = (300, 200, 200, 81)

        self.songList = QtGui.QTableWidget(0, 4)
        self.songList.setFocusPolicy(Qt.NoFocus)
        self.songList.setHorizontalHeaderLabels(headers)

        for i, sz in enumerate(headerpos):
            self.songList.horizontalHeader().resizeSection(i, sz)
        self.songList.horizontalHeader().setResizeMode(QHeaderView.Fixed)
        self.songList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.songList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Create the centerLayout and add the source buttons
        buttons = ('resources\\FILEICON', 'resources\\CDICON',
                   'resources\\USBICON', 'resources\\RADIOICON',
                   'resources\\AUXICON', 'resources\\BLUETOOTHICON',
                   'resources\\FOLDERICON')
        buttons2 = ('FILE', 'CD', 'USB', 'RADIO', 'AUX', 'BLUETOOTH', 'BROWSE')

        self.rVButtons = []

        sourceButtons = QtGui.QButtonGroup(self)
        sourceButtons.setExclusive(True)
        for i in range(7):
            sb = QtGui.QPushButton(QtGui.QIcon(buttons[i]), buttons2[i], self)
            sb.setIconSize(QtCore.QSize(50, 50))
            sb.setFocusPolicy(Qt.NoFocus)
            centerLayout.addWidget(sb, i + 1, 1)
            if i <= 5:
                sb.setCheckable(True)
                sourceButtons.addButton(sb)
            self.rVButtons.append(sb)

        self.rVButtons[6].clicked.connect(lambda: CreateFileBrowser(mainWindow))

        # Create the menu buttons
        buttons = ('Menu', 'Music', 'Video', 'Climate', 'Settings')

        menubarButtons = QtGui.QButtonGroup(self)
        menubarButtons.setExclusive(True)

        for i in range(5):
            rb = QtGui.QPushButton(buttons[i], self)
            rb.setCheckable(True)
            rb.setFocusPolicy(Qt.NoFocus)
            menubarButtons.addButton(rb)
            menuLayout.addWidget(rb, 1, i + 1)

        # Build the layout and add it to the widget

        mainHBox.addWidget(self.songList)
        mainHBox.addLayout(centerLayout)

        mainVBox.addWidget(self.osTimeClock)
        mainVBox.addLayout(mainHBox)
        mainVBox.addLayout(menuLayout)
        mainVBox.setAlignment(self.osTimeClock,
                              Qt.AlignCenter | Qt.AlignTop)

        self.setLayout(mainVBox)


class ToolBar(QtGui.QToolBar):

    def __init__(self):

        QToolBar.__init__(self)

        self.create_toolbar_actions()
        self.create_toolbar_widgets()
        self.create_toolbar()

    def create_toolbar(self):

        # Run functions for creating toolbar
        self.create_toolbar_actions()
        self.create_toolbar_widgets()

        # Add the widgets to the toolbar
        self.setIconSize(QtCore.QSize(80, 80))
        self.setMovable(False)
        self.addAction(self.nextSongAction)
        self.addAction(self.playPauseAction)
        self.addAction(self.previousSongAction)
        self.addWidget(self.layoutWidget)

    def create_toolbar_actions(self):

        # Create the action buttons on the toolbar
        self.playPauseAction = QtGui.QAction(QtGui.QIcon(
            'resources\PLAYICON.png'), '&Play selected media', self)
        self.playPauseAction.setShortcut('Ctrl+P')
        self.playPauseAction.triggered.connect(lambda: MediaPlayer.controlMedia(1))

        self.nextSongAction = QtGui.QAction(QtGui.QIcon(
            'resources\\SKIPICON.png'), '&Advance to the next song', self)
        self.nextSongAction.setShortcut('Ctrl+M')
        # self.nextSongAction.triggered.connect(self.test)

        self.previousSongAction = QtGui.QAction(QtGui.QIcon(
            'resources\\BACKWARDICON.png'), '&Revert to the previous song',
            self)
        self.previousSongAction.setShortcut('Ctrl+N')

    def create_toolbar_widgets(self):

        # Create toolbar pushbuttons & volume slider
        buttons = ('resources\SHUFFLEICON.png', 'resources\REPEATICON.png',
                   'resources\VOLUMEICON.png')

        self.toolbarButtons = []

        self.layoutGrid = QtGui.QGridLayout()

        for i in range(3):
            tb = QtGui.QPushButton(QtGui.QIcon(buttons[i]), None, self)
            tb.setCheckable(True)
            tb.setFocusPolicy(Qt.NoFocus)
            if i == 0:
                self.layoutGrid.addWidget(tb, 1, 1)
                tb.setMinimumHeight(50)
            elif i == 1:
                self.layoutGrid.addWidget(tb, 1, 2)
                tb.setMinimumHeight(50)
            else:
                self.layoutGrid.addWidget(tb, 2, 1, 2, 2)
            self.toolbarButtons.append(tb)

        self.volumeSlider = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setStyleSheet("""
        .QSlider:vertical {
        min-width: 40px;
        }
        """)
        self.volumeSlider.valueChanged.connect(self.volume_update)

        self.volumeLabel = QtGui.QLabel('test')

        # Add the widgets to the grid
        self.layoutGrid.addWidget(self.volumeSlider, 4, 1)
        self.layoutGrid.addWidget(self.volumeLabel, 4, 2)

        self.layoutWidget = QtGui.QWidget()
        self.layoutWidget.setLayout(self.layoutGrid)

    def volume_update(self):
        newVolume = self.volumeSlider.value()
        MediaPlayer.mediaPlayerObj.audio_set_volume(newVolume)


class CreateFileBrowser(QtGui.QWidget):

    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        QWidget.__init__(mainWindow)

        self.create_filebrowser()

    def create_filebrowser(self):

        global fileBrowserOpen
        if fileBrowserOpen:

            print('ERROR: File browser already open!')

        else:

            print('I ran yay!')

            self.resize(1024, 600)

            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)

            fileBrowser = QtGui.QWidget(self)
            fileBrowser.setGeometry(128, 75, 768, 450)
            fileBrowser.setPalette(palette)
            fileBrowser.setAutoFillBackground(True)

            browserLayout = QtGui.QGridLayout()

            label = QtGui.QLabel('Hello')
            browserLayout.addWidget(label)
            browserLayout.setAlignment(label, Qt.AlignCenter)

            fileBrowser.setLayout(browserLayout)

            fileBrowserOpen = True
            self.show()


class CreateDialog(QtGui.QWidget):

    def __init__(self, mainWindow, text, image):
        super().__init__(mainWindow)
        QWidget.__init__(mainWindow)

        self.create_dialog(text, image)

    def create_dialog(self, text, image):

            global dialogBoxOpen
            if dialogBoxOpen:

                print('ERROR: Dialog box already on-screen!')

            else:

                self.resize(1024, 600)

                dialogBox = QtGui.QWidget(self)
                dialogBox.setGeometry(384, 225, 256, 150)
                dialogBox.setAutoFillBackground(True)

                palette = QtGui.QPalette()
                palette.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
                dialogBox.setPalette(palette)

                dialogLayout = QtGui.QGridLayout()

                exitIcon = QtGui.QPushButton(QtGui.QIcon('resources/EXITICON.png'), None)
                exitIcon.clicked.connect(self.close_dialog)

                errorFont = QtGui.QFont('impact', 12)

                self.dialogLabel = QtGui.QLabel(text)
                self.dialogLabel.setFont(errorFont)

                self.dialogImage = QtGui.QLabel()
                self.dialogImage.setPixmap(QtGui.QPixmap(image).scaled(50, 50, Qt.KeepAspectRatio))

                button = QtGui.QPushButton('OK')
                button.setFont(errorFont)
                button.clicked.connect(self.close_dialog)

                dialogLayout.setColumnStretch(0, 1)
                dialogLayout.setColumnStretch(2, 1)
                dialogLayout.setRowStretch(2, 1)
                dialogLayout.addWidget(exitIcon, 0, 2)
                dialogLayout.addWidget(self.dialogImage, 1, 0)
                dialogLayout.addWidget(self.dialogLabel, 1, 1)
                dialogLayout.addWidget(button, 3, 1)
                dialogLayout.setAlignment(exitIcon, Qt.AlignRight | Qt.AlignTop)
                dialogLayout.setAlignment(self.dialogImage, Qt.AlignCenter)
                dialogLayout.setAlignment(self.dialogLabel, Qt.AlignCenter)

                dialogBox.setLayout(dialogLayout)
                dialogBoxOpen = True
                self.show()

    def close_dialog(self):
        global dialogBoxOpen
        dialogBoxOpen = False
        self.close()

class MediaClass():

    def __init__(self):

        # Create VLC Media Player Instance
        self.mediaInstance = vlc.Instance()
        self.mediaPlayerObj = self.mediaInstance.media_player_new()

    def controlMedia(self, mediaAction=0, mediaType=0, mediaLocation=None):

        # mediaActions      mediaType
        # 0 = PLAY          0 = FILE
        # 1 = PAUSE/RESUME  1 = CD
        # 2 = STOP

        if mediaAction == 0:
            if mediaType == 0:
                media = self.mediaInstance.media_new(mediaLocation)
                self.mediaPlayerObj.set_media(media)
                self.mediaPlayerObj.play()
                GUI.playPauseAction.setIcon(QtGui.QIcon(
                    'resources\\PAUSEICON.png'))
        if mediaAction == 1:
            self.mediaPlayerObj.pause()
            if self.mediaPlayerObj.is_playing():
                GUI.playPauseAction.setIcon(QtGui.QIcon(
                    'resources\\PLAYICON.png'))
            else:
                GUI.playPauseAction.setIcon(QtGui.QIcon(
                    'resources\\PAUSEICON.png'))

app = QtGui.QApplication(sys.argv)
GUI = CarGUI()
MediaPlayer = MediaClass()
sys.exit(app.exec_())

##        self.shuffleToggle = QtGui.QPushButton(QtGui.QIcon('resources\SHUFFLEICON.png'), None, self)
##        self.shuffleToggle.clicked[bool].connect(self.test)
##        self.shuffleToggle.setCheckable(True)

##        leftSpacer = QtGui.QWidget()
##        leftSpacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
##
##        rightSpacer = QtGui.QWidget()
##        rightSpacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
