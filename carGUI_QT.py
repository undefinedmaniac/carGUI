import sys
import time
import vlc
import os
import random
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.Qt import *
from PyQt5 import QtWidgets


class CarGUI(QMainWindow):

    def __init__(self):

        super(CarGUI, self).__init__()
        self.setGeometry(100, 100, 1024, 600)
        self.setMinimumSize(1024, 600)
        self.setMaximumSize(1024, 600)
        self.setWindowTitle('carGUI')
        self.setWindowIcon(QIcon('resources\Music_Icon.ico'))

        print(QStyleFactory.keys())

        palette = QPalette()
        palette.setColor(QPalette.Background, QtCore.Qt.darkGray)

        self.setPalette(palette)

        self.flash = True

        self.mainWidget = MainWidget()
        self.setCentralWidget(self.mainWidget)

        self.MediaPlayer = MediaClass(self)

        self.controlBar = ToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, self.controlBar)

        QApplication.setStyle(QStyleFactory.create('Fusion'))

        self.setFocusPolicy(Qt.NoFocus)
        self.show()

        # Start the periodic function
        timer = QTimer(self)
        timer.timeout.connect(self.periodic)
        timer.start(500)

        self.popUpMGR = PopUps(self)
        # self.popUpMGR.open_popup(1, 'YOLO', 'resources/ERRORICON.png')

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

        if self.MediaPlayer.advance_song:

            self.MediaPlayer.advance_song = False
            self.MediaPlayer.play_next_song()


class MainWidget(QWidget):

    def __init__(self):

        QWidget.__init__(self)

        self.osTimeClock = QLabel()
        self.mediaList = QTableWidget(0, 4)
        self.mediaList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroller_props = QScrollerProperties()
        scroller_props.setScrollMetric(
            QScrollerProperties.MaximumVelocity, .15)
        scroller_props.setScrollMetric(
            QScrollerProperties.SnapTime, .05)
        scroller_props.setScrollMetric(
            QScrollerProperties.DragVelocitySmoothingFactor, .02)

        test = QScroller.scroller(self.mediaList)

        test.setScrollerProperties(scroller_props)

        test.grabGesture(
            self.mediaList, QScroller.LeftMouseButtonGesture
        )
        
        self.rVButtons = []

        self.create_main_widget()

    def create_main_widget(self):

        main_v_box = QVBoxLayout()
        main_h_box = QHBoxLayout()
        center_layout = QGridLayout()
        menu_layout = QGridLayout()

        # Create the clock font and clock
        clock_font = QFont('Courier', 25, QFont.Bold)

        self.osTimeClock.setFont(clock_font)

        # Create the QTableWidget
        headers = ('Title', 'Artist', 'Album', 'Genre')
        headerpos = (200, 150, 65)

        self.mediaList.setFocusPolicy(Qt.NoFocus)
        self.mediaList.setHorizontalHeaderLabels(headers)

        for i, sz in enumerate(headerpos):

            self.mediaList.horizontalHeader().resizeSection(i+1, sz)
        self.mediaList.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.mediaList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mediaList.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mediaList.cellClicked.connect(self.play_media)

        # Create the center_layout and add the source buttons
        buttons = ('resources\\FILEICON', 'resources\\CDICON',
                   'resources\\USBICON', 'resources\\RADIOICON',
                   'resources\\AUXICON', 'resources\\BLUETOOTHICON',
                   'resources\\FOLDERICON', 'resources\\LISTICON')
        buttons2 = ('FILE', 'CD', 'USB', 'RADIO', 'AUX', 'BLUETOOTH', 'BROWSE', 'LIST')

        source_buttons = QButtonGroup(self)
        source_buttons.setExclusive(True)

        for i in range(8):

            sb = QPushButton(QIcon(buttons[i]), buttons2[i], self)
            sb.setIconSize(QtCore.QSize(50, 50))
            sb.setFocusPolicy(Qt.NoFocus)
            center_layout.addWidget(sb, i + 1, 1)
            sb.setStyleSheet("""
            text-align: left
            """)

            if i <= 5:

                sb.setCheckable(True)
                source_buttons.addButton(sb)

            self.rVButtons.append(sb)

        self.rVButtons[6].clicked.connect(lambda: self.parent().popUpMGR.open_popup(0))

        # Create the menu buttons
        buttons = ('Menu', 'Music', 'Video', 'Climate', 'Settings')

        menu_bar_buttons = QButtonGroup(self)
        menu_bar_buttons.setExclusive(True)

        for i in range(5):

            rb = QPushButton(buttons[i], self)

            if i != 1:

                rb.setCheckable(True)

            rb.setFocusPolicy(Qt.NoFocus)
            rb.setMinimumSize(100, 50)
            menu_bar_buttons.addButton(rb)
            menu_layout.addWidget(rb, 1, i + 1)

        # Build the layout and add it to the widget

        main_h_box.addWidget(self.mediaList)
        main_h_box.addLayout(center_layout)

        main_v_box.addWidget(self.osTimeClock)
        main_v_box.addLayout(main_h_box)
        main_v_box.addLayout(menu_layout)
        main_v_box.setAlignment(self.osTimeClock,
                                Qt.AlignCenter | Qt.AlignTop)

        self.setLayout(main_v_box)
        self.load_music()

    def play_media(self, row, column):

        if not self.parent().controlBar.toolbarButtons[3].isChecked():

            self.parent().MediaPlayer.media_queue.clear()

        self.parent().MediaPlayer.control_media(0, 0, self.mediaList.item(row, 0).data(1))
        self.parent().MediaPlayer.update_queue()

    def load_music(self, path='music/'):

        music_files = [f for f in os.listdir(path)
                       if f.endswith(".mp3") or
                       f.endswith(".wav") or
                       f.endswith(".wma")]
        
        for i in music_files:
            test = vlc.Instance()
            media = test.media_new(os.path.join(path, i))
            media.parse()

            meta_1 = vlc.libvlc_media_get_meta(media, vlc.Meta(0))
            meta_1 = meta_1.replace('.wav', '')
            meta_1 = meta_1.replace('.mp3', '')
            meta_1 = meta_1.replace('.wma', '')
            music_item_1 = QTableWidgetItem(meta_1)
            music_item_1.setData(1, os.path.join(path, i))
            music_item_2 = QTableWidgetItem(vlc.libvlc_media_get_meta(media, vlc.Meta(1)))
            music_item_3 = QTableWidgetItem(vlc.libvlc_media_get_meta(media, vlc.Meta(4)))
            music_item_4 = QTableWidgetItem(vlc.libvlc_media_get_meta(media, vlc.Meta(2)))

            current_row = self.mediaList.rowCount()
            self.mediaList.insertRow(current_row)
            self.mediaList.setItem(current_row, 0, music_item_1)
            self.mediaList.setItem(current_row, 1, music_item_2)
            self.mediaList.setItem(current_row, 2, music_item_3)
            self.mediaList.setItem(current_row, 3, music_item_4)
            

class ToolBar(QToolBar):

    def __init__(self, parent):

        QToolBar.__init__(self)

        self.toolbar_parent = parent

        # Redefined later in create_toolbar_actions
        self.playPauseAction = None
        self.nextSongAction = None
        self.previousSongAction = None

        self.create_toolbar_actions()

        self.toolbarButtons = []
        self.layoutGrid = QGridLayout()
        self.volumeSlider = QSlider(QtCore.Qt.Vertical, self)
        self.volumeSlider.setMaximum(100)
        self.volumeLabel = QLabel()
        self.layoutWidget = QWidget()

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
        self.playPauseAction = QAction(QIcon(
            'resources\PLAYICON.png'), '&Play selected media', self)
        self.playPauseAction.setShortcut('Ctrl+P')
        self.playPauseAction.triggered.connect(lambda: self.toolbar_parent.MediaPlayer.control_media(1))

        self.nextSongAction = QAction(QIcon(
            'resources\\SKIPICON.png'), '&Advance to the next song', self)
        self.nextSongAction.setShortcut('Ctrl+M')
        # self.nextSongAction.triggered.connect(self.test)

        self.previousSongAction = QAction(QIcon(
            'resources\\BACKWARDICON.png'), '&Revert to the previous song',
            self)
        self.previousSongAction.setShortcut('Ctrl+N')

    def create_toolbar_widgets(self):

        # Create toolbar pushbuttons & volume slider
        buttons = ('resources\SHUFFLEICON.png', 'resources\REPEATICON.png',
                   'resources\VOLUMEICON.png')

        for i in range(3):
            tb = QPushButton(QIcon(buttons[i]), None, self)
            tb.setCheckable(True)
            tb.setFocusPolicy(Qt.NoFocus)

            if i == 0:

                self.layoutGrid.addWidget(tb, 1, 1)
                tb.toggled.connect(self.shuffle_toggle)

                tb.setMinimumHeight(50)
            elif i == 1:

                self.layoutGrid.addWidget(tb, 1, 2)
                tb.setMinimumHeight(50)

            else:

                self.layoutGrid.addWidget(tb, 2, 1, 2, 2)
                tb.toggled.connect(self.mute_volume)
                tb.setMinimumHeight(40)

            self.toolbarButtons.append(tb)

        self.volumeSlider.setFocusPolicy(Qt.NoFocus)
        self.volumeSlider.setMinimumWidth(50)
        self.volumeSlider.setStyleSheet("""
        .QSlider::groove:vertical {
        background: white;
        position: absolute;
        left: 4px; right: 4px;
        }

        .QSlider::handle:vertical {
        border: 1px solid #5c5c5c;
        background: black;
        height: 30px;
        margin: 0 -4px; /* expand outside the groove */
        }
        """)
        self.volumeSlider.valueChanged.connect(self.volume_update)

        # Add the widgets to the grid
        self.layoutGrid.addWidget(self.volumeSlider, 4, 1)
        self.layoutGrid.addWidget(self.volumeLabel, 4, 2)

        self.layoutWidget.setLayout(self.layoutGrid)

    def shuffle_toggle(self):

        self.toolbar_parent.MediaPlayer.media_queue.clear()
        self.toolbar_parent.MediaPlayer.update_queue()

    def volume_update(self):

        if self.toolbar_parent.MediaPlayer.mediaPlayerObj.audio_get_mute:

            self.toolbarButtons[5].setChecked(False)
            self.mute_volume(False)

        new_volume = self.volumeSlider.value()
        self.toolbar_parent.MediaPlayer.mediaPlayerObj.audio_set_volume(new_volume)

        self.volumeLabel.setText(str(new_volume) + '%')

    def mute_volume(self, value):

            self.toolbar_parent.MediaPlayer.mediaPlayerObj.audio_set_mute(value)

            if value:

                self.toolbarButtons[5].setIcon(QIcon('resources/VOLUMEICONMUTED'))
                self.volumeLabel.setText(str(self.volumeSlider.value()) + '%\nMUTE')

            else:

                self.toolbarButtons[5].setIcon(QIcon('resources/VOLUMEICON'))
                self.volumeLabel.setText(str(self.volumeSlider.value()) + '%')


class PopUps(QWidget):

    def __init__(self, main_window):

        # Create the popups in memory now, display them with open_popup
        super().__init__(main_window)
        QWidget.__init__(main_window)

        self.resize(1024, 600)

        self.fileBrowser = QWidget()
        self.browser_path_label = QLabel('C:/')
        self.right_list = QListWidget()
        self.left_list = QListWidget()
        self.current_path =[]
        self.selected_path = None

        self.create_filebrowser()

        self.dialogBox = QWidget()
        self.dialogLabel = QLabel('NULL')
        self.dialogImage = QLabel()

        self.create_dialog()

        self.dialogLayout = QHBoxLayout()
        self.dialogLayout.addWidget(self.dialogBox, 0, Qt.AlignCenter)

        self.dialogWidget = QWidget()
        self.dialogWidget.setLayout(self.dialogLayout)

        self.popups = QStackedWidget(self)
        self.popups.addWidget(self.fileBrowser)
        self.popups.addWidget(self.dialogWidget)

        center_layout = QGridLayout()
        center_layout.setColumnStretch(0, 1)
        center_layout.setColumnStretch(2, 1)
        center_layout.setRowStretch(0, 1)
        center_layout.setRowStretch(2, 1)
        center_layout.addWidget(self.popups, 1, 1)

        self.setLayout(center_layout)

    def create_filebrowser(self):

        browser_v_box = QVBoxLayout()

        browser_top = QHBoxLayout()

        label_font = QFont('impact', 12)

        self.browser_path_label.setFont(label_font)
        self.browser_path_label.setAlignment(Qt.AlignCenter)

        browser_lists = QHBoxLayout()

        browser_buttons = QHBoxLayout()

        label = QLabel('Browse')
        label.setFont(label_font)

        list_font = QFont('Cambria', 20)

        exit_icon = QPushButton(QIcon('resources/EXITICON.png'), None)
        exit_icon.setMaximumSize(50, 50)
        exit_icon.clicked.connect(self.close_popup)

        space_label = QLabel()

        browser_top.addWidget(space_label)
        browser_top.addWidget(label)
        browser_top.addWidget(exit_icon)

        self.left_list.setFocusPolicy(Qt.NoFocus)

        self.right_list.setFocusPolicy(Qt.NoFocus)
        self.right_list.setFont(list_font)
        self.right_list.setMinimumWidth(500)

        QScroller.grabGesture(
            self.right_list, QScroller.LeftMouseButtonGesture
        )

        buttons = ('Back', 'Open', 'Select Folder', 'Cancel')

        button_icons = ('resources/FOLDEROUTICON.png', 'resources/FOLDERINICON.png', 'resources/SELECTICON.png', 'resources/EXITICON.png')

        select_buttons = []

        browser_buttons.addStretch(1)

        for i in range(4):
            button = QPushButton(buttons[i])
            button.setIcon(QIcon(button_icons[i]))
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

        palette = QPalette()
        palette.setColor(QPalette.Background, QtCore.Qt.lightGray)

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

            self.selected_path = os.path.join('C:/', *self.current_path, self.right_list.currentItem().data(0))

        self.parent().mainWidget.load_music(self.selected_path)

        print(self.selected_path)
        self.close_popup()

    def update_lists(self, path, mode):

        self.right_list.clear()
        self.browser_path_label.setText(os.path.join('C:\\', *self.current_path))

        if mode:

            items = next(os.walk(path))[1]
            for i in items:
                list_item = QListWidgetItem(self.right_list)
                list_item.setIcon(QIcon('resources/FOLDERICON.png'))
                list_item.setData(0, i)
                list_item.setSizeHint(QSize(300, 40))

        else:

            self.right_list.addItems(os.listdir(path))

    def create_dialog(self):

        self.dialogBox.setMinimumSize(256, 150)
        self.dialogBox.setMaximumSize(256, 150)

        palette = QPalette()
        palette.setColor(QPalette.Background, QtCore.Qt.lightGray)
        self.dialogBox.setPalette(palette)

        dialog_layout = QGridLayout()

        exit_icon = QPushButton(QIcon('resources/EXITICON.png'), None)
        exit_icon.clicked.connect(self.close_popup)

        error_font = QFont('impact', 12)

        self.dialogLabel.setFont(error_font)

        self.dialogImage.setPixmap(QPixmap('resources/ERRORICON.png').scaled(50, 50, Qt.KeepAspectRatio))

        button = QPushButton('OK')
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
            self.dialogImage.setPixmap(QPixmap(image).scaled(50, 50, Qt.KeepAspectRatio))

        elif popup == 0:

            self.current_path.clear()
            self.update_lists('C:/', True)

        self.popups.setCurrentIndex(popup)
        self.show()

    def close_popup(self):

        self.hide()


class MediaClass:

    def __init__(self, parent):

        self.localMainWidget = parent.mainWidget
        self.localParent = parent
        self.advance_song = False

        # Create VLC Media Player Instance
        self.mediaInstance = vlc.Instance()
        self.mediaPlayerObj = self.mediaInstance.media_player_new()
        vlc_events = self.mediaPlayerObj.event_manager()
        vlc_events.event_attach(vlc.EventType.MediaPlayerEndReached, self._next_song)

        # Create the queue list
        self.media_queue = []

    def control_media(self, media_action=0, media_type=0, media_location=None):

        # mediaActions      mediaType
        # 0 = PLAY          0 = FILE
        # 1 = PAUSE/RESUME  1 = CD
        # 2 = STOP

        if media_action == 0:
            if media_type == 0:
                media = self.mediaInstance.media_new(media_location)
            elif media_type == 1:
                media = self.mediaInstance.media_new("cdda:///H:/", (":cdda-track=" + str(media_location)))
            self.mediaPlayerObj.set_media(media)
            self.mediaPlayerObj.play()
            GUI.controlBar.playPauseAction.setIcon(QIcon(
                'resources\\PAUSEICON.png'))
        elif media_action == 1:
            self.mediaPlayerObj.pause()
            if self.mediaPlayerObj.is_playing():
                GUI.controlBar.playPauseAction.setIcon(QIcon(
                    'resources\\PLAYICON.png'))
            else:
                GUI.controlBar.playPauseAction.setIcon(QIcon(
                    'resources\\PAUSEICON.png'))

    def _next_song(self, event):

        self.advance_song = True

    def play_next_song(self):

        next_song = self.media_queue[0]
        self.localMainWidget.mediaList.clearSelection()
        self.localMainWidget.mediaList.setRangeSelected(
            QTableWidgetSelectionRange(next_song, 0, next_song, 3), True)
        self.media_queue.pop(0)
        self.update_queue()
        self.control_media(
            0, 0, self.localMainWidget.mediaList.item(next_song, 0).data(1)
        )

    def update_queue(self):

        selection = None

        selected_indexes = self.localMainWidget.mediaList.selectedIndexes()
        if len(selected_indexes) == 0:

            selected_index = -1
        else:

            selected_index = selected_indexes[0].row()

        row_count = self.localMainWidget.mediaList.rowCount() - 1

        for i in range(5 - len(self.media_queue)):

            if self.localParent.controlBar.toolbarButtons[3].isChecked():

                while selection in self.media_queue or \
                            selection == selected_index or selection is None:

                    selection = random.randrange(0, self.localMainWidget.mediaList.rowCount())

            else:

                if len(self.media_queue) == 0:

                    if selected_index == row_count:

                        selection = 0

                    else:

                        selection = selected_index + 1

                else:

                    new_number = self.media_queue[len(self.media_queue) - 1] + 1

                    if new_number > row_count:

                        selection = 0

                    else:

                        selection = new_number

            self.media_queue.append(selection)

        print(self.media_queue)


app = QApplication(sys.argv)
GUI = CarGUI()
sys.exit(app.exec_())
