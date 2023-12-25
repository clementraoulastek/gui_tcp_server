import contextlib
from typing import Callable
from src.client.controller.api_controller import ApiStatus
from src.client.view.custom_widget.custom_avatar_label import AvatarStatus
from src.client.view.layout.login_layout import LoginLayout
from src.client.core.qt_core import Qt
from src.tools.commands import Commands
import src.client.controller.global_variables as global_variables

class ConnectionController:
    def __init__(self, parent, ui):
        self.ui = ui
        self.parent = parent
    
    def login(self) -> None:
        """
        Display the login form
        """
        self.parent.clear()
        if not hasattr(self.ui, "login_form") or not self.ui.login_form:
            self.ui.login_form = LoginLayout(theme=self.parent.theme)
            self.ui.scroll_area.main_layout.addLayout(self.ui.login_form)
            self.ui.scroll_area.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            # Connect signals
            self.ui.login_form.password_entry.returnPressed.connect(
                lambda: self.login_form(self.parent.api_controller.send_login_form)
            )
            self.ui.login_form.username_entry.returnPressed.connect(
                lambda: self.login_form(self.parent.api_controller.send_login_form)
            )
            self.ui.login_form.send_action.triggered.connect(
                lambda: self.login_form(self.parent.api_controller.send_form, self.ui.backend.send_login_form)
            )
            self.ui.login_form.entry_action.triggered.connect(
                lambda: self.login_form(self.parent.api_controller.send_form, self.ui.backend.send_register_form)
            )
            
    def login_form(self, callback: Callable, backend_callback: Callable) -> None:
        """
        Update the layout if login succeed
        """
        status = callback(backend_callback)
        if status == ApiStatus.SUCCESS:
            self.handle_sucess_gui_conn()
        elif status == ApiStatus.FORBIDDEN:
            self.ui.login_form.error_label.setText("Error: Empty username or password")
        elif status == ApiStatus.ERROR:
            self.ui.login_form.error_label.setText(
                "Error: Username or password incorect"
            )
        else:
            self.ui.login_form.error_label.setText(
                "Enable to join the server, please try again later"
            )
            
    def handle_sucess_gui_conn(self):
        """
        Show GUI panels if login succeed
        """
        self.clean_gui_and_connect(update_avatar=True)
        self.parent.show_left_layout()
        self.parent.show_right_layout()
        self.parent.show_footer_layout()
        self.ui.upper_widget.show()
        self.ui.header.frame_research.show()
        self.ui.header.frame_research.clearFocus()
        self.ui.header.avatar.height_, self.ui.header.avatar.width_ = 20, 20
        self.ui.header.avatar.update_picture(
            status=AvatarStatus.ACTIVATED,
            content=self.ui.users_pict[self.ui.client.user_name],
        )
        self.ui.header.avatar.show()
        self.ui.header.welcome_label.setText(f"{self.ui.client.user_name}")
        self.ui.header.welcome_label.show()
        self.ui.header.separator.show()

        # Signal
        self.ui.header.frame_research.textChanged.connect(
            self.parent.display_users_from_research
        )
        hide_research = self.ui.header.frame_research.focusOutEvent
        self.ui.header.frame_research.focusOutEvent = lambda e: self.parent.hide_research(
            e, hide_research
        )
        
    def clean_gui_and_connect(self, update_avatar: bool) -> None:
        """
        Clean GUI

        Args:
            update_avatar (bool): update user avatar
        """
        self.ui.users_connected[self.ui.client.user_name] = True

        if self.parent.tcp_controller.is_connected_to_server():
            self.parent.init_working_signals()
            self.ui.client.send_data(Commands.HELLO_WORLD, Commands.HELLO_WORLD.name)
            self.ui.login_form = None
            self.parent.clear()
            self.parent.api_controller.get_user_icon(update_personal_avatar=update_avatar)
            self.ui.left_nav_widget.info_disconnected_label.show()
            self.parent.fetch_all_users_username()
            self.parent.fetch_all_rooms()

            # Get older messages from the server
            dm_list = self.parent.messages_controller.get_all_dm_users_username()["usernames"]

            last_message_id = self.parent.api_controller.get_last_message_id()

            # In case of empty database
            if last_message_id:
                last_message_id = int(last_message_id)
            else:
                return
            NB_OF_MESSAGES = 20
            for dm in dm_list:
                self.parent.messages_controller.fetch_older_messages(
                    start=last_message_id + 1, number=NB_OF_MESSAGES, username=dm
                )

            self.ui.footer_widget.reply_entry_action.triggered.connect(lambda: None)
            
    def logout(self) -> None:
        """
        Disconnect the client
        """
        # Update backend connection status
        self.parent.api_controller.send_login_status(
            username=self.ui.client.user_name, status=False
        )
        self.parent.api_controller.is_connected = False

        # Socket disconnection
        self.ui.client.close_connection()

        # Update the gui with home layout for reconnection
        self.parent.update_gui_for_mp_layout("home")

        # Dict clear
        global_variables.user_connected.clear()
        global_variables.user_disconnect.clear()
        self.ui.users_pict.clear()
        self.ui.users_connected.clear()
        self.parent.dm_avatar_dict.clear()
        self.ui.right_nav_widget.room_list.clear()
        self.parent.messages_dict.clear()

        # UI update
        self.parent.update_buttons()
        self.parent.avatar_controller.clear_avatar("user_inline", self.ui.left_nav_widget)
        self.parent.avatar_controller.clear_avatar("user_offline", self.ui.left_nav_widget)
        self.parent.avatar_controller.clear_avatar("main_layout", self.ui.rooms_widget, delete_all=True)
        self.parent.avatar_controller.clear_avatar("direct_message_layout", self.ui.right_nav_widget)
        
        with contextlib.suppress(RuntimeError):
            self.ui.footer_widget.reply_entry_action.triggered.disconnect()
            
        self.ui.header.frame_research.hide()
        self.ui.header.welcome_label.hide()
        self.ui.header.separator.hide()
        self.ui.header.avatar.hide()
        self.ui.rooms_widget.main_widget.hide()

        self.ui.left_nav_widget.info_disconnected_label.hide()
        self.ui.upper_widget.hide()
        
        self.login()