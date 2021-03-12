import os
import platform
import threading
import PySimpleGUI as sg
from utils.roam_json_tools import RoamTool

import tkinter as tk    # 使用Nuitka打包需要加这行以使用 tk-inter plugin
interp = tk.Tcl()


def my_print(*args, **kwargs):
    window['-ML1-' + sg.WRITE_ONLY_KEY].print(*args, **kwargs)


sys_str = platform.system()
sg.theme('Light Blue 3')

layout = [[sg.Text('选择你要转换的json文件，点击 运行 按钮\n'
                   '待程序运行结束后点击 下载 下载转换好的json文件\n'
                   'RoamResearch图片原生存放在google服务器中，请确保能访问google\n'
                   '点击 设置 设置代理服务器和 Picgo 服务')],
          [sg.Text('选择文件:', size=(7, 1)),
           sg.Input(key="json_file_path", size=(50, 1)),
           sg.FileBrowse(button_text="浏览"),
           sg.Button(button_text="设置", key="setting")],
          [sg.Submit(button_text="运行", key="run"),
           sg.Input(visible=False, enable_events=True, key="download"),
           sg.SaveAs(button_text="下载", disabled=True, key="new_json_file_path",
                     default_extension="json",
                     file_types=[('JSON', '*.json')])],
          [sg.MLine(key='-ML1-'+sg.WRITE_ONLY_KEY, size=(70, 20))]]
window = sg.Window('RoamTool', layout, finalize=True,
                   font=("San Francisco", 16))
roam_tool = RoamTool(my_print)
current_path = os.path.abspath(os.path.dirname(__file__))
while True:
    event, values = window.read()
    if event == "run":
        # threading.Thread(target=roam_tool.test,
        #                  args=(window,), daemon=True).start()
        path = values["json_file_path"]
        if path:
            old_json_path = os.path.join(current_path, "old_json.json")
            print("保存文件", old_json_path)
            if sys_str == "Windows":
                path = path.replace("/", "\\")
                print("copy " + path + " " + old_json_path)
                os.system("copy " + path + " " + old_json_path)
            else:
                os.system("cp " + path + " " + old_json_path)
            print("保存成功")
            threading.Thread(
                target=roam_tool.run,
                args=(old_json_path, window),
                daemon=True
            ).start()
        else:
            sg.popup("请先选择 roam json 文件！", font=("San Francisco", 16))
    if event == "download":
        if roam_tool.roam_json:
            new_json_path = values["new_json_file_path"]
            roam_tool.save_as_json(new_json_path)
        else:
            sg.popup("请先点运行处理 roam json 文件", font=("San Francisco", 16))
    if event == "setting":
        if sys_str == "Windows":
            os.system(".\\" + "config.json")
        elif sys_str == "Darwin":
            os.system("open " + "config.json")
        elif sys_str == "Linux":
            os.system("xdg-open " + "config.json")
        else:
            os.system("xdg-open " + "config.json")
    print(os.getcwd(), event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
window.close()
