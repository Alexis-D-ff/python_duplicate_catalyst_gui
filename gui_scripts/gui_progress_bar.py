from tkinter import ttk

class Progress_Bar(ttk.Frame):
    """
    This class generates a progress bar inside a ttk.Frame widget.
    The progress bar can be started and stopped by calling appropriate methods.
    """
    def __init__(self):
        ttk.Frame.__init__(self)
        self.prog_bar = ttk.Progressbar(self,
                                        orient = 'horizontal',
                                        length = 1000,
                                        mode = 'indeterminate',
                                        )
        
    def starting(self) -> None:
        """
        This method packs the widget and launches the progress bar.
        """
        self.prog_bar.pack(side='left', fill='both', expand=True)
        self.prog_bar.start(50)
        
    def stoping(self) -> None:
        """
        This method stops the progress bar and unpacks the widget until the next call.
        """
        self.prog_bar.stop()
        self.prog_bar.pack_forget()