"""Contains custom exceptions."""


class CommandCancel(Exception):
    """Cancel a command."""

    def __init__(self, ui, alert_params):
        self.ui = ui
        self.alert_params = alert_params
