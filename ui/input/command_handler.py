"""Command handler for slash commands like /exit, /reload, /settings."""

from typing import Callable
from ..logger import Logger
from ..events import EventBus, Events

logger = Logger.get_instance()


class CommandHandler:
    """Handles slash commands in input fields."""

    COMMANDS = {"/exit": Events.EXIT, "/reload": Events.RELOAD, "/settings": Events.SETTINGS}

    def __init__(self):
        """Initialize command handler."""
        pass

    def try_execute(self, text: str, clear_callback: Callable = None) -> bool:
        """
        Check if text is a command and execute it.

        Args:
            text: Input text to check
            clear_callback: Optional callback to clear input field

        Returns:
            True if command was handled, False otherwise
        """
        command = text.strip().lower()
        if command in self.COMMANDS:
            event = self.COMMANDS[command]
            logger.info(f"{command[1:].capitalize()} command detected")
            # Clear input for non-exit commands
            if clear_callback and command != "/exit":
                clear_callback()
            EventBus.publish(event)
            return True
        return False
