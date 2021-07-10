from tkinter import ttk

class Credentials(ttk.Frame):
    """
    This class encapsulated credential info.
    """
    def __init__(self):
        ttk.Frame.__init__(self)
        credentials = ttk.Label(self, text='Designed from scratch by Alexis D.')
        credentials.pack()