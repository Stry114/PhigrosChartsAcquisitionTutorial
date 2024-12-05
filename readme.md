# Chart Analyzer 谱面提取/分析工具

# phigros谱面/曲绘/音频提取完整教程（并导入模拟器）
## 需要准备的工具
 - phigros 安卓安装包 (apk文件)
 - 支持直接使用官谱的 phigros 模拟器 (如phira)
 - 压缩软件 (以winrar为例)
 - python3
 - AssetsStudioGUI (下附下载链接)
 - 一台 windows 电脑
 - 打歌用的板子 (非必需)

## 第一步 解压apk文件
将apk文件扩展名改为".zip"并使用压缩软件打开。
解压到合适的目录。图中解压到`D:\phigros`目录下。

![](readme/1.png)

![](readme/2.png )

解压后的路径：

![](readme/3.png)

## 第二步 使用 Assets Studio GUI 提取资源文件
Assets Studio GUI 下载链接：
```
https://github.com/Perfare/AssetStudio/releases
```

 - 若打不开请自行百度。网上也可以找到其他下载方式。
 - 打开Assets Studio GUI，点击`file`→`Load folder`

![](readme/4.png)

 - 选择刚刚解压后的`assets`文件夹。

![](readme/5.png)

 - 等待加载完成。

![](readme/6.png)

 - 点击`Export`→`All assets`

![](readme/7.png)

 - 选择一个合适的目录导出，图中新建一个`export`文件夹并导出。

![](readme/8.png)

 - 选择一个合适的目录导出，图中新建一个`export`文件夹并导出。
 - 等待导出完成。

![](readme/9.png)

 - 这就是我们从安装包里提取出来的所有资源了。各个文件夹的内容如下

|文件夹|内容|
|---|---|
|AudioCilp|音频文件，含音效和音乐| 
|Font|字体包文件|
|Sprite|贴图，含高清曲绘等|
|TextAsset|谱面文件|
|Texture2D|也是贴图，含头像、背景等|
|VideoCilp|过场动画、异象等|

# 导入模拟器教程（以phira为例）
## 找出谱面文件
以下是提取官谱并导入模拟器的教程。以白复生AT为例。

 - 打开`Texture2D`文件夹会发现提取出来的谱面全是乱的 (每个人导出得到的顺序都不一样)，找不到想要的谱面文件。
 - 上方的脚本（ChartAnalyzer.py）会分析所有谱面物量、bpm、时长等数据，并匹配到我们想要的文件。
 - 从上方github下载`ChartAnalyzer.py`并打开编辑。

![](readme/10.png)

 - 填入铺面所在的文件夹，即`Texture2D`文件夹的完整路径。尽量使用左斜杠`/`。
 - 填入相关的物量、bpm、时长数据。
 - 在关键词一栏填入难度`"AT"`。
 - 注意不要修改其他任何内容。

![](readme/11.png)

 - 点击运行，等待分析完成.

![](readme/12.png)

 - 匹配度最高的就是筛选出来的谱面了。

## 找出音频文件
打开`AudioCilp`文件夹，右键选择显示时长。

![](readme/13.png)

选择按照时长排序，已知白复生全曲长为2:41，筛选出对应的音频。

![](readme/14.png)

逐个试听，找到正确的音频文件。

## 找出曲绘文件
打开`Sprite`文件夹，找到曲绘。

![](readme/15.png)

## 打包压缩
 - 将上述三个文件复制出来放到一起。
 - 将铺面文件的扩展名改为`.json` (非常重要)

![](readme/16.5.png)

 - 选中三个文件，右键压缩为zip格式 (请勿压缩为其他格式)

![](readme/16.png)
![](readme/17.png)

 - 将zip压缩包导入到 phira 即可。