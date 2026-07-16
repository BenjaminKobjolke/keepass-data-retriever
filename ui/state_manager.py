from enum import Enum, auto
from typing import Dict, List, Any, Protocol, Optional
from .logger import Logger

# Get logger instance
logger = Logger.get_instance()


class AppState(Enum):
    """Enum representing the different states of the application"""

    STARTING = auto()  # Initial application startup state
    INITIAL = auto()  # Initial window state, search input with no results
    SEARCH = auto()  # Active search input with focus
    RESULTS_LIST = auto()  # Displaying search results as a list
    ENTRY_ACTIONS = auto()  # Showing actions for a selected entry
    LOCKED = auto()  # Database is locked
    PASSWORD_PROMPT = auto()  # Password dialog is shown
    HIDDEN = auto()  # Window is hidden


class StateListener(Protocol):
    """Protocol for components that listen to state changes"""

    def on_state_changed(self, state: AppState, data: Dict[str, Any]) -> None:
        """Called when the application state changes"""
        ...


class StateManager:
    """Manages the application state and notifies listeners of changes"""

    def __init__(self):
        self._current_state: AppState = AppState.STARTING
        self._previous_state: Optional[AppState] = None
        self._state_data: Dict[str, Any] = {}
        self._previous_data: Dict[str, Any] = {}  # Store previous state data
        self._listeners: List[StateListener] = []
        self._transition_in_progress: bool = False

        logger.debug(f"StateManager initialized with state: {self._current_state}")

    def transition_to(self, new_state: AppState, data: Dict[str, Any] = None) -> None:
        """
        Transition to a new state with associated data

        Args:
            new_state: The new state to transition to
            data: Optional data associated with the new state
        """
        if data is None:
            data = {}

        # Don't transition if we're already in this state
        if new_state == self._current_state:
            logger.debug(f"Already in state {new_state}, skipping transition")
            return

        # Prevent recursive transitions
        if self._transition_in_progress:
            logger.debug(
                f"State transition already in progress, skipping: {self._current_state} -> {new_state}"
            )
            return

        # Set lock to prevent recursive transitions
        self._transition_in_progress = True

        try:
            # Print debug info
            import traceback

            stack = traceback.extract_stack()
            caller = stack[-2]
            logger.debug(
                f"State transition requested by {caller.name} in {caller.filename}:{caller.lineno}"
            )

            # Store previous state and data for potential restoration
            self._previous_state = self._current_state
            self._previous_data = self._state_data.copy()  # Make a copy of the current data

            # Update current state and data
            self._current_state = new_state
            self._state_data = data

            logger.debug(f"State transition: {self._previous_state} -> {self._current_state}")

            # Notify listeners
            self._notify_listeners()
        finally:
            # Release lock
            self._transition_in_progress = False

    def get_current_state(self) -> AppState:
        """Get the current application state"""
        return self._current_state

    def get_previous_state(self) -> Optional[AppState]:
        """Get the previous application state"""
        return self._previous_state

    def get_state_data(self) -> Dict[str, Any]:
        """Get the data associated with the current state"""
        return self._state_data

    def get_previous_state_data(self) -> Dict[str, Any]:
        """Get the data associated with the previous state"""
        return self._previous_data

    def register_listener(self, listener: StateListener) -> None:
        """
        Register a component as a state change listener

        Args:
            listener: The component to register
        """
        if listener not in self._listeners:
            self._listeners.append(listener)
            logger.debug(f"Registered listener: {listener}")

    def unregister_listener(self, listener: StateListener) -> None:
        """
        Unregister a component as a state change listener

        Args:
            listener: The component to unregister
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
            logger.debug(f"Unregistered listener: {listener}")

    def _notify_listeners(self) -> None:
        """Notify all registered listeners of the state change"""
        for listener in self._listeners:
            try:
                listener.on_state_changed(self._current_state, self._state_data)
            except Exception as e:
                logger.error(f"Error notifying listener {listener}: {e}")

    def go_back(self) -> None:
        """Transition back to the previous state if available"""
        if self._previous_state:
            # Swap current and previous states
            current = self._current_state
            self._current_state = self._previous_state
            self._previous_state = current

            logger.debug(f"Going back to state: {self._current_state}")

            # Notify listeners
            self._notify_listeners()
        else:
            logger.warning("Cannot go back: no previous state")
