import threading, os, psutil

class ThreadMaster:

    def __init__(self):

        self.threads = []
        self.active_threads = []

        self.cpu_threads = os.cpu_count()
        self.cpu_cores = psutil.cpu_count(True)

    def add_thread(self, func, name, daemon = True):

        self.threads.append({
            "name": name,
            "func": func,
            "daemon": daemon
        })

    def start_thread(self, name):

        o = None

        for t in self.threads:
            if t["name"] == name:
                o = t

        if o is None:
            return

        thread = threading.Thread(target=o["func"], daemon=o["daemon"], name=o["name"])
        thread.start()


        self.active_threads.append({"thread": thread, "object": o})

    def start_all_threads(self):

        for t in self.threads:
            self.start_thread(t["name"])




