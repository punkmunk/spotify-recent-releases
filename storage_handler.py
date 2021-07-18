import pickle
import os


class StorageHandler:
    # A very simple storage handler using data serialization

    def __init__(self, fname: str):
        self.fname = fname

    def load(self):
        if os.path.exists(self.fname):
            with open(self.fname, "rb") as f:
                self.data = pickle.load(f)
        else:
            self.data = set()

    def save(self):
        with open(self.fname, "wb") as f:
            pickle.dump(self.data, f)
