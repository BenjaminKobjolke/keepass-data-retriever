import tkinter as tk
from typing import Any, Callable
from .action_buttons import ActionButtons
from .keyboard_handler import KeyboardHandler
from .logger import Logger
from .state_manager import StateManager

# Get logger instance
logger = Logger.get_instance()


class EntryActionsHandler:
    """Handles actions for selected entries"""

    def __init__(
        self,
        root: tk.Tk,
        main_frame: tk.Frame,
        state_manager: StateManager,
        on_action: Callable,
        window_relations_manager: Any,
        hide_callback: Callable,
    ):
        """Initialize the entry actions handler"""
        self.root = root
        self.main_frame = main_frame
        self.state_manager = state_manager
        self.on_action = on_action
        self.window_relations_manager = window_relations_manager
        self.hide_callback = hide_callback
        self.actions = None
        self.keyboard_handler = KeyboardHandler()

    def handle_action(self, action: str, entry: Any = None):
        """Handle action request"""
        if not entry:
            logger.warning("No entry selected")
            return

        # Log the entry selection
        try:
            self.window_relations_manager.log_entry_selection(entry)
        except Exception as e:
            logger.error(f"Error logging entry selection: {e}")

        logger.debug(f"Handling action: {action}")

        if action.startswith("type_"):
            # For paste actions, get the text first
            base_action = action.replace("type_", "")
            # Hide window first
            self.hide_callback()
            # Schedule the paste operation
            text_to_type = entry.username
            if base_action == "password":
                text_to_type = entry.password
            self.root.after(1000, lambda: self.keyboard_handler.type_text(text_to_type))
        elif action == "auto_type":
            # Auto type username and password
            self.hide_callback()
            self.root.after(
                1000, lambda: self.keyboard_handler.type_credentials(entry.username, entry.password)
            )
        else:
            # Normal copy/open actions
            self.on_action(action, entry)  # Pass the entry along
            self.hide_callback()

    def show_selected_entry(self, entry: Any, skip_state_transition=False):
        """Show selected entry with action buttons"""
        # Ensure we have a valid entry
        if not entry:
            logger.warning("Cannot show actions for null entry")
            return

        logger.debug(f"Showing actions for entry: {entry.title}")

        # Clean up existing action buttons
        if self.actions:
            self.actions.hide()
            self.actions = None

        # Create action buttons for the selected entry
        self.actions = ActionButtons(
            self.main_frame,
            lambda action: self.handle_action(action, entry),
            entry,
            self.state_manager,
        )
        self.actions.show()

    def handle_highlight_change(self, direction: str):
        """Handle highlight change in action buttons"""
        if not self.actions:
            return

        # Use the ActionButtons' highlight change handler
        self.actions.handle_highlight_change(direction)

    def handle_return_key(self, entry: Any):
        """Handle Return key in action mode - auto-fill username and password"""
        if not entry:
            return False

        # Hide the window first
        self.hide_callback()

        # Schedule the typing operation with a delay
        self.root.after(
            1000, lambda: self.keyboard_handler.type_credentials(entry.username, entry.password)
        )
        return True

    def handle_action_return(self, current_entry: Any):
        """Handle Return key when in action mode"""
        if not self.actions or not current_entry:
            return False

        # Get the currently highlighted action
        current_index = self.actions.get_current_highlight()
        if current_index >= 0 and current_index < self.actions.get_action_count():
            # Get the action name from the button
            action = self.actions.buttons[current_index]["action"]
            # Handle the action
            self.handle_action(action, current_entry)
            return True
        return False

    def cleanup(self):
        """Clean up resources"""
        if self.actions:
            self.actions.hide()
            self.actions = None
