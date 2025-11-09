import customtkinter as ctk
from customtkinter import CTkEntry


class Entry(CTkEntry):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master


class App(ctk.CTk):
    def __init__(self, entries_count: int = 10, **kwargs):
        super().__init__(**kwargs)

        self.entries_count = entries_count
        self.entries = []

        self.start_y = 50
        self.start_x = 20

        self.geometry(f"300x{self.entries_count * self.start_y}")
        self.title = "Параметры"


        for _ in range(self.entries_count):

            entry_attr = Entry(self, placeholder_text=f"Attribute #{_+1}", width = 100)
            entry_attr.place(x=self.start_x, y=self.start_y*_)

            entry_value = Entry(self, placeholder_text=f"Value #{_+1}", width = 100)
            entry_value.place(x=self.start_x+120, y=self.start_y*_)

            self.entries.append(
                {"attribute": entry_attr, "value": entry_value}
            )

    def get_values(self):
        return self.entries



def run_app():

    app = App()
    app.mainloop()