"""Event bus for decoupled component communication."""

from typing import Callable, Dict, List, Any
from .logger import Logger

logger = Logger.get_instance()


class Events:
    """Event type constants."""
    SEARCH = 'search'
    SELECT = 'select'
    ACTION = 'action'
    HIDE = 'hide'
    RESET = 'reset'
    SHOW_INITIAL = 'show_initial'
    HIGHLIGHT_CHANGE = 'highlight_change'
    ACTION_HIGHLIGHT_CHANGE = 'action_highlight_change'
    DELETE_ENTRY = 'delete_entry'
    EXIT = 'exit'
    RELOAD = 'reload'
    SETTINGS = 'settings'
    FILTER = 'filter'


class EventBus:
    """Simple event bus for publish/subscribe pattern."""

    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event: str, callback: Callable) -> None:
        """Subscribe to an event.

        Args:
            event: Event type from Events class
            callback: Function to call when event is published
        """
        if event not in cls._listeners:
            cls._listeners[event] = []
        if callback not in cls._listeners[event]:
            cls._listeners[event].append(callback)
            logger.debug(f"EventBus: Subscribed to {event}")

    @classmethod
    def unsubscribe(cls, event: str, callback: Callable) -> None:
        """Unsubscribe from an event.

        Args:
            event: Event type
            callback: Function to remove
        """
        if event in cls._listeners and callback in cls._listeners[event]:
            cls._listeners[event].remove(callback)
            logger.debug(f"EventBus: Unsubscribed from {event}")

    @classmethod
    def publish(cls, event: str, data: Any = None) -> None:
        """Publish an event to all subscribers.

        Args:
            event: Event type
            data: Optional data to pass to callbacks
        """
        logger.debug(f"EventBus: Publishing {event}")
        if event in cls._listeners:
            for callback in cls._listeners[event]:
                try:
                    if data is not None:
                        callback(data)
                    else:
                        callback()
                except Exception as e:
                    logger.error(f"EventBus: Error in callback for {event}: {e}")

    @classmethod
    def clear(cls) -> None:
        """Clear all subscriptions."""
        cls._listeners.clear()
        logger.debug("EventBus: Cleared all subscriptions")

    @classmethod
    def clear_event(cls, event: str) -> None:
        """Clear all subscriptions for a specific event."""
        if event in cls._listeners:
            cls._listeners[event].clear()
            logger.debug(f"EventBus: Cleared subscriptions for {event}")
