import requests
from base64 import b64encode
from enum import Enum, member


def ra_rehost(img_link, key):
    url = "https://thesungod.xyz/api/image/rehost_new"
    data = {'api_key': key,
            'link': img_link}
    r = requests.post(url, data=data)
    return r.json()['link']


def ptpimg_rehost(img_input: str | requests.Response, key):
    url = "https://ptpimg.me/"
    data = {'api_key': key}
    files = {}
    if isinstance(img_input, str):
        data['link-upload'] = img_input
    else:
        files['file-upload'] = ('bla.jpg', img_input.content, img_input.headers['content-type'])

    r = requests.post(url + 'upload.php', data=data, files=files)
    rj = r.json()[0]
    return f"{url}{rj['code']}.{rj['ext']}"


def imgbb_rehost(img_input: str | requests.Response, key):
    url = 'https://api.imgbb.com/1/upload'
    if isinstance(img_input, requests.Response):
        img_input = b64encode(img_input.content)
    data = {'key': key,
            'image': img_input}
    r = requests.post(url, data=data)
    return r.json()['data']['url']


class IH(Enum):
    Ra = member(ra_rehost)
    PTPimg = member(ptpimg_rehost)
    ImgBB = member(imgbb_rehost)

    def __new__(cls, func):
        obj = object.__new__(cls)
        obj._value_ = len(cls.__members__)
        return obj

    def __init__(self, func):
        self.key = ''
        self.enabled = False
        self.value: int
        self.prio: int = self.value
        self.func = func

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key: str):
        self._key = key.strip()

    def extra_attrs(self):
        return self.enabled, self.key, self.prio

    def set_extras(self, enabled, key, prio):
        self.enabled = enabled
        self.key = key
        self.prio = prio

    @classmethod
    def set_attrs(cls, attr_dict: dict):
        for name, attrs in attr_dict.items():
            mem = cls[name]
            if mem:
                mem.set_extras(*attrs)

    @classmethod
    def get_attrs(cls) -> dict:
        attr_dict = {}
        for mem in cls:
            attr_dict[mem.name] = mem.extra_attrs()
        return attr_dict

    @classmethod
    def prioritised(cls) -> list:
        return sorted(cls, key=lambda m: m.prio)
