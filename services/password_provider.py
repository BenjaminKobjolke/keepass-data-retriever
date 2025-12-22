"""Password provider service for KeePass database authentication."""

import sys
from typing import Callable, Tuple, Optional
from ui.password_dialog import PasswordDialog


class PasswordProvider:
    """Handles password retrieval from command line or GUI dialog."""

    @staticmethod
    def get_password():
        """
        Get password using command line argument or GUI dialog.

        Returns:
            str: Password string, or None if cancelled
        """
        args = sys.argv[1:]

        # Check for --password argument (for backward compatibility)
        for i, arg in enumerate(args):
            if arg == '--password' and i + 1 < len(args):
                return args[i + 1]

        # If no password provided, show password dialog
        dialog = PasswordDialog()
        return dialog.get_password()

    @staticmethod
    def get_password_with_validation(validator: Callable[[str], Tuple[bool, Optional[str]]]):
        """
        Get password using GUI dialog with inline validation.

        Args:
            validator: Callback function (password) -> (success, error_msg)

        Returns:
            str: Password string if validation succeeded, or None if cancelled
        """
        args = sys.argv[1:]

        # Check for --password argument first (for backward compatibility)
        for i, arg in enumerate(args):
            if arg == '--password' and i + 1 < len(args):
                password = args[i + 1]
                # Validate command-line password
                success, _ = validator(password)
                if success:
                    return password
                print("Command line password is incorrect")
                # Fall through to show dialog

        # Show dialog with validator
        dialog = PasswordDialog(validator=validator)
        return dialog.get_password()

    @staticmethod
    def get_password_for_reload():
        """
        Get password for reload - always show dialog (ignore command line).

        Returns:
            str: Password string, or None if cancelled
        """
        dialog = PasswordDialog()
        return dialog.get_password()

    @staticmethod
    def get_password_for_reload_with_validation(validator: Callable[[str], Tuple[bool, Optional[str]]]):
        """
        Get password for reload with inline validation - always show dialog.

        Args:
            validator: Callback function (password) -> (success, error_msg)

        Returns:
            str: Password string if validation succeeded, or None if cancelled
        """
        dialog = PasswordDialog(validator=validator)
        return dialog.get_password()
