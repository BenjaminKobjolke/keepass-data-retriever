"""Window lifecycle management for show/hide operations."""

import time
from typing import Optional, Callable
from .state_manager import StateManager, AppState
from .logger import Logger
from config import config

logger = Logger.get_instance()


class WindowLifecycle:
    """Manages window show/hide lifecycle and context detection."""

    def __init__(
        self,
        window_manager,
        state_manager: StateManager,
        window_relations_manager,
        state_handler,
        on_connect: Callable,
        input_manager,
    ):
        self.window_manager = window_manager
        self.state_manager = state_manager
        self.window_relations_manager = window_relations_manager
        self.state_handler = state_handler
        self.on_connect = on_connect
        self.input_manager = input_manager

        # State tracking
        self.active_window_title_at_last_hide: Optional[str] = None
        self.last_hotkey_time: float = 0

    def show(self) -> bool:
        """
        Handle window show with context detection and state management.

        Returns:
            True if window was shown, False if connection failed
        """
        newly_logged_window_title = None
        try:
            newly_logged_window_title = self.window_relations_manager.log_active_window()
            logger.debug(f"Active window title after logging: {newly_logged_window_title}")
        except Exception as e:
            logger.error(f"Error logging active window: {e}")

        # Check database connection
        if not self.on_connect():
            return False

        current_time = time.time()
        self.window_manager.show()

        # Determine state transitions
        current_app_state = self.state_manager.get_current_state()
        logger.debug(
            f"Current state before processing: {current_app_state}, "
            f"last hidden title: '{self.active_window_title_at_last_hide}', "
            f"new title: '{newly_logged_window_title}'"
        )

        # Check if context changed
        context_changed = (
            self.active_window_title_at_last_hide is not None
            and self.active_window_title_at_last_hide != newly_logged_window_title
        )

        if context_changed:
            logger.info(
                f"Window context changed from '{self.active_window_title_at_last_hide}' "
                f"to '{newly_logged_window_title}'. Triggering reset to INITIAL."
            )

        # Determine reset conditions
        reset_to_initial, reset_reason = self._should_reset_to_initial(
            context_changed, current_app_state, current_time
        )

        # Handle state transitions
        self._handle_state_transition(reset_to_initial, reset_reason, current_app_state)

        # Update last hotkey time
        self.last_hotkey_time = current_time

        return True

    def _should_reset_to_initial(
        self, context_changed: bool, current_state: AppState, current_time: float
    ) -> tuple:
        """
        Determine if state should reset to initial.

        Returns:
            Tuple of (should_reset: bool, reason: str)
        """
        if context_changed:
            return True, "context changed"
        elif current_state == AppState.STARTING:
            return True, "first time showing window"
        elif current_time - self.last_hotkey_time > config.get_search_reset_timeout():
            return True, "search reset timeout exceeded"
        return False, ""

    def _handle_state_transition(
        self, reset_to_initial: bool, reset_reason: str, current_app_state: AppState
    ):
        """Handle the appropriate state transition."""
        if reset_to_initial:
            logger.debug(f"{reset_reason}, transitioning to INITIAL state")
            data = {"window_relations_manager": self.window_relations_manager}
            self.state_manager.transition_to(AppState.INITIAL, data)
        elif current_app_state == AppState.HIDDEN:
            previous_state = self.state_manager.get_previous_state()
            logger.debug(f"Coming from HIDDEN state, previous state was: {previous_state}")

            if previous_state == AppState.INITIAL:
                logger.debug("Previous state was INITIAL, transitioning back")
                data = {"window_relations_manager": self.window_relations_manager}
                self.state_manager.transition_to(AppState.INITIAL, data)
            else:
                logger.debug("Attempting to restore previous state")
                if not self.state_handler.restore_previous_state():
                    logger.debug("No previous state to restore, using default")
                    self.input_manager.restore_last_mode()
        else:
            logger.debug(f"Current state: {current_app_state}. Attempting to restore.")
            if not self.state_handler.restore_previous_state():
                logger.debug("No previous state to restore, using default")
                self.input_manager.restore_last_mode()

    def hide(self):
        """Hide the window with state preservation."""
        # Store current window title
        self.active_window_title_at_last_hide = self.window_relations_manager.current_window_title
        logger.debug(
            f"Storing active_window_title_at_last_hide: '{self.active_window_title_at_last_hide}'"
        )

        # Transition to HIDDEN state if not already
        current_state = self.state_manager.get_current_state()
        if current_state != AppState.HIDDEN:
            if self.input_manager.entries:
                logger.debug(f"Storing {len(self.input_manager.entries)} entries before hiding")
            self.state_manager.transition_to(AppState.HIDDEN)

        # Hide the window
        self.window_manager.hide()

    def ensure_focus(self):
        """Ensure the current input has focus."""
        from .input import InputMode

        logger.debug(f"Ensuring focus for mode: {self.input_manager.current_mode}")

        if self.input_manager.current_mode == InputMode.SEARCH:
            logger.debug("Focusing search input")
            self.input_manager.search_input.focus_force()
        elif self.input_manager.current_mode == InputMode.LIST:
            logger.debug("Focusing list input")
            self.input_manager.list_input.focus_force()
        elif self.input_manager.current_mode == InputMode.ACTION:
            logger.debug("Focusing action input")
            self.input_manager.action_input.focus_force()
