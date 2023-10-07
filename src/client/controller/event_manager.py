from src.client.core.qt_core import QObject, Signal

class EventManager(QObject):
    
    coming_message_signal = Signal()
    users_connected_signal = Signal()
    users_disconnected_signal = Signal()
    react_message_signal = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        
    def event_coming_message(self) -> None:
        self.coming_message_signal.emit()
    
    def event_users_connected(self) -> None:
        self.users_connected_signal.emit()
    
    def event_users_disconnected(self) -> None:
        self.users_disconnected_signal.emit()
    
    def event_react_message(self) -> None:
        self.react_message_signal.emit()