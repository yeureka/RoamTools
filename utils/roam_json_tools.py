import json
import re
import time
import requests
import os
import pickle
from functools import wraps
from utils.fixroam import fix_roam


def retry(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        last_raised = None
        retries_limit = 3
        for _ in range(retries_limit):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print("retrying %s", func.__qualname__)
                last_raised = e
        raise last_raised

    return wrapped


class MarkdownImg:
    def __init__(self):
        self.markdown_img_str = None
        self.img_introduction = None
        self.img_url = None
        self.img_path = None
        self.img_name = None
        self.new_img_url = None
        self.new_markdown_img_str = None
        self.upload_status = False


def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        page_lst = json.load(f)
    return page_lst


def open_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_json_file(file_path, json_content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json_content)


def pickle_lst(path, lst):
    with open(path, "wb") as f:
        pickle.dump(lst, f)


def load_pickle_lst(path):
    with open(path, "rb") as f:
        markdown_img_lst = pickle.load(f)
        return markdown_img_lst


def get_config():
    config_dict = load_json_file("./config.json")
    return config_dict


def save_img(img_name, img_content):
    path = os.getcwd() + '/img/' + img_name
    with open(path, 'wb') as f:
        f.write(img_content)
    return path


def get_img_name(img_url):
    time_stamp = str(int(time.time() * 10000))
    split_url = img_url.split('/')
    img_name = split_url[-1]
    if split_url[2] == "firebasestorage.googleapis.com":
        img_name = time_stamp + ".png"
    return img_name


@retry
def download_img(img_url, proxies):
    resp = requests.get(img_url, proxies=proxies, timeout=30)
    if resp.status_code != 200 or not len(resp.content):
        raise ValueError
    return resp.content


@retry
def upload_img(path, picgo_upload):
    data = {
        "list": [path]
    }
    resp = requests.post(picgo_upload, data=json.dumps(data), timeout=30)
    resp_info = json.loads(resp.text)
    return resp_info["success"], resp_info["result"][0]


def construct_markdown_img_str(img_introduction, new_img_url):
    return "![{}]({})".format(img_introduction, new_img_url)


class RoamTool:
    def __init__(self, my_print=print):
        self.roam_json = None
        self.new_roam_json = None
        self.reimport_json_file = None
        self.proxies = None
        self.picgo_upload = None
        self.markdown_img_lst = list()
        self.my_print = my_print
        self.current_dir = os.getcwd() + "/"
        self.pickle_path = self.current_dir + "markdown_img_lst.pickle"

    def init_config(self):
        config_dict = get_config()
        self.proxies = config_dict.get("proxies", None)
        self.picgo_upload = config_dict.get("picgo_upload", None)
        self.my_print("已初始化代理和Picgo服务")

    def _analysis_markdown_img_str(self, roam_json):
        pattern = re.compile(r"(!\[(.*?)]\((.*?)\))")
        img_info_lst = pattern.findall(roam_json)
        for img_info in img_info_lst:
            markdown_img = MarkdownImg()
            markdown_img.markdown_img_str = img_info[0]
            markdown_img.img_introduction = img_info[1]
            markdown_img.img_url = img_info[2]
            self.markdown_img_lst.append(markdown_img)
            self.my_print("找到图片链接", markdown_img.markdown_img_str)

    def _download_and_save_img(self):
        for markdown_img in self.markdown_img_lst:
            self.my_print("下载:", markdown_img.img_url)
            try:
                img_content = download_img(markdown_img.img_url, self.proxies)
            except Exception as e:
                self.my_print("下载失败", e)
                continue

            markdown_img.img_name = get_img_name(markdown_img.img_url)

            self.my_print("保存 {} 到img文件夹:".format(markdown_img.img_name))
            try:
                markdown_img.img_path = save_img(markdown_img.img_name,
                                                 img_content)
            except Exception as e:
                self.my_print("保存失败", e)
                continue

    def _upload_img_and_get_new_url(self):
        for markdown_img in self.markdown_img_lst:
            self.my_print("上传:", markdown_img.img_path)
            try:
                upload_status, new_img_url = upload_img(
                    markdown_img.img_path,
                    self.picgo_upload
                )
                if upload_status:
                    markdown_img.new_img_url = new_img_url
                    markdown_img.new_markdown_img_str = \
                        construct_markdown_img_str(
                            markdown_img.img_introduction,
                            markdown_img.new_img_url
                        )
                    markdown_img.upload_status = True
                else:
                    raise ValueError
            except Exception as e:
                self.my_print("上传失败", e)
                continue

    def _replace_markdown_img_str(self):
        for markdown_img in self.markdown_img_lst:
            self.roam_json = self.roam_json.replace(
                markdown_img.markdown_img_str,
                markdown_img.new_markdown_img_str
            )
            self.my_print(
                "替换完成:",
                markdown_img.markdown_img_str,
                "->",
                markdown_img.new_markdown_img_str
            )

    def open_json_file(self, file_path):
        self.my_print("进入打开文件:", file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            self.my_print("文件打开:", file_path)
            return f.read()

    def analysis(self, json_path):
        self.my_print("打开文件前:", json_path)
        self.roam_json = self.open_json_file(json_path)
        self.my_print("打开文件:", json_path)
        self._analysis_markdown_img_str(self.roam_json)
        self.my_print("分析完成，找到 {} 个链接".format(str(len(self.markdown_img_lst))))
        pickle_lst(self.pickle_path, self.markdown_img_lst)
        self.my_print("文件markdown_img_lst.pickle已保存")

    def download_and_save(self):
        # 下载并保存图片
        self.my_print("从markdown_img_lst.pickle获取链接")
        self.markdown_img_lst = load_pickle_lst(self.pickle_path)
        self.my_print("获取到{}个链接".format(str(len(self.markdown_img_lst))))
        self.my_print("下载保存图片")
        self._download_and_save_img()
        pickle_lst(self.pickle_path, self.markdown_img_lst)
        self.my_print("文件markdown_img_lst.pickle已保存")

    def upload_and_get_new_url(self):
        # 通过picgo上传图片并构造新链接
        self.my_print("从markdown_img_lst.pickle获取链接")
        self.markdown_img_lst = load_pickle_lst(self.pickle_path)
        self.my_print("获取到{}个链接".format(str(len(self.markdown_img_lst))))
        self.my_print("上传图片并获取新链接")
        self._upload_img_and_get_new_url()
        pickle_lst(self.pickle_path, self.markdown_img_lst)
        self.my_print("文件markdown_img_lst.pickle已保存")

    def replace_url(self):
        # 修改roam_json替代原有链接
        self.my_print("从markdown_img_lst.pickle获取链接")
        self.markdown_img_lst = load_pickle_lst(self.pickle_path)
        self.my_print("获取到{}个链接".format(str(len(self.markdown_img_lst))))
        self.my_print("替换新旧markdown链接")
        self._replace_markdown_img_str()
        save_json_file("new_json_file.json", self.roam_json)
        self.my_print("保存文件")

    def fix_roam_json(self):
        # fix json，使其可以重新导入RoamResearch中
        # NOTE: Roam might just not want to import a note!
        # When you identify these, blacklist them and rerun.
        # 打开新json文件，修复并保存为新json文件
        self.my_print("开始修复json文件")
        self.new_roam_json = open_json_file("new_json_file.json")
        blacklist = list()
        self.reimport_json_file = fix_roam(blacklist, self.new_roam_json)
        save_json_file(self.current_dir + "reimport.json",
                       self.reimport_json_file)
        self.my_print("修复完毕")

    def save_as_json(self, path):
        save_json_file(path, self.roam_json)
        self.my_print("文件成功保存到: {}".format(path))

    def run(self, path, window):
        window["run"].update(disabled=True)
        self.init_config()
        self.analysis(path)
        self.download_and_save()
        self.upload_and_get_new_url()
        self.replace_url()
        self.fix_roam_json()
        window["run"].update(disabled=False)
        window["new_json_file_path"].update(disabled=False)

    def test(self, window):
        window["run"].update(disabled=True)
        for i in range(3):
            self.my_print("ceshi{}".format(str(i)))
            time.sleep(1)
        window["run"].update(disabled=False)
        window["download"].update(disabled=False)
