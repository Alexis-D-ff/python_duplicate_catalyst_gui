from tkinter import messagebox
import sys

class Message_Box():
    """
    This class generates a simple messagebox to confirm different actions.
    """
    def __init__(self, parent: object, title: str, message: str, type: str):
        """
        Args:
        ----
        parent: object
            the ttk root widget where the messagebox should be spawned
        title: str
            title of the messagebox to be shown
        message: str
            message to be shown inside the box
        type: str
            type of the message_box (confirm exit or confirm an action)
        """
        # Upon creation of an instance, check the type of message box
        if type == 'exit' and messagebox.askokcancel(title, message):
            parent.destroy()
            sys.exit()
        self.action_flag = False
        if type == 'confirm' and messagebox.askokcancel(title, message):
            # Continue only if OK button of the messagebox was pushed
            self.action_flag = True
    
    def pass_action(self) -> None:
        """
        This method returns the binary value that controls wether the messagebox was accepted or canceled.
        It controls the further execution of code after closing of the messagebox.
        """
        return self.action_flag