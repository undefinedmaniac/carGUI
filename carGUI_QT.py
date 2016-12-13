import sys
import time
import vlc
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.Qt import *


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

        self.create_toolbar()
        self.create_main_widget()

        self.setCentralWidget(self.mainWidget)

        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('CDE'))

        self.setFocusPolicy(Qt.NoFocus)
        self.show()

        # Create VLC Media Player Instance
        self.mediaInstance = vlc.Instance()
        self.mediaPlayerObj = self.mediaInstance.media_player_new()

        # Start the periodic function
        timer = QTimer(self)
        timer.timeout.connect(self.periodic)
        timer.start(500)

        #self.mediaPlayer(0, 0, "C:/Non-Synced Files/CarGUI/carGUI V1/Music/Boulevard of Broken Dreams by Green Day Lyrics.mp3")

        self.create_dialog('Song Error', 'resources/ERRORICON.png')

    def periodic(self):

        # Update the clock
        AMPM = time.strftime("%p")
        hour = time.strftime("%I")
        minute = time.strftime("%M")
        if hour[0] == '0':
            hour = hour[1]
        if self.flash == True:
            value = '{}:{} {}'.format(hour, minute, AMPM)
            self.flash = False
        else:
            value = '{} {} {}'.format(hour, minute, AMPM)
            self.flash = True
        self.osTimeClock.setText(value)

    def create_toolbar(self):

        # Run functions for creating toolbar
        self.create_toolbar_actions()
        self.create_toolbar_widgets()

        self.controlBar = QToolBar()

        # Add the widgets to the toolbar
        self.addToolBar(Qt.LeftToolBarArea, self.controlBar)
        self.controlBar.setIconSize(QtCore.QSize(80, 80))
        self.controlBar.setMovable(False)
        self.controlBar.addAction(self.nextSongAction)
        self.controlBar.addAction(self.playPauseAction)
        self.controlBar.addAction(self.previousSongAction)
        self.controlBar.addWidget(self.layoutWidget)

    def create_toolbar_actions(self):

        # Create the action buttons on the toolbar
        self.playPauseAction = QtGui.QAction(QtGui.QIcon(
             'resources\PLAYICON.png'), '&Play selected media', self)
        self.playPauseAction.setShortcut('Ctrl+P')
        self.playPauseAction.triggered.connect(lambda: self.media_player(1))

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

    def create_main_widget(self):

        mainVBox = QtGui.QVBoxLayout()
        mainHBox = QtGui.QHBoxLayout()
        self.mainWidget = QtGui.QWidget()
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
            centerLayout.addWidget(sb, i+1, 1)
            if i <= 5:
                sb.setCheckable(True)
                sourceButtons.addButton(sb)
            self.rVButtons.append(sb)

        self.rVButtons[6].clicked.connect(self.create_filebrowser)

        # Create the menu buttons
        buttons = ('Menu', 'Music', 'Video', 'Climate', 'Settings')

        menubarButtons = QtGui.QButtonGroup(self)
        menubarButtons.setExclusive(True)

        for i in range(5):
            rb = QtGui.QPushButton(buttons[i], self)
            rb.setCheckable(True)
            rb.setFocusPolicy(Qt.NoFocus)
            menubarButtons.addButton(rb)
            menuLayout.addWidget(rb, 1, i+1)

        # Build the layout and add it to the widget

        mainHBox.addWidget(self.songList)
        mainHBox.addLayout(centerLayout)

        mainVBox.addWidget(self.osTimeClock)
        mainVBox.addLayout(mainHBox)
        mainVBox.addLayout(menuLayout)
        mainVBox.setAlignment(self.osTimeClock,
                              Qt.AlignCenter | Qt.AlignTop)

        self.mainWidget.setLayout(mainVBox)

    def create_dialog(self, text=None, image=None):

        try:

            if self.dialogBlocker:
                
                print('ERROR: Dialog box already on-screen!')

        except(AttributeError):

            width = self.mainWidget.width()
            height = self.mainWidget.height()

            self.dialogBlocker = QtGui.QWidget(self.mainWidget)
            self.dialogBlocker.resize(width, height)

            dialogBox = QtGui.QWidget(self.dialogBlocker)
            dialogBox.setGeometry(width/2-width*.125, height/2-height*.125,
                                       width*.25, height*.25)
            dialogBox.setAutoFillBackground(True)

            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
            dialogBox.setPalette(palette)

            dialogLayout = QtGui.QGridLayout()

            exitIcon = QtGui.QPushButton(QtGui.QIcon('resources/EXITICON.png'), None)
            exitIcon.clicked.connect(lambda: self.dialogBlocker.close())

            errorFont = QtGui.QFont('impact', 12)

            self.dialogLabel = QtGui.QLabel(text)
            self.dialogLabel.setFont(errorFont)

            self.dialogImage = QtGui.QLabel()
            self.dialogImage.setPixmap(QtGui.QPixmap(image).scaled(50, 50, Qt.KeepAspectRatio))

            button = QtGui.QPushButton('OK')
            button.setFont(errorFont)
            button.clicked.connect(lambda: self.dialogBlocker.close())

            dialogLayout.setColumnStretch(0, 1)
            dialogLayout.setColumnStretch(2, 1)
            dialogLayout.setRowStretch(2, 1)
            dialogLayout.addWidget(exitIcon, 0, 2)
            dialogLayout.addWidget(self.dialogImage, 1, 0)
            dialogLayout.addWidget(self.dialogLabel, 1, 1)
            dialogLayout.addWidget(button, 3 ,1)
            dialogLayout.setAlignment(exitIcon, Qt.AlignRight | Qt.AlignTop)
            dialogLayout.setAlignment(self.dialogImage, Qt.AlignCenter)
            dialogLayout.setAlignment(self.dialogLabel, Qt.AlignCenter)

            dialogBox.setLayout(dialogLayout)
            self.dialogBlocker.show()

    def create_filebrowser(self):
        try:

            if self.fileBlocker:

                print('ERROR: File browser already open!')

        except(AttributeError):

            width = self.mainWidget.width()
            height = self.mainWidget.height()

            self.fileBlocker = QtGui.QWidget(self.mainWidget)
            self.fileBlocker.resize(width, height)

            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)

            fileBrowser = QtGui.QWidget(self.fileBlocker)
            fileBrowser.setGeometry(width*.125, height*.125, width*.75, height*.75)
            fileBrowser.setPalette(palette)
            fileBrowser.setAutoFillBackground(True)

            browserLayout = QtGui.QGridLayout()

            label = QtGui.QLabel('Hello')
            browserLayout.addWidget(label)
            browserLayout.setAlignment(label, Qt.AlignCenter)

            fileBrowser.setLayout(browserLayout)

            self.fileBlocker.show()

    def volume_update(self):
        newVolume = self.volumeSlider.value()
        self.mediaPlayerObj.audio_set_volume(newVolume)

    def media_player(self, mediaAction=0, mediaType=0, mediaLocation=None):
        # mediaActions      mediaType
        # 0 = PLAY          0 = FILE
        # 1 = PAUSE/RESUME  1 = CD
        # 2 = STOP

        if mediaAction == 0:
            if mediaType == 0:
                media = self.mediaInstance.media_new(mediaLocation)
                self.mediaPlayerObj.set_media(media)
                self.mediaPlayerObj.play()
                self.playPauseAction.setIcon(QtGui.QIcon(
                    'resources\\PAUSEICON.png'))
        if mediaAction == 1:
            self.mediaPlayerObj.pause()
            if self.mediaPlayerObj.is_playing():
                self.playPauseAction.setIcon(QtGui.QIcon(
                    'resources\\PLAYICON.png'))
            else:
                self.playPauseAction.setIcon(QtGui.QIcon(
                    'resources\\PAUSEICON.png'))
            #self.update()

app = QtGui.QApplication(sys.argv)
GUI = CarGUI()
sys.exit(app.exec_())

##        self.shuffleToggle = QtGui.QPushButton(QtGui.QIcon('resources\SHUFFLEICON.png'), None, self)
##        self.shuffleToggle.clicked[bool].connect(self.test)
##        self.shuffleToggle.setCheckable(True)

##        leftSpacer = QtGui.QWidget()
##        leftSpacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
##
##        rightSpacer = QtGui.QWidget()
##        rightSpacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
