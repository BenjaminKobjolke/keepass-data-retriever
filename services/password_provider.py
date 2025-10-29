"""Password provider service for KeePass database authentication."""

import sys
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
    def get_password_for_reload():
        """
        Get password for reload - always show dialog (ignore command line).

        Returns:
            str: Password string, or None if cancelled
        """
        dialog = PasswordDialog()
        return dialog.get_password()
