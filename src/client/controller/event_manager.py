"""Event manager for client."""

from PySide6.QtCore import QObject, Signal


class EventManager(QObject):
    """
    EventManager class.

    Args:
        QObject (QObject): the QObject class
    """

    coming_message_signal = Signal()
    users_connected_signal = Signal()
    users_disconnected_signal = Signal()
    react_message_signal = Signal()

    def event_coming_message(self) -> None:
        """
        Emit a signal when a message is coming.
        """
        self.coming_message_signal.emit()

    def event_users_connected(self) -> None:
        """
        Emit a signal when users are connected.
        """
        self.users_connected_signal.emit()

    def event_users_disconnected(self) -> None:
        """
        Emit a signal when users are disconnected.
        """
        self.users_disconnected_signal.emit()

    def event_react_message(self) -> None:
        """
        Emit a signal when a message is reacted.
        """
        self.react_message_signal.emit()
