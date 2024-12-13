import json
import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog


### 用户自定义变量 ###
### 留空请填 None ###

# 铺面文件夹，即 TextAsset 文件夹
fileDir = u"D:"
# 难度
difficulty = "AT"
# 目标物量
targetNumber = 1156
# 目标时长 (单位：秒)
targetMaxTime = 162
# 目标bpm (单位：拍/分钟)
targetBPM = 174

# 注：
# 1. 音频长度是根据最后一个note/最后一个判定线动画的时间推测的，可能略短于实际音频长度
# 2. bpm是铺面开头段的bpm，请注意部分铺面会变速。极少数特殊铺面，为了整活可能会使用特殊的bpm，如321的bpm为321.321
# 3. 程序对铺面物量进行统计，比较可信，可以作为主要判断标准

### 请勿修改的全局变量 ###
# 关键词，名称中不含所有关键词的文件将被跳过
keyWords = ["#", difficulty]
# 输出列表
chartObjectsList: list["Chart"] = []
# 匹配队列
sortedList: list["Chart"] = []
# 文件列表及其长度
fileCount = None
fileList = []
# 已完成扫描
scanned = False


class Chart:
    def __init__(self, file, bpm, aboveNumber, belowNumber, keyMaxTime, eventMaxTime):
        # 文件名称
        self.file = file
        self.fileName = file
        # 铺面 bpm
        self.bpm = bpm
        # 物量
        self.aboveNumber = aboveNumber
        self.belowNumber = belowNumber
        self.objectNumber = aboveNumber + belowNumber
        # 最后一个键的时间
        self.keyMaxTime = keyMaxTime
        self.keyMaxSecond = round(self.keyMaxTime / bpm * 1.875, 2)
        # 最后一个事件的事件
        self.eventMaxTime = eventMaxTime
        self.eventMaxSecond = round(self.eventMaxTime / bpm * 1.875, 2)
        # 曲长
        self.maxTime = max(eventMaxTime, keyMaxTime)
        self.audioLength = round(self.maxTime / bpm * 1.875, 2)
        # 排名分数
        self.sortingScore = 0

    def __str__(self) -> str:
        return f"<Chart '{self.fileName}', bpm={self.bpm}, number={self.objectNumber}, maxTime={self.maxTime}, audioLength={self.audioLength}s>"

    def __repr__(self) -> str:
        return f"<Chart {self.fileName}>"

def sortingCallBack(chart: Chart):
    # 给 sorted() 函数排序用的回调函数
    return chart.sortingScore

def analyseJsonChart(chartFile: str):
    # 分析铺面文件，生成 Chart 对象
    # 提取物量、bpm、时长等内容
    f = open(chartFile, 'r', encoding="utf-8")
    jsonData = json.load(f)

    # 铺面 bpm
    bpm = jsonData["judgeLineList"][0]["bpm"]
    # 物量
    aboveNumber = 0
    belowNumber = 0
    # 最后一个键的时间
    keyMaxTime = 0
    # 最后一个事件的时间
    eventMaxTime = 0

    # 统计最后一个判定线动画的时间
    for line in jsonData["judgeLineList"]:
        aboveNumber += len(line["notesAbove"])
        belowNumber += len(line["notesBelow"])

        eventList = line["speedEvents"] + line["judgeLineMoveEvents"] + line["judgeLineRotateEvents"] + line["judgeLineDisappearEvents"]
        for event in eventList:
            eventMaxTime = max(event["startTime"], eventMaxTime)
    
    # 统计最后一个note的时间
    for line in jsonData["judgeLineList"]:
        for note in line["notesAbove"]:
            keyMaxTime = max(note["time"], keyMaxTime)

    return Chart(
        chartFile,
        bpm,
        aboveNumber,
        belowNumber,
        keyMaxTime,
        eventMaxTime
    )

def selectPath():
    path = filedialog.askdirectory(title="打开铺面文件夹", initialdir=fileDir)
    if not path:
        return
    else:
        E1.delete(0, END)
        E1.insert(0, path)

def info(*msg, step=" ", end=""):
    msg = step.join(msg)+end
    BL1.config(text=msg)
    top.update()


def main():
    global chartObjectsList
    global fileList, chartObjectsList
    global fileDir, fileCount
    global scanned
    global keyWords
    global targetBPM, targetNumber, targetMaxTime, difficulty

    # 预处理数据
    fileDir = E1.get()
    if not os.path.exists(fileDir):
        messagebox.showerror("错误", "路径不存在。")

    difficulty = E2.get()
    targetNumber = E3.get()
    targetBPM = E4.get()
    targetMaxTime = E5.get()

    if targetNumber == "" and targetBPM == "" and targetMaxTime == "":
        messagebox.showerror("缺少筛选条件", "请至少填写一个筛选条件！")
        return

    if difficulty == "":
        difficulty = None
        keyWords = ["#"]
    else:
        keyWords = ["#", difficulty]
    if targetNumber == "":
        targetNumber = None
    else:
        targetNumber = int(targetNumber)
    if targetBPM == "":
        targetBPM = None
    else:
        targetBPM = int(targetBPM)
    if targetMaxTime == "":
        targetMaxTime = None
    else:
        targetMaxTime = int(targetMaxTime)

    # 开始逐个分析谱面
    scanned = True
    fileList = os.listdir(fileDir)
    fileCount = len(fileList)
    chartObjectsList = []

    for i in range(len(fileList)):
        file = fileList[i]
        fileName = fileList[i]

        # 确认是否含有关键词
        # 跳过不含关键词的文件
        skip = False
        for keyword in keyWords:
            if keyword not in file:
                skip = True
        if skip:
            continue

        # 尝试分析铺面文件
        try:
            chart = analyseJsonChart(os.path.join(fileDir, file))
            chartObjectsList.append(chart)
            info(f"{i}/{fileCount}\t分析完成{chart}")
        except KeyError as e:
            info(f"{i}/{fileCount}\t分析‘{file}’时遇到 KeyError:" + str(e))

    # 计算匹配度
    info(f"正在对 {fileCount} 个铺面文件进行匹配。")
    chart.sortingScore = 0
    for chart in chartObjectsList:
        if targetNumber is not None:
            chart.sortingScore += max(0, 10 - abs(targetNumber - chart.objectNumber))
        if targetBPM is not None:
            chart.sortingScore += max(0, 10 - 0.2 * abs(targetBPM - chart.bpm))
        if targetMaxTime is not None:
            chart.sortingScore += max(0, 10 - 0.2 * abs(targetMaxTime - chart.audioLength))
    # 进行排序
    sortedList: list["Chart"] = sorted(chartObjectsList, key=sortingCallBack, reverse=True)[:10]


    # 输出到T1
    for child in T1.get_children():
        T1.delete(child)
    if len(sortedList) == 0:
        info("匹配完成。未找到任何匹配项目。")
    elif sortedList[0].sortingScore <= 0:
        info("匹配完成。未找到任何匹配项目。")
    else:
        info("匹配完成，最佳匹配项为："+sortedList[0].fileName)
        for i in range(len(sortedList)):
            chart = sortedList[i]
            if chart.sortingScore <= 0:
                continue
            T1.insert("", "end",
              values=(
                  chart.fileName,
                  chart.objectNumber,
                  chart.bpm,
                  chart.audioLength,
                  f"{chart.sortingScore / 30:.2%}"
            ))


if __name__ == '__main__':
    top = Tk()
    top.geometry("700x500")
    top.title("ChartAnalyzer")
    top.resizable(0, 0)

    L1 = Label(top, text="谱面文件夹（TextAsset）")
    L1.place(x=20,y=20)
    E1 = ttk.Entry(top)
    E1.place(x=20,y=40,width=560,height=30)
    B1 = ttk.Button(top, text="选取", command=selectPath)
    B1.place(x=600,y=40,width=80,height=30)

    L2 = Label(top, text="关键词")
    L2.place(x=20,y=80)
    E2 = ttk.Entry(top)
    E2.place(x=20,y=100,width=100,height=30)

    L3 = Label(top, text="物量")
    L3.place(x=140,y=80)
    E3 = ttk.Entry(top)
    E3.place(x=140,y=100,width=100,height=30)

    L4 = Label(top, text="BPM")
    L4.place(x=260,y=80)
    E4 = ttk.Entry(top)
    E4.place(x=260,y=100,width=100,height=30)

    L5 = Label(top, text="音频长度")
    L5.place(x=380,y=80)
    E5 = ttk.Entry(top)
    E5.place(x=380,y=100,width=100,height=30)

    B2 = ttk.Button(top, text="开始筛选", command=main)
    B2.place(x=500,y=80,width=180,height=50)

    T1 = ttk.Treeview(top)
    T1.place(x=20,y=150,width=660,height=300)

    BL1 = Label(top, bg="white", anchor="w")
    BL1.place(x=0,y=480,width=700,height=20)

    column = ["1", "2", "3", "4", "5"]
    T1.config(columns=column, show='headings')
    T1.heading("1", text="文件路径")
    T1.heading("2", text="物量")
    T1.heading("3", text="BPM")
    T1.heading("4", text="谱面时长（秒）")
    T1.heading("5", text="匹配度")
    T1.column("1", width=200)
    T1.column("2", width=1)
    T1.column("3", width=1)
    T1.column("4", width=1)
    T1.column("5", width=1)

    top.after(1000, selectPath)
    mainloop()