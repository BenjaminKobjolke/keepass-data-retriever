"""Centralized action registry for KeePass Data Retriever."""

from typing import List, Dict, Optional
from .constants import Actions


class ActionRegistry:
    """Central registry for all available actions."""

    # Action definitions with labels and keyboard shortcuts
    ACTIONS: List[Dict] = [
        {'id': Actions.AUTO_TYPE, 'label': 'Auto type', 'key': '1', 'copy': False},
        {'id': Actions.USERNAME, 'label': 'Copy username', 'key': '2', 'copy': True},
        {'id': Actions.PASSWORD, 'label': 'Copy password', 'key': '3', 'copy': True},
        {'id': Actions.TYPE_USERNAME, 'label': 'Type username', 'key': '4', 'copy': False},
        {'id': Actions.TYPE_PASSWORD, 'label': 'Type password', 'key': '5', 'copy': False},
        {'id': Actions.URL, 'label': 'Copy URL', 'key': '6', 'copy': True, 'requires_url': True},
        {'id': Actions.OPEN_URL, 'label': 'Open URL', 'key': '7', 'copy': False, 'requires_url': True},
    ]

    @classmethod
    def get_all_actions(cls, has_url: bool = True) -> List[Dict]:
        """Get all available actions, optionally filtering by URL requirement."""
        if has_url:
            return cls.ACTIONS
        return [a for a in cls.ACTIONS if not a.get('requires_url', False)]

    @classmethod
    def get_action_by_key(cls, key: str) -> Optional[Dict]:
        """Get action by keyboard shortcut key."""
        for action in cls.ACTIONS:
            if action['key'] == key:
                return action
        return None

    @classmethod
    def get_action_by_id(cls, action_id: str) -> Optional[Dict]:
        """Get action by ID."""
        for action in cls.ACTIONS:
            if action['id'] == action_id:
                return action
        return None

    @classmethod
    def get_action_ids(cls) -> List[str]:
        """Get list of all action IDs in order."""
        return [a['id'] for a in cls.ACTIONS]

    @classmethod
    def get_label(cls, action_id: str, paste_mode: bool = False) -> str:
        """Get the display label for an action, adjusting for paste mode."""
        action = cls.get_action_by_id(action_id)
        if not action:
            return action_id

        label = action['label']
        key = action['key']

        # Adjust label for paste mode
        if paste_mode and action_id in (Actions.TYPE_USERNAME, Actions.TYPE_PASSWORD):
            label = label.replace('Type', 'Paste')

        return f"{label} ({key})"
