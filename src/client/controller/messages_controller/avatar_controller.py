from functools import partial
from typing import List, Optional, Union

from src.client.view.custom_widget.custom_avatar_label import AvatarLabel, AvatarStatus
import src.client.controller.global_variables as global_variables
from src.client.view.custom_widget.custom_button import CustomQPushButton
from src.client.core.qt_core import QHBoxLayout, Qt, QEvent, QEnterEvent, QLabel, QLayout, QWidget
from src.tools.utils import check_str_len

class AvatarController:
    def __init__(self, parent, ui, dm_avatar_dict: dict):
        self.parent = parent
        self.ui = ui
        self.dm_avatar_dict = dm_avatar_dict
    
    def remove_sender_avatar(
        self,
        payload: str,
        user_connected: dict[str, List[Union[str, bool]]],
        user_disconnect: dict[str, List[Union[str, bool]]],
    ) -> None:
        """
        Remove the user icon from the connected layout from a GOOD BYE message

        Args:
            payload (str): payload of the command
            user_connected (dict[str, List[Union[str, bool]]]): dict of connected users
            user_disconnect (dict[str, List[Union[str, bool]]]): dict of disconnected users
        """
        id_, _ = payload.split(":", 1)
        self.clear_avatar("user_inline", self.ui.left_nav_widget, f"{id_}_layout")
        self.parent.api_controller.add_sender_picture(id_)
        user_disconnect[id_] = [user_connected[id_][0], False]
        self.ui.users_connected.pop(id_)

        if (
            id_ in self.dm_avatar_dict.keys()
            and self.dm_avatar_dict[id_].status != AvatarStatus.DM
        ):
            self.dm_avatar_dict[id_].update_pixmap(AvatarStatus.DEACTIVATED)

        self.parent.event_manager.event_users_disconnected()

    def add_sender_avatar(
        self, payload: str, user_disconnect: dict[str, List[Union[str, bool]]]
    ) -> None:
        """
        Add the user icon to the connected layout from a HELLO WORLD or WELCOME message

        Args:
            payload (str): payload of the command
            user_disconnect (dict[str, List[Union[str, bool]]]): dict of disconnected users
        """
        id_, _ = payload.split(":", 1)

        # In case of new user not register before
        if id_ not in self.ui.users_pict.keys():
            self.parent.api_controller.add_sender_picture(id_)

        # Remove user's icon disconnected from the disconnected layout
        if id_ in user_disconnect:
            self.clear_avatar(
                "user_offline", self.ui.left_nav_widget, f"{id_}_layout_disconnected"
            )
            user_disconnect.pop(id_)

        if (
            id_ in self.dm_avatar_dict.keys()
            and self.dm_avatar_dict[id_].status != AvatarStatus.DM
        ):
            self.dm_avatar_dict[id_].update_pixmap(AvatarStatus.ACTIVATED)

        # Add the user icon to the connected layout
        if id_ not in self.ui.users_connected.keys():
            self.ui.users_connected[id_] = True
            self.parent.api_controller.update_user_connected(id_, self.ui.users_pict[id_])

        self.parent.event_manager.event_users_connected()
        
    def update_gui_with_connected_avatar(self) -> None:
        """
        Callback to update gui with input connected avatar
        """
        user_connected_dict = global_variables.user_connected.copy()

        for user, data in user_connected_dict.items():
            if data[1] == True:
                continue
            global_variables.user_connected[user] = [data[0], True]
            # Layout
            user_widget = CustomQPushButton()
            user_widget.setFixedHeight(50)
            user_widget.setStyleSheet("border: none")
            user_layout = QHBoxLayout(user_widget)
            user_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            user_layout.setSpacing(10)
            user_layout.setContentsMargins(5, 0, 0, 0)
            username = user
            user_layout.setObjectName(f"{username}_layout")
            content = data[0]

            def hover(event: QEvent, user_widget):
                if isinstance(event, QEnterEvent):
                    color = self.parent.theme.background_color
                    user_pic.update_pixmap(
                        AvatarStatus.ACTIVATED,
                        background_color=self.parent.theme.rgb_background_color_innactif,
                    )
                else:
                    color = self.parent.theme.inner_color
                    user_pic.update_pixmap(
                        AvatarStatus.ACTIVATED,
                        background_color=self.parent.theme.rgb_background_color_actif,
                    )
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: 8px;
                border: 1px solid {color};
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))

            # Create avatar label
            user_pic, dm_pic = AvatarLabel(
                content=content,
                status=AvatarStatus.ACTIVATED,
                background_color=self.parent.theme.rgb_background_color_actif,
            ), AvatarLabel(
                content=content,
                status=AvatarStatus.ACTIVATED,
                background_color=self.parent.theme.rgb_background_color_actif,
            )

            # Update picture alignment
            user_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dm_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_pic.setStyleSheet("border: 0px;")

            # Avoid gui troubles with bigger username
            username_label = check_str_len(username)
            user_name = QLabel(username_label)

            if (
                username in self.dm_avatar_dict.keys()
                and self.dm_avatar_dict[username].status != AvatarStatus.DM
            ):
                self.dm_avatar_dict[username].update_pixmap(
                    AvatarStatus.ACTIVATED,
                    background_color=self.parent.theme.rgb_background_color_actif,
                )

            # StyleSheet
            style_ = """
            QLabel {{
            text-align: left;
            font-weight: bold;
            border-radius: 8px;
            border: 1px solid;
            border-color: transparent;
            }} 
            """
            # Add user menu
            if username != self.ui.client.user_name:
                user_widget.setToolTip("Open direct message")
                user_widget.enterEvent = partial(hover, user_widget=user_widget)
                user_widget.leaveEvent = partial(hover, user_widget=user_widget)

                user_widget.clicked.connect(
                    partial(self.parent.add_gui_for_mp_layout, username, dm_pic, True)
                )
                hover_ = """
                QPushButton:hover {{
                text-decoration: underline;
                }}
                """
                style_ = f"{style_}{hover_}"
            user_name.setStyleSheet(style_.format(color=self.parent.theme.background_color))

            # Add widgets to the layout
            user_layout.addWidget(user_pic)
            user_layout.addWidget(user_name)
            self.ui.left_nav_widget.user_inline.insertWidget(1, user_widget)
            self.ui.left_nav_widget.user_inline.update()
            
    def update_gui_with_disconnected_avatar(self) -> None:
        """
        Callback to update gui with input disconnected avatar
        """
        user_disconnected_dict = global_variables.user_disconnect.copy()

        for user, data in user_disconnected_dict.items():
            if data[1] == True:
                continue
            # Layout
            user_widget = CustomQPushButton()
            user_widget.setToolTip("Open direct message")
            user_widget.setFixedHeight(50)
            style_ = """
            QWidget {{
            border-radius: 8px;
            border: 0px solid {color};
            }} 
            """

            def hover(event: QEvent, user_widget, user_pic: AvatarLabel):
                if isinstance(event, QEnterEvent):
                    color = self.parent.theme.background_color
                    user_pic.graphicsEffect().setEnabled(False)
                    user_pic.update_pixmap(
                        AvatarStatus.DEACTIVATED,
                        background_color=self.parent.theme.rgb_background_color_innactif,
                    )
                else:
                    color = self.parent.theme.inner_color
                    user_pic.graphicsEffect().setEnabled(True)
                    user_pic.update_pixmap(
                        AvatarStatus.DEACTIVATED,
                        background_color=self.parent.theme.rgb_background_color_actif,
                    )
                style_ = """
                QWidget {{
                background-color: {color};
                border-radius: 8px;
                border: 0px solid {color};
                }} 
                """
                user_widget.setStyleSheet(style_.format(color=color))
                user_widget.update()

            user_widget.setStyleSheet(style_.format(color=self.parent.theme.background_color))
            user_widget.setContentsMargins(0, 0, 0, 0)

            user_layout = QHBoxLayout(user_widget)
            user_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            user_layout.setSpacing(10)
            user_layout.setContentsMargins(5, 0, 0, 0)
            username = user
            content = data[0]
            user_layout.setObjectName(f"{username}_layout_disconnected")

            # Create avatar label
            user_pic, dm_pic = AvatarLabel(
                content=content,
                status=AvatarStatus.DEACTIVATED,
            ), AvatarLabel(content=content, status=AvatarStatus.DEACTIVATED)

            user_widget.enterEvent = partial(
                hover, user_widget=user_widget, user_pic=user_pic
            )
            user_widget.leaveEvent = partial(
                hover, user_widget=user_widget, user_pic=user_pic
            )

            # Update picture
            user_pic.set_opacity(0.2)
            user_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dm_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_pic.setStyleSheet(
                f"border: 0px solid;\
                border-color: {self.parent.theme.background_color};"
            )

            # Avoid gui troubles with bigger username
            username_label = check_str_len(username)
            user_name = QLabel(username_label)
            user_name.setContentsMargins(0, 0, 0, 0)

            # Add user menu
            user_widget.clicked.connect(
                partial(self.parent.add_gui_for_mp_layout, username, dm_pic, True)
            )
            style_ = """
            QLabel {{
            text-align: left;
            font-weight: bold;
            border-radius: 8px;
            border: 1px solid;
            border-color: {color};
            }}
            """
            user_name.setStyleSheet(style_.format(color="transparent"))

            # Add widgets to the layout
            user_layout.addWidget(user_pic)
            user_layout.addWidget(user_name)
            self.ui.left_nav_widget.user_offline.insertWidget(1, user_widget)
            self.ui.left_nav_widget.user_offline.update()

            global_variables.user_disconnect[user] = [data[0], True]

        self.ui.left_nav_widget.info_disconnected_label.setText(
            f"Users offline   |   {len(global_variables.user_disconnect)}"
        )
        
    def clear_avatar(
        self,
        parent_layout: QLayout,
        parent=None,
        layout_name: Optional[Union[QHBoxLayout, None]] = None,
        delete_all: Optional[bool] = False,
    ) -> None:
        """
        Clear avatars or all widgets from the layout

        Args:
            parent_layout (QLayout): parent layout
            layout_name (Optional[Union[QHBoxLayout, None]], optional): layout name. Defaults to None.
            delete_all (Optional[bool], optional): delete all widgets. Defaults to False.
        """
        for i in reversed(range(getattr(parent or self.ui, parent_layout).count())):
            if widget := getattr(parent or self.ui, parent_layout).itemAt(i).widget():
                widget: QWidget
                if type(widget) != CustomQPushButton and not delete_all:
                    continue
                layout = widget.layout()
                if not layout:
                    widget.setParent(None)
                    widget.deleteLater()
                    continue
                if (
                    layout_name
                    and layout_name == layout.objectName()
                    or not layout_name
                ):
                    layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()

        getattr(parent or self.ui, parent_layout).update()
        
    def update_pixmap_avatar(self, room_name: str, status: AvatarStatus) -> None:
        """
        Update pixmap avatar

        Args:
            room_name (str): room frame
            status (AvatarStatus): status needed
        """
        self.dm_avatar_dict[room_name].update_pixmap(status)