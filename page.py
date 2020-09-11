import json
import os


class Page:
    PAGES_DIR_NAME = "pages"
    count = 0

    def __init__(self, url, root_url, out_links=None, depth=0, rank=0, valid_mime=True):
        self.root_url = root_url
        self.url = url
        self.out_links = out_links
        self.depth = depth
        self.rank = rank
        self.valid_mime = valid_mime

    def __getitem__(self, link):
        yield self.out_links[link]

    def __repr__(self):
        return str(f"{self.url}  {self.depth}  {self.rank}")

    @staticmethod
    def _get_json_file_name():
        res = "{}.json".format(Page.count)
        Page.count += 1
        return res

    def get_json_path(self):
        return os.path.join(self.root_url, Page.PAGES_DIR_NAME, self._get_json_file_name())

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def save_to_json_file(self):
        with open(self.get_json_path(), 'w') as file:
            json.dump(self.__dict__, file, indent=4)

    @staticmethod
    def restore_form_json_file(path):
        with open(path, 'r') as f:
            return Page.from_json(json.load(f))



