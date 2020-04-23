import tkinter as tk

class HeureEntry(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.entry_1 = tk.Entry(self, width=2)
        self.label_1 = tk.Label(self, text=':')
        self.entry_2 = tk.Entry(self, width=2)

        self.entry_1.pack(side=tk.LEFT)
        self.label_1.pack(side=tk.LEFT)
        self.entry_2.pack(side=tk.LEFT)

        self.entries = [self.entry_1, self.entry_2]

        self.entry_1.bind('<KeyRelease>', lambda e: self._check(0, 2))
        self.entry_2.bind('<KeyRelease>', lambda e: self._check(1, 2))

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, cont[:-1])

    def _check(self, index, size):
        entry = self.entries[index]
        next_index = index + 1
        next_entry = self.entries[next_index] if next_index < len(self.entries) else None
        data = entry.get()

        if len(data) > size or not data.isdigit():
            self._backspace(entry)
        if len(data) >= size and next_entry:
            next_entry.focus()

    def get(self):
        return [e.get() for e in self.entries]

    def disable(self):
        for e in self.entries:
            e['state'] = "disabled" 

    def enable(self):
        for e in self.entries:
            e['state'] = "normal" 