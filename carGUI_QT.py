import sys
import time
import vlc
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.Qt import *


class CarGUI(QtGui.QMainWindow):

    def __init__(self):

        super(CarGUI, self).__init__()
        self.setGeometry(100, 100, 1024, 600)
        self.setMinimumSize(1024, 600)
        self.setMaximumSize(1024, 600)
        self.setWindowTitle('carGUI')
        self.setWindowIcon(QtGui.QIcon('resources\Music_Icon.ico'))

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.darkGray)

        self.setPalette(palette)

        self.flash = True

        self.controlBar = ToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.controlBar)

        self.mainWidget = MainWidget()
        self.setCentralWidget(self.mainWidget)

        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('CDE'))

        self.setFocusPolicy(Qt.NoFocus)
        self.show()

        # Start the periodic function
        timer = QTimer(self)
        timer.timeout.connect(self.periodic)
        timer.start(500)

        self.popUpMGR = PopUps(self)
        self.popUpMGR.open_popup(1, 'YOLO', 'resources/ERRORICON.png')

    def periodic(self):

        # Update the clock
        ampm = time.strftime("%p")
        hour = time.strftime("%I")
        minute = time.strftime("%M")
        if hour[0] == '0':
            hour = hour[1]
        if self.flash:
            value = '{}:{} {}'.format(hour, minute, ampm)
            self.flash = False
        else:
            value = '{} {} {}'.format(hour, minute, ampm)
            self.flash = True
        self.mainWidget.osTimeClock.setText(value)


class MainWidget(QtGui.QWidget):

    def __init__(self):

        QWidget.__init__(self)

        self.osTimeClock = QtGui.QLabel()
        self.songList = QtGui.QTableWidget(0, 4)
        self.rVButtons = []

        self.create_main_widget()

    def create_main_widget(self):

        main_v_box = QtGui.QVBoxLayout()
        main_h_box = QtGui.QHBoxLayout()
        center_layout = QtGui.QGridLayout()
        menu_layout = QtGui.QGridLayout()

        # Create the clock font and clock
        clock_font = QtGui.QFont('Courier', 25, QtGui.QFont.Bold)

        self.osTimeClock.setFont(clock_font)

        # Create the QTableWidget
        headers = ('Title', 'Artist', 'Album', 'Year')
        headerpos = (300, 200, 200, 81)

        self.songList.setFocusPolicy(Qt.NoFocus)
        self.songList.setHorizontalHeaderLabels(headers)

        for i, sz in enumerate(headerpos):
            self.songList.horizontalHeader().resizeSection(i, sz)
        self.songList.horizontalHeader().setResizeMode(QHeaderView.Fixed)
        self.songList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.songList.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # Create the center_layout and add the source buttons
        buttons = ('resources\\FILEICON', 'resources\\CDICON',
                   'resources\\USBICON', 'resources\\RADIOICON',
                   'resources\\AUXICON', 'resources\\BLUETOOTHICON',
                   'resources\\FOLDERICON')
        buttons2 = ('FILE', 'CD', 'USB', 'RADIO', 'AUX', 'BLUETOOTH', 'BROWSE')

        source_buttons = QtGui.QButtonGroup(self)
        source_buttons.setExclusive(True)
        for i in range(7):
            sb = QtGui.QPushButton(QtGui.QIcon(buttons[i]), buttons2[i], self)
            sb.setIconSize(QtCore.QSize(50, 50))
            sb.setFocusPolicy(Qt.NoFocus)
            center_layout.addWidget(sb, i + 1, 1)
            if i <= 5:
                sb.setCheckable(True)
                source_buttons.addButton(sb)
            self.rVButtons.append(sb)

        self.rVButtons[6].clicked.connect(lambda: self.parent().popUpMGR.open_popup(0))

        # Create the menu buttons
        buttons = ('Menu', 'Music', 'Video', 'Climate', 'Settings')

        menu_bar_buttons = QtGui.QButtonGroup(self)
        menu_bar_buttons.setExclusive(True)

        for i in range(5):
            rb = QtGui.QPushButton(buttons[i], self)
            rb.setCheckable(True)
            rb.setFocusPolicy(Qt.NoFocus)
            rb.setMinimumSize(100, 50)
            menu_bar_buttons.addButton(rb)
            menu_layout.addWidget(rb, 1, i + 1)

        # Build the layout and add it to the widget

        main_h_box.addWidget(self.songList)
        main_h_box.addLayout(center_layout)

        main_v_box.addWidget(self.osTimeClock)
        main_v_box.addLayout(main_h_box)
        main_v_box.addLayout(menu_layout)
        main_v_box.setAlignment(self.osTimeClock,
                                Qt.AlignCenter | Qt.AlignTop)

        self.setLayout(main_v_box)


class ToolBar(QtGui.QToolBar):

    def __init__(self):

        QToolBar.__init__(self)

        # Redefined later in create_toolbar_actions
        self.playPauseAction = None
        self.nextSongAction = None
        self.previousSongAction = None

        self.create_toolbar_actions()

        self.toolbarButtons = []
        self.layoutGrid = QtGui.QGridLayout()
        self.volumeSlider = QtGui.QSlider(QtCore.Qt.Vertical, self)
        self.volumeLabel = QtGui.QLabel('test')
        self.layoutWidget = QtGui.QWidget()

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
        self.playPauseAction.triggered.connect(lambda: MediaPlayer.control_media(1))

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

        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setStyleSheet("""
        .QSlider:vertical {
        min-width: 40px;
        }
        """)
        self.volumeSlider.valueChanged.connect(self.volume_update)

        # Add the widgets to the grid
        self.layoutGrid.addWidget(self.volumeSlider, 4, 1)
        self.layoutGrid.addWidget(self.volumeLabel, 4, 2)

        self.layoutWidget.setLayout(self.layoutGrid)

    def volume_update(self):
        new_volume = self.volumeSlider.value()
        MediaPlayer.mediaPlayerObj.audio_set_volume(new_volume)


class PopUps(QtGui.QWidget):

    def __init__(self, main_window):

        # Create the popups in memory now, display them with open_popup
        super().__init__(main_window)
        QWidget.__init__(main_window)

        self.resize(1024, 600)

        self.fileBrowser = QtGui.QWidget()
        self.browser_path_label = QtGui.QLabel('C:/')
        self.right_list = QtGui.QListWidget()
        self.left_list = QtGui.QListWidget()
        self.current_path =[]
        self.selected_path = None

        self.create_filebrowser()

        self.dialogBox = QtGui.QWidget()
        self.dialogLabel = QtGui.QLabel('NULL')
        self.dialogImage = QtGui.QLabel()

        self.create_dialog()

        self.dialogLayout = QtGui.QHBoxLayout()
        self.dialogLayout.addWidget(self.dialogBox, 0, Qt.AlignCenter)

        self.dialogWidget = QtGui.QWidget()
        self.dialogWidget.setLayout(self.dialogLayout)

        self.popups = QtGui.QStackedWidget(self)
        self.popups.addWidget(self.fileBrowser)
        self.popups.addWidget(self.dialogWidget)

        center_layout = QtGui.QGridLayout()
        center_layout.setColumnStretch(0, 1)
        center_layout.setColumnStretch(2, 1)
        center_layout.setRowStretch(0, 1)
        center_layout.setRowStretch(2, 1)
        center_layout.addWidget(self.popups, 1, 1)

        self.setLayout(center_layout)

    def create_filebrowser(self):

        browser_v_box = QtGui.QVBoxLayout()

        browser_top = QtGui.QHBoxLayout()

        label_font = QtGui.QFont('impact', 12)

        self.browser_path_label.setFont(label_font)
        self.browser_path_label.setAlignment(Qt.AlignCenter)

        browser_lists = QtGui.QHBoxLayout()

        browser_buttons = QtGui.QHBoxLayout()

        label = QtGui.QLabel('Browse')
        label.setFont(label_font)

        list_font = QtGui.QFont('Cambria', 20)

        exit_icon = QtGui.QPushButton(QtGui.QIcon('resources/EXITICON.png'), None)
        exit_icon.setMaximumSize(50, 50)
        exit_icon.clicked.connect(self.close_popup)

        space_label = QtGui.QLabel()

        browser_top.addWidget(space_label)
        browser_top.addWidget(label)
        browser_top.addWidget(exit_icon)

        self.left_list.setFocusPolicy(Qt.NoFocus)

        self.right_list.setFocusPolicy(Qt.NoFocus)
        self.right_list.setFont(list_font)
        self.right_list.setMinimumWidth(500)

        buttons = ('Back', 'Open', 'Select Folder', 'Cancel')

        button_icons = ('resources/FOLDEROUTICON.png', 'resources/FOLDERINICON.png', 'resources/SELECTICON.png', 'resources/EXITICON.png')

        select_buttons = []

        browser_buttons.addStretch(1)

        for i in range(4):
            button = QtGui.QPushButton(buttons[i])
            button.setIcon(QtGui.QIcon(button_icons[i]))
            button.setIconSize(QSize(40, 40))
            button.setFocusPolicy(Qt.NoFocus)
            button.setMinimumSize(100, 50)
            browser_buttons.addWidget(button)
            select_buttons.append(button)

        select_buttons[0].clicked.connect(self.back_item)
        select_buttons[1].clicked.connect(self.open_item)
        select_buttons[2].clicked.connect(self.select_item)
        select_buttons[3].clicked.connect(self.close_popup)

        browser_lists.addWidget(self.left_list)
        browser_lists.addWidget(self.right_list)

        browser_v_box.addLayout(browser_top)
        browser_v_box.addWidget(self.browser_path_label)
        browser_v_box.addLayout(browser_lists)
        browser_v_box.addLayout(browser_buttons)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)

        self.fileBrowser.setPalette(palette)
        self.fileBrowser.setAutoFillBackground(True)
        self.fileBrowser.setLayout(browser_v_box)
        self.fileBrowser.setMinimumSize(768, 450)

    def back_item(self):

        if not self.current_path:

            pass

        else:

            self.current_path.pop()
            self.update_lists(os.path.join('C:/', *self.current_path), True)

    def open_item(self):

        if self.right_list.currentItem() is None:

            return

        self.current_path.append(self.right_list.currentItem().data(0))
        self.update_lists(os.path.join('C:/', *self.current_path), True)

    def select_item(self):

        if self.right_list.currentItem() is None:

            self.selected_path = os.path.join('C:/', *self.current_path)

        else:

            self.selected_path = os.path.join('C:/', *self.current_path,
                                              self.right_list.currentItem().data(0))

        print(self.selected_path)
        self.close_popup()

    def update_lists(self, path, mode):

        self.right_list.clear()
        self.browser_path_label.setText(os.path.join('C:/', *self.current_path))

        if mode:

            items = next(os.walk(path))[1]
            for i in items:
                list_item = QtGui.QListWidgetItem(self.right_list)
                list_item.setIcon(QtGui.QIcon('resources/FOLDERICON.png'))
                list_item.setData(0, i)
                list_item.setSizeHint(QSize(300, 40))

        else:

            self.right_list.addItems(os.listdir(path))

    def create_dialog(self):

        self.dialogBox.setMinimumSize(256, 150)
        self.dialogBox.setMaximumSize(256, 150)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.lightGray)
        self.dialogBox.setPalette(palette)

        dialog_layout = QtGui.QGridLayout()

        exit_icon = QtGui.QPushButton(QtGui.QIcon('resources/EXITICON.png'), None)
        exit_icon.clicked.connect(self.close_popup)

        error_font = QtGui.QFont('impact', 12)

        self.dialogLabel.setFont(error_font)

        self.dialogImage.setPixmap(QtGui.QPixmap('resources/ERRORICON.png').scaled(50, 50, Qt.KeepAspectRatio))

        button = QtGui.QPushButton('OK')
        button.setFont(error_font)
        button.clicked.connect(self.close_popup)

        dialog_layout.setColumnStretch(0, 1)
        dialog_layout.setColumnStretch(2, 1)
        dialog_layout.setRowStretch(2, 1)
        dialog_layout.addWidget(exit_icon, 0, 2)
        dialog_layout.addWidget(self.dialogImage, 1, 0)
        dialog_layout.addWidget(self.dialogLabel, 1, 1)
        dialog_layout.addWidget(button, 3, 1)
        dialog_layout.setAlignment(exit_icon, Qt.AlignRight | Qt.AlignTop)
        dialog_layout.setAlignment(self.dialogImage, Qt.AlignCenter)
        dialog_layout.setAlignment(self.dialogLabel, Qt.AlignCenter)

        self.dialogBox.setAutoFillBackground(True)
        self.dialogBox.setLayout(dialog_layout)

    def open_popup(self, popup, text=None, image=None):

        if popup == 1:

            self.dialogLabel.setText(text)
            self.dialogImage.setPixmap(QtGui.QPixmap(image).scaled(50, 50, Qt.KeepAspectRatio))

        elif popup == 0:

            self.current_path.clear()
            self.update_lists('C:/', True)

        self.popups.setCurrentIndex(popup)
        self.show()

    def close_popup(self):

        self.hide()


class MediaClass:

    def __init__(self):

        # Create VLC Media Player Instance
        self.mediaInstance = vlc.Instance()
        self.mediaPlayerObj = self.mediaInstance.media_player_new()
        self.mediaMetaData = []

    def control_media(self, media_action=0, media_type=0, media_location=None):

        # mediaActions      mediaType
        # 0 = PLAY          0 = FILE
        # 1 = PAUSE/RESUME  1 = CD
        # 2 = STOP

        if media_action == 0:
            if media_type == 0:
                media = self.mediaInstance.media_new(media_location)
                media.parse()
                self.mediaMetaData.clear()
                self.mediaMetaData.append(vlc.libvlc_media_get_meta(media, vlc.Meta(0)))
                self.mediaMetaData.append(vlc.libvlc_media_get_meta(media, vlc.Meta(1)))
                self.mediaMetaData.append(vlc.libvlc_media_get_meta(media, vlc.Meta(2)))
                self.mediaMetaData.append(vlc.libvlc_media_get_meta(media, vlc.Meta(4)))
            elif media_type == 1:
                media = self.mediaInstance.media_new("cdda:///H:/", (":cdda-track=" + str(media_location)))
            self.mediaPlayerObj.set_media(media)
            self.mediaPlayerObj.play()
            GUI.controlBar.playPauseAction.setIcon(QtGui.QIcon(
                'resources\\PAUSEICON.png'))
        elif media_action == 1:
            self.mediaPlayerObj.pause()
            if self.mediaPlayerObj.is_playing():
                GUI.controlBar.playPauseAction.setIcon(QtGui.QIcon(
                    'resources\\PLAYICON.png'))
            else:
                GUI.controlBar.playPauseAction.setIcon(QtGui.QIcon(
                    'resources\\PAUSEICON.png'))

app = QtGui.QApplication(sys.argv)
GUI = CarGUI()
MediaPlayer = MediaClass()
# MediaPlayer.control_media(0, 1, 1)
sys.exit(app.exec_())
