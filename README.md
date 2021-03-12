### 缘由
由于Roam的调整，无法加载http链接图片，只能加载https链接图片，而本人RoamResearch中的图片存放在七牛云，https链接需要收费，因此转用又拍云，需要将笔记中所有图片链接转换到又拍云。
### 功能说明
下载RoamResearch的图片并利用Picgo上传到新图床备份，同时用新图床链接替换原有图片链接，生成新的json文件可重新导入RoamResearch中。
### 依赖
1. requests
2. pysimplegui
3. picgo
### 使用方法
#### 下载安装
```
# 下载并进入文件夹
git clone https://github.com/yeureka/RoamTools.git
cd RoamTools
# 使用 pipenv 安装虚拟环境
pipenv install
# 打开
python RoamToolUI.py 
```
#### 使用前准备
首先需要将RoamResearch文章导出为json格式文件。  
然后打开本工具。  

![](https://youpai.yeureka.cn/picgo/Screen Shot 2021-03-13 at 12.28.48 AM.png)

由于RoamResearch原生图片存放在google，众所周知的原因下载这些图片需要使用代理。点击`设置`按钮可设置代理服务ip。
```
# config.json
{
     "proxies": {   # 如果不需要代理，可将"proxies"置设为空值
          "http": "http://127.0.0.1:1087",
          "https": "http://127.0.0.1:1087"
     },
     "picgo_upload": "http://127.0.0.1:36677/upload"    # 设置Picgo
}
```
另外，上传图床利用了Picgo的服务，picgo设置请参考以下官方教程。
> [picgo-server的使用](https://picgo.github.io/PicGo-Doc/zh/guide/advance.html#picgo-server%E7%9A%84%E4%BD%BF%E7%94%A8)
#### 使用方法
1. 点击`浏览`选择刚从RoamResearch下载的json文件。
2. 点击`运行`。
3. 运行结束后点击`下载`按钮保存转换好的json文件。
4. 将转换好的json文件重新导入回RoamResearch中即可。
#### 鸣谢
感谢ryantuck提供的工具 [fix-roam](https://github.com/ryantuck/fix-roam) 解决了Roam的json文件再次导入时遇到的问题。

