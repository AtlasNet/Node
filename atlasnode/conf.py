import json


class Config (dict):
    def load(self, path):
        self.path = path
        self.clear()
        self.update(json.load(open(path)))

    def save(self):
        open(self.path, 'w').write(json.dumps(self, indent=4))
