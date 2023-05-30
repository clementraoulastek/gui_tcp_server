# create a gui in tkinter
import contextlib
import datetime
import functools
import logging
import signal
from threading import Thread
import tkinter
from client.client import Client
import customtkinter
from other.constant import PORT_NB, IP_SERVER
from other.utils import get_scaled_icon, Icon, Color
from datetime import datetime
import time 

class Gui:
    def __init__(self, title, root=None):
        self.extend_root = root or None
        self.root = tkinter.Toplevel(root) if self.extend_root else tkinter.Tk()
        self.root.title(title)
        self.root.geometry("300x600")
        self.root.resizable(False, False)
        
        # Init signal
        self.root.bind('<Return>', self.send)
        self.root.protocol('WM_DELETE_WINDOW', self.close_connection)
        self.root.bind('<Control-q>', self.close_connection)
        signal.signal(signal.SIGINT, self.close_connection)

        main_panel = tkinter.PanedWindow(self.root)
        main_panel.pack(fill=tkinter.BOTH, expand=True)

        main_frame = customtkinter.CTkFrame(main_panel)
        main_frame.pack(fill=tkinter.BOTH, expand=True)

        self.icon_status_server = get_scaled_icon(Icon.STATUS.value)
        self.status_server = customtkinter.CTkLabel(
            main_frame,
            text = "Status Server",
            compound="left",
            fg_color=Color.LIGHT_GREY.value,
            text_color=Color.GREY.value,
            font = ("Arial", 12, "bold"),
            image=self.icon_status_server
        )
        self.status_server.pack(fill=tkinter.BOTH, expand=True)
        
        self.scrolled_text = customtkinter.CTkTextbox(main_frame, state="disabled", height=450)
        self.scrolled_text.pack(fill=tkinter.BOTH, expand=True)
        self.scrolled_text.tag_config('server', foreground=Color.BLUE.value)
        self.scrolled_text.tag_config('client', foreground=Color.LIGHT_GREY.value)
        self.scrolled_text.tag_config('id', foreground=Color.WHITE.value)

        button_frame = tkinter.Frame(main_frame)
        button_frame.pack(fill=tkinter.BOTH, expand=True)

        self.icon_clear = get_scaled_icon(Icon.CLEAR.value)
        clear_button = customtkinter.CTkButton(
            button_frame,
            text="Clear",
            command=self.clear,
            image=self.icon_clear,
            fg_color = Color.LIGHT_GREY.value,
            hover_color = Color.BLUE.value,
            text_color = Color.GREY.value,
            font = ("Arial", 12, "bold"),
            width = 70
        )
        clear_button.pack(expand=True, side=tkinter.LEFT)

        self.icon_login = get_scaled_icon(Icon.LOGIN.value)
        self.login_button = customtkinter.CTkButton(
            button_frame,
            text="Login",
            command=self.login,
            image=self.icon_login,
            fg_color = Color.LIGHT_GREY.value,
            hover_color = Color.BLUE.value,
            text_color = Color.GREY.value,
            font = ("Arial", 12, "bold"),
            width = 70
        )
        self.login_button.pack(expand=True, side=tkinter.LEFT)
        
        self.icon_logout = get_scaled_icon(Icon.LOGOUT.value)
        self.logout_button = customtkinter.CTkButton(
            button_frame,
            text="Logout",
            command=self.logout,
            image=self.icon_logout,
            fg_color = Color.LIGHT_GREY.value,
            hover_color = Color.BLUE.value,
            text_color = Color.GREY.value,
            font = ("Arial", 12, "bold"),
            width = 70
        )
        self.logout_button.pack(expand=True, side=tkinter.LEFT)
        self.logout_button.configure(state="disabled")
        
        self.icon_config = get_scaled_icon(Icon.CONFIG.value)
        self.config_button = customtkinter.CTkButton(
            button_frame,
            text="",
            command=self.config,
            image=self.icon_config,
            fg_color = Color.LIGHT_GREY.value,
            hover_color = Color.BLUE.value,
            text_color = Color.GREY.value,
            font = ("Arial", 12, "bold"),
            width = 50
        )
        self.config_button.pack(expand=True, side=tkinter.RIGHT)

        self.entry = customtkinter.CTkEntry(
            main_frame,
            placeholder_text="Tape message here",
        )
        self.entry.pack(fill=tkinter.BOTH, expand=True)

        self.icon_send = get_scaled_icon(Icon.SEND.value)
        send_button = customtkinter.CTkButton(
            main_frame,
            text="Send message",
            command=functools.partial(self.send, 0),
            image=self.icon_send,
            fg_color = Color.LIGHT_GREY.value,
            hover_color = Color.BLUE.value,
            text_color = Color.GREY.value,
            font = ("Arial", 12, "bold")
        )
        send_button.pack(fill=tkinter.BOTH, expand=True, pady=5)

        self.client = Client(IP_SERVER, PORT_NB, title)
        self.update_login = False

    def start(self):
        self.root.mainloop()
        
    def close_connection(self, *args):
        """
            Close the socket and destroy the gui
        """
        # close the connection
        if hasattr(self.client, 'sock'):
            self.client.sock.close()
            # close the socket
            logging.debug("Client disconnected")
        else:
            logging.debug("GUI closed")
        self.root.destroy()
                
    def send(self, signal):
        """
            Send message to the server

        Args:
            signal (event): event coming from signal
        """
        if message := self.entry.get():
            if self.update_login:
                self._diplay_message_and_clear('Login updated: ', message, is_from_server=True)
                self.client.user_name = message
                self.update_login = False
                self.root.title(message)
            else:
                self.client.send_data(message, is_from_server=False)
                date_time_now = datetime.now()
                dt_string = date_time_now.strftime("%d/%m/%Y %H:%M:%S")
                self._diplay_message_and_clear("Date: ", dt_string, is_from_server=False)
                self._diplay_message_and_clear('me: ', message, is_from_server=False, doubleReturn=True)

    def _diplay_message_and_clear(self, id_sender, message, is_from_server, doubleReturn=False):
        """
            Display message on gui and clear the entry

        Args:
            id_sender (str): id from the sender
            message (str): message to display
            is_from_server (bool): is msg coming from server
            doubleReturn (bool, optional): if double return needed. Defaults to False.
        """
        self.scrolled_text.configure(state='normal')
        if id_sender != 'Date: ':
            self.scrolled_text.insert(
                tkinter.END,
                f"{id_sender}",
                'id'
            )
        self.scrolled_text.insert(
            tkinter.END,
            f"{message}\n\n" if doubleReturn else f"{message}\n",
            'server' if is_from_server else 'client'
        )
        self.scrolled_text.see("end")
        self.entry.delete(0, tkinter.END)
        self.scrolled_text.configure(state='disabled')
    
    def _display_message(self, message:str, is_from_server, doubleReturn=False):
        """
            Display message on gui and clear the entry

        Args:
            message (str): message to display
            is_from_server (bool): is msg coming from server
            doubleReturn (bool, optional): if double return needed. Defaults to False.
        """
        self.scrolled_text.configure(state='normal')
        if ":" in message and "Date" not in message:
            id, message = message.split(":", 1)
            self.scrolled_text.insert(
                tkinter.END,
                f'{id}:',
                "id"
            )
        self.scrolled_text.insert(
            tkinter.END,
            message+"\n\n" if doubleReturn else message+"\n",
            'server' if is_from_server else 'client'
        )
        self.scrolled_text.see("end")
        self.scrolled_text.configure(state='disabled')
   
    def read(self):
        """
            Read message comming from server
        """
        with contextlib.suppress(Exception):
            while self.client.is_connected:
                message, is_from_server = self.client.read_data()
                if message:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    self._display_message(f"Date: {dt_string}", is_from_server=False)
                    self._display_message(message, is_from_server, doubleReturn=True)
                time.sleep(0.1)
        
    def clear(self):
        """
            Clear the entry
        """
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.delete(1.0, tkinter.END)
        self.scrolled_text.configure(state='disabled')
    
    def login(self):
        """
            Init the connection to the server
        """
        self.client.init_connection()
        Thread(target=self.read, daemon=True).start()
        self.login_button.configure(state="disabled")
        self.logout_button.configure(state="normal")
    
    def logout(self):
        """
            Disconnect the client
        """
        self.logout_button.configure(state="disabled")
        self.login_button.configure(state="normal")
        self.client.close_connection()
        
    def config(self):
        """
            Display the config 
        """
        self.scrolled_text.configure(state='normal')
        config = f"User name = '{self.client.user_name}'\nClient host = '{self.client.host}'\nClient port = '{self.client.port}'\n\n"
        
        self.scrolled_text.insert(
            tkinter.END,
            config,
            'server'
        )
        self.scrolled_text.configure(state='disabled')

    
