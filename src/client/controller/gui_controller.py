"""Module for the GUI controller."""

from collections import OrderedDict
from functools import partial
from threading import Thread
from typing import List, Optional

from PySide6.QtCore import QEvent, QSize, QTimer
from PySide6.QtGui import QEnterEvent, QIcon, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLayout,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.client.controller import global_variables
from src.client.controller.api_controller import ApiController
from src.client.controller.connection_controller import ConnectionController
from src.client.controller.event_manager import EventManager
from src.client.controller.messages_controller.avatar_controller import AvatarController
from src.client.controller.messages_controller.messages_controller import (
    MessagesController,
)
from src.client.controller.messages_controller.reaction_controller import (
    ReactController,
)
from src.client.controller.messages_controller.router_controller import RouterController
from src.client.controller.tcp_controller import TcpServerController
from src.client.controller.user_profile_controller import UserProfileController
from src.client.view.custom_widget.custom_avatar_label import AvatarLabel, AvatarStatus
from src.client.view.custom_widget.custom_button import CustomQPushButton
from src.client.view.custom_widget.custom_line_edit import CustomQLineEdit
from src.client.view.layout.body_scroll_area import BodyScrollArea
from src.client.view.layout.message_layout import MessageLayout
from src.tools.utils import (
    GenericColor,
    Icon,
    ImageAvatar,
    Themes,
    check_str_len,
    icon_from_svg,
)


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
class GuiController:
    """
    GUI controller class.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        ui,
        messages_dict: dict[str, MessageLayout],
        api_controller: ApiController,
        tcp_controller: TcpServerController,
        event_manager: EventManager,
        theme: Themes,
    ) -> None:
        self.ui = ui
        self.theme = theme
        self.theme_board = None
        self.worker_thread = None
        self.room_icon = None
        self.is_focused = None

        self.messages_dict: dict[str, List[MessageLayout]] = messages_dict
        self.dm_avatar_dict: dict[str, AvatarLabel] = {}

        self.event_manager = event_manager

        self.api_controller = api_controller
        self.tcp_controller = tcp_controller
        self.messages_controller = MessagesController(self, ui, self.messages_dict)
        self.react_controller = ReactController(self, ui, self.messages_dict)
        self.router_controller = RouterController(self, ui)
        self.avatar_controller = AvatarController(self, ui, self.dm_avatar_dict)
        self.user_profile_controller = UserProfileController(self, ui)
        self.connection_controller = ConnectionController(self, ui)

    def init_working_signals(self) -> None:
        """
        Init signals for incoming messages
        """
        self.event_manager.coming_message_signal.connect(
            self.messages_controller.diplay_coming_message_on_gui
        )

        self.event_manager.users_connected_signal.connect(
            self.avatar_controller.update_gui_with_connected_avatar
        )

        self.event_manager.users_disconnected_signal.connect(
            self.avatar_controller.update_gui_with_disconnected_avatar
        )
        self.event_manager.react_message_signal.connect(
            self.react_controller.update_react_message_on_gui
        )
        self.worker_thread = Thread(
            target=self.router_controller.callback_routing_messages_on_ui, daemon=False
        )
        self.worker_thread.start()

        # Update buttons status
        self.update_buttons()

    def update_scroll_bar(self) -> None:
        """
        Callback to handle scroll bar update
        """
        self.ui.scroll_area.scrollToBottom()

    def clear(self) -> None:
        """
        Clear the main layout
        """
        for i in reversed(range(self.ui.scroll_area.main_layout.count())):
            layout = self.ui.scroll_area.main_layout.itemAt(i).layout()
            if isinstance(layout, QLayout):
                for j in reversed(range(layout.count())):
                    layout.itemAt(j).widget().deleteLater()
        self.ui.scroll_area.main_layout.update()

    def hide_left_layouts_buttons(self) -> None:
        """
        Hide left button
        """
        self.ui.header.close_left_nav_button.hide()

    def show_left_layouts_buttons(self) -> None:
        """
        Show left button
        """
        self.ui.show_left_nav_button.show()
        self.ui.close_left_nav_button.show()

    def hide_right_layouts_buttons(self) -> None:
        """
        Hide right button
        """
        self.ui.header.close_right_nav_button.hide()

    def show_right_layouts_buttons(self) -> None:
        """
        Show right button
        """
        self.ui.header.show_right_nav_button.show()
        self.ui.header.close_right_nav_button.show()

    def hide_left_layout(self) -> None:
        """
        Hide left layout
        """
        if self.ui.left_nav_widget.scroll_area_avatar.isHidden():
            self.ui.left_nav_widget.slide_out()
        else:
            self.ui.left_nav_widget.slide_in()

    def show_left_layout(self) -> None:
        """
        Show left layout
        """
        self.ui.rooms_widget.main_widget.show()
        self.ui.left_nav_widget.scroll_area_avatar.show()
        self.ui.header.close_left_nav_button.show()

    def hide_right_layout(self) -> None:
        """
        Hide right layout
        """
        if self.ui.right_nav_widget.scroll_area_dm.isHidden():
            self.ui.right_nav_widget.slide_out()
        else:
            self.ui.right_nav_widget.slide_in()

    def show_right_layout(self) -> None:
        """
        Show right layout
        """
        self.ui.right_nav_widget.scroll_area_dm.show()
        self.ui.header.close_right_nav_button.show()

    def show_footer_layout(self) -> None:
        """
        Show footer layout
        """
        self.ui.footer_widget.send_widget.show()

    def hide_footer_layout(self) -> None:
        """
        Hide footer layout
        """
        self.ui.footer_widget.send_widget.hide()

    def update_buttons(self) -> None:
        """
        Update input widgets
        """
        if self.ui.client.is_connected:
            self._set_buttons_status(False, "Enter your message to Rooms | home")
            username_label = check_str_len(self.ui.client.user_name)
            self.ui.footer_widget.user_name.setText(username_label)
        else:
            self._set_buttons_status(True, "Please login")
            self.ui.footer_widget.user_name.setText("User disconnected")
            self.ui.left_nav_widget.info_label.setText("Welcome")
            self.ui.footer_widget.user_picture.update_picture(
                status=AvatarStatus.DEACTIVATED,
                content="",
                background_color=self.theme.rgb_background_color_innactif,
            )

    def _set_buttons_status(self, activate: bool, lock_message: str) -> None:
        """
        Update buttons state

        Args:
            activate (bool): status of the button needed
            lock_message (str): message for the entry
        """
        self.ui.footer_widget.logout_button.setDisabled(activate)
        self.ui.footer_widget.entry.setDisabled(activate)
        self.ui.footer_widget.entry.setPlaceholderText(lock_message)

    # pylint: disable=line-too-long
    def add_gui_for_mp_layout(
        self, room_name: str, icon, switch_frame: Optional[bool] = False
    ) -> None:
        """
        Add GUI for a new room based on the direct message

        Args:
            room_name (str): room name
            icon (Icon): icon
            switch_frame (Optional[bool], optional): switch to direct message layout?. Defaults to False.
        """
        if room_name not in self.ui.right_nav_widget.room_list:
            # Layout
            direct_message_widget = CustomQPushButton()
            direct_message_widget.setToolTip("Open direct message")
            direct_message_widget.setFixedHeight(50)
            direct_message_widget.setStyleSheet("border: 1px solid transparent;")
            direct_message_layout = QHBoxLayout(direct_message_widget)
            direct_message_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            direct_message_layout.setSpacing(12)
            direct_message_layout.setContentsMargins(5, 0, 5, 0)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            close_button = CustomQPushButton()
            close_button.setToolTip("Close")
            close_button.clicked.connect(direct_message_widget.deleteLater)
            close_button.setFixedHeight(30)
            close_button.setFixedWidth(30)
            close_icon = QIcon(
                icon_from_svg(Icon.CLOSE.value, color=self.theme.text_color)
            )
            close_button.setIcon(close_icon)
            retain = close_button.sizePolicy()
            retain.setRetainSizeWhenHidden(True)
            close_button.setSizePolicy(retain)
            close_button.hide()

            def hover(event: QEvent, user_widget, close_button: CustomQPushButton):
                if isinstance(event, QEnterEvent):
                    color = self.theme.background_color
                else:
                    color = self.theme.inner_color
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: 8px;
                border: 0px solid transparent;
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))
                # pylint: disable=expression-not-assigned
                close_button.show() if isinstance(
                    event, QEnterEvent
                ) else close_button.hide()

            direct_message_widget.enterEvent = partial(
                hover, user_widget=direct_message_widget, close_button=close_button
            )
            direct_message_widget.leaveEvent = partial(
                hover, user_widget=direct_message_widget, close_button=close_button
            )

            partial_room_name = check_str_len(room_name)

            btn = QLabel(partial_room_name)
            self.dm_avatar_dict[room_name] = icon
            direct_message_widget.clicked.connect(
                partial(self.update_gui_for_mp_layout, room_name)
            )

            style_ = """
            QLabel {{
            text-align: left;
            font-weight: bold;
            border-radius: 8px;
            border: 0px solid transparent;
            }} 
            """
            btn.setStyleSheet(style_.format(color=self.theme.background_color))
            btn.update()
            btn.setContentsMargins(0, 0, 0, 0)

            direct_message_layout.addWidget(icon)
            direct_message_layout.addWidget(btn)
            direct_message_layout.addWidget(
                close_button, stretch=1, alignment=Qt.AlignmentFlag.AlignRight
            )
            self.ui.right_nav_widget.room_list[room_name] = direct_message_layout
            # Insert widget after the separator
            self.ui.right_nav_widget.direct_message_layout.insertWidget(
                1, direct_message_widget
            )

            # --- Add Body Scroll Area --- #
            self.ui.body_gui_dict[room_name] = BodyScrollArea(
                name=room_name, gui_controller=self
            )

            # Add new room to the messages dict
            if room_name not in self.messages_dict.keys():
                self.messages_dict[room_name] = OrderedDict()

        if switch_frame:
            self.update_gui_for_mp_layout(room_name)

    def update_gui_for_mp_layout(self, room_name: str) -> None:
        """
        Update the GUI based on the room selected

        Args:
            room_name (str): room frame
        """
        # Update reply entry
        self.ui.footer_widget.reply_entry_action.triggered.emit()

        if room_name != "home":
            # Update avatar status with iddle
            self.avatar_controller.update_pixmap_avatar(
                room_name,
                AvatarStatus.ACTIVATED
                if room_name in self.ui.users_connected.keys()
                else AvatarStatus.DEACTIVATED,
            )
            self.api_controller.update_is_readed_status(
                room_name, self.ui.client.user_name
            )
        else:
            self.room_icon.update_pixmap(
                AvatarStatus.IDLE,
                background_color=self.theme.rgb_background_color_rooms,
            )

        old_widget = self.ui.scroll_area
        old_widget.hide()

        widget = self.ui.body_gui_dict[room_name]
        index = self.ui.body_layout.indexOf(old_widget)

        self.ui.body_layout.removeWidget(old_widget)
        self.ui.body_layout.insertWidget(index, widget)

        type_room = "Rooms" if room_name == "home" else "Messages"
        self.ui.frame_name.setText(f"{type_room} \n| {room_name}")
        self.ui.frame_research.setPlaceholderText(
            f"Search in {type_room} | {room_name}"
        )
        self.ui.footer_widget.entry.setPlaceholderText(
            f"Enter your message to {type_room} | {room_name}"
        )
        self.ui.scroll_area = widget
        self.ui.scroll_area.show()
        self.ui.scroll_area.scrollToBottom()

    def fetch_all_users_username(self):
        """
        Fetch all users picture from backend
        """
        usernames: List[str] = self.ui.backend.get_all_users_username()
        for username in usernames:
            self.api_controller.add_sender_picture(username)

    def fetch_all_rooms(self):
        """
        Fetch all rooms
        """
        room_widget = CustomQPushButton()
        room_widget.setFixedHeight(50)
        room_layout = QHBoxLayout(room_widget)
        room_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        room_layout.setContentsMargins(0, 0, 0, 0)

        divider = QIcon(
            icon_from_svg(Icon.SEPARATOR_HORIZ.value, color=self.theme.background_color)
        )
        divider_label = QLabel()
        divider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider_label.setPixmap(divider.pixmap(20, 20))

        self.room_icon = AvatarLabel(
            content=ImageAvatar.ROOM.value,
            status=AvatarStatus.DEACTIVATED,
        )
        self.room_icon.setToolTip("Display home room")

        self.room_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        room_widget.clicked.connect(lambda: self.update_gui_for_mp_layout("home"))

        def hover(event: QEvent, user_widget):
            if isinstance(event, QEnterEvent):
                color = self.theme.background_color
            else:
                color = self.theme.rooms_color
            style_ = """
            QWidget {{
            font-weight: bold;
            text-align: center;
            background-color: {color};
            border-radius: 8px;
            border: 1px solid transparent;
            }} 
            """
            user_widget.setStyleSheet(style_.format(color=color))

        room_widget.enterEvent = partial(hover, user_widget=room_widget)
        room_widget.leaveEvent = partial(hover, user_widget=room_widget)

        style_ = """
            QWidget {{
            font-weight: bold;
            text-align: center;
            border: 1px solid transparent;
            }} 
            """
        room_widget.setStyleSheet(style_.format())

        room_layout.addWidget(self.room_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        self.ui.rooms_widget.main_layout.addWidget(room_widget)
        self.ui.rooms_widget.main_layout.addWidget(divider_label)

    def focus_in_message(self, message: MessageLayout) -> None:
        """
        Focus in a message

        Args:
            message (MessageLayout): message layout
        """
        style_sheet_main = message.main_widget.styleSheet()
        style_sheet_left = message.left_widget.styleSheet()

        self.update_stylesheet_with_reply(message)

        def callback(
            message: MessageLayout, style_sheet_main_: str, style_sheet_left_: str
        ) -> None:
            """
            Callback to update stylesheet

            Args:
                message (MessageLayout): message layout to update
                style_sheet_main_ (str): style sheet
                style_sheet_left_ (str): style sheet
            """
            message.main_widget.setStyleSheet(style_sheet_main_)
            message.left_widget.setStyleSheet(style_sheet_left_)
            self.is_focused = False

        self.ui.scroll_area.ensureWidgetVisible(message.main_widget)

        QTimer.singleShot(
            1000, partial(callback, message, style_sheet_main, style_sheet_left)
        )

    def update_stylesheet_with_reply(self, message: MessageLayout) -> None:
        """
        Update stylesheet with reply

        Args:
            message (MessageLayout): message layout
        """
        message.main_widget.setStyleSheet(
            f"color: {self.theme.title_color};\
            margin-bottom: 1px;\
            margin-right: 2px;\
            background-color: {self.theme.inner_color};\
            border-left: 0px solid;"
        )
        message.left_widget.setStyleSheet("border-left: 0px solid")

    def update_stylesheet_with_focus_event(
        self, message: MessageLayout, border_color: str
    ) -> None:
        """
        Update stylesheet with focus event

        Args:
            message (MessageLayout): message layout
            border_color (str): border color
        """
        message.main_widget.setStyleSheet(
            f"color: {self.theme.title_color};\
            margin-bottom: 1px;\
            margin-right: 2px;\
            background-color: {self.theme.inner_color};"
        )
        message.left_widget.setStyleSheet(
            f"""QWidget{{
                border-left: 2px solid;\
                border-color: {border_color};
            }}
            AvatarLabel{{
                border: 0px solid;
            }}"""
        )

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    def display_users_from_research(self):
        """
        Display users list from research
        """
        # Move the list under the research bar
        x = self.ui.header.frame_research.x()
        y = self.ui.header.frame_research.y() + self.ui.header.frame_research.height()
        self.ui.header.frame_research_list.move(x, y)
        self.ui.header.frame_research_list.clear()

        # Get the text from the research bar
        text_from_research = self.ui.header.frame_research.text()
        if not text_from_research:
            self.ui.header.frame_research_list.hide()
            self.ui.header.frame_research.reset_layout()
            return

        # Get all users
        users = self.ui.users_pict.keys()

        def hover(event: QEvent, user_widget) -> None:
            if isinstance(event, QEnterEvent):
                color = self.theme.background_color
            else:
                color = self.theme.search_color

            style_ = """
            QWidget {{
            background-color: {color};
            border-radius: 8px;
            border: 0px solid {color};
            }} 
            """
            user_widget.setStyleSheet(style_.format(color=color))
            user_widget.update()

        nb_users = 0
        for user in users:
            # If the user is in the research text bar
            if (
                text_from_research in user
                and user != "server"
                and user != self.ui.client.user_name
            ):
                nb_users += 1
                self.ui.header.frame_research_list.show()
                self.ui.header.frame_research.update_layout()
                user_widget = CustomQPushButton()
                content = (
                    global_variables.user_connected[user][0]
                    if user in global_variables.user_connected
                    else global_variables.user_disconnect[user][0]
                )
                dm_pic = AvatarLabel(
                    content=content,
                    status=AvatarStatus.IDLE,
                )

                def callback(user, dm_pic):
                    self.add_gui_for_mp_layout(user, dm_pic, True)
                    self.ui.header.frame_research.clear()
                    self.ui.header.frame_research_list.hide()
                    self.ui.header.frame_research.reset_layout()
                    self.ui.header.frame_research.clearFocus()

                user_widget.clicked.connect(partial(callback, user, dm_pic))
                user_widget.enterEvent = partial(hover, user_widget=user_widget)
                user_widget.leaveEvent = partial(hover, user_widget=user_widget)
                user_widget.setContentsMargins(5, 0, 0, 0)
                user_widget.setFixedHeight(30)
                user_layout = QHBoxLayout(user_widget)

                user_pic = AvatarLabel(
                    content=content, status=AvatarStatus.IDLE, height=20, width=20
                )

                user_layout.setContentsMargins(0, 0, 0, 0)
                user = check_str_len(user)
                label = QLabel(user)
                label.setStyleSheet(
                    f"font-weight: bold;\
                    background-color: transparent;\
                    color: {self.theme.title_color};"
                )
                user_layout.addWidget(user_pic)
                user_layout.addWidget(label)
                user_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                item = QListWidgetItem()
                self.ui.header.frame_research_list.addItem(item)
                self.ui.header.frame_research_list.setItemWidget(item, user_widget)
        if not nb_users:
            self.ui.header.frame_research_list.hide()
            self.ui.header.frame_research.reset_layout()

        self.ui.header.frame_research_list.setFixedHeight(50 * 3 if nb_users > 0 else 0)

    def hide_research(self, event, hide_research) -> None:
        """
        Hide research bar

        Args:
            event (QEvent): event
            hide_research (Callable): callback
        """
        hide_research(event)
        if self.ui.header.frame_research_list.hasFocus():
            return
        self.ui.header.frame_research.clear()
        self.ui.header.frame_research_list.hide()
        self.ui.header.frame_research.reset_layout()

    def display_theme_board(self):
        """
        Display theme board
        """
        if self.theme_board and self.theme_board.isVisible():
            return
        self.theme_board = QWidget()

        height = 250
        self.theme_board.setFixedSize(QSize(240, height))
        self.theme_board.move(
            self.ui.footer_widget.bottom_right_widget.x() + 5,
            self.ui.footer_widget.send_widget.y()
            - height
            + self.ui.footer_widget.bottom_right_widget.height()
            - 5,
        )
        self.theme_board.setContentsMargins(0, 0, 0, 0)
        self.theme_board.setStyleSheet(
            f"background-color: {self.theme.background_color};\
            border-radius: 8px;\
            border: 1px solid {self.theme.nav_color};"
        )
        theme_board_layout = QVBoxLayout(self.theme_board)
        theme_board_layout.setContentsMargins(15, 15, 15, 15)
        theme_board_layout.setSpacing(5)
        list_theme_label = [
            QLabel(color_name.capitalize().replace("_color", ""))
            for color_name in self.theme.list_colors
        ]
        list_theme_line_edit = [
            CustomQLineEdit(
                text=getattr(self.theme, self.theme.list_colors[i]),
                place_holder_text="#",
                radius=4,
            )
            for i in range(len(list_theme_label))
        ]

        for label in list_theme_label:
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setStyleSheet(
                f"color: {self.theme.title_color};\
                font-weight: bold;\
                border: 0px solid"
            )
        for line_edit in list_theme_line_edit:
            line_edit.setFixedSize(QSize(120, 15))
            line_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        for label, line_edit in zip(list_theme_label, list_theme_line_edit):
            widget = QWidget()
            widget.setStyleSheet("border: 0px solid;")
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 0, 5, 0)
            layout.setSpacing(0)
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(line_edit, alignment=Qt.AlignmentFlag.AlignLeft)
            theme_board_layout.addWidget(widget)

        # Update layout
        update_widget = QWidget()
        update_widget.setStyleSheet(
            f"border: 0px solid;\
            background-color: {self.theme.search_color};"
        )
        update_layout = QHBoxLayout(update_widget)
        update_layout.setContentsMargins(5, 5, 5, 5)

        # Update theme button
        theme_icon = QIcon(
            icon_from_svg(Icon.SWITCH_COLOR.value, color=self.theme.title_color)
        )
        update_button = self._create_theme_button(" Custom", 80, 40, theme_icon)
        update_button.clicked.connect(
            partial(self.theme.create_custom_theme, self, list_theme_line_edit)
        )
        # Black theme
        black_icon = QIcon(icon_from_svg(Icon.STATUS.value, color="#000000"))
        black_theme_button = self._create_theme_button("", 30, 30, black_icon)
        black_theme_button.clicked.connect(
            partial(self.theme.switch_theme, self, Themes.ThemeColor.BLACK)
        )

        # White theme
        white_icon = QIcon(icon_from_svg(Icon.STATUS.value, color="#ffffff"))
        white_theme_button = self._create_theme_button("", 30, 30, white_icon)
        white_theme_button.clicked.connect(
            partial(self.theme.switch_theme, self, Themes.ThemeColor.WHITE)
        )
        # close button
        close_icon = QIcon(
            icon_from_svg(Icon.CLOSE.value, color=GenericColor.RED.value)
        )
        close_button = self._create_theme_button("", 30, 30, close_icon)
        close_button.clicked.connect(self.theme_board.hide)

        update_layout.addWidget(update_button)
        update_layout.addWidget(black_theme_button)
        update_layout.addWidget(white_theme_button)
        update_layout.addWidget(close_button)

        theme_board_layout.addWidget(update_widget)

        self.ui.main_layout.addChildWidget(self.theme_board)
        self.theme_board.setFocus()

    def _create_theme_button(
        self, text: str, w: int, h: int, icon: QIcon
    ) -> CustomQPushButton:
        """
        Create theme button

        Args:
            text (str): button text
            w (int): width
            h (int): height
            icon (QIcon): Icon

        Returns:
            CustomQPushButton: button
        """
        result = CustomQPushButton(text)
        result.setFixedSize(QSize(w, h))
        result.setIcon(icon)

        return result
