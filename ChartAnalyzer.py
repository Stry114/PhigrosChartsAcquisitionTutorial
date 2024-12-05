import json
import os

### 用户自定义变量 ###
### 留空请填 None ###

# 铺面文件夹，即 TextAsset 文件夹
fileDir = u"D:\phigros\export\TextAsset"
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
        self.keyMaxSecond = keyMaxTime / 90
        # 最后一个事件的事件
        self.eventMaxTime = eventMaxTime
        self.eventMaxSecond = eventMaxTime / 90
        # 曲长
        self.maxTime = max(eventMaxTime, keyMaxTime)
        self.audioLength = round(self.maxTime / bpm / 0.524)
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


if __name__ == "__main__":

    # 扫描路径下所有铺面文件
    fileList = os.listdir(fileDir)
    fileCount = len(fileList)

    for i in range(len(fileList)):
        file = fileList[i]

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
            print(f"{i}/{fileCount}\t分析完成{chart}")
        except KeyError as e:
            print(f"{i}/{fileCount}\t分析‘{file}’时遇到 KeyError:"+str(e))
    
    # 计算匹配度
    print(f"正在对 {fileCount} 个铺面文件进行匹配。")
    for chart in chartObjectsList:
        if targetNumber is not None:
            chart.sortingScore += max(0, 10-abs(targetNumber-chart.objectNumber))
        if targetBPM is not None:
            chart.sortingScore += max(0, 10-0.2*abs(targetBPM-chart.bpm))
        if targetMaxTime is not None:
            chart.sortingScore += max(0, 10-0.2*abs(targetMaxTime - chart.audioLength))
    # 进行排序
    sortedList: list["Chart"] = sorted(chartObjectsList, key=sortingCallBack, reverse=True)[:10]
    
    print("匹配完成。")
    # 进行输出
    print("排名\t匹配度\t物量\tBPM\t曲长\t文件名")
    print(f"目标\t\t{targetNumber}\t{targetBPM}\t{targetMaxTime}")
    for i in range(len(sortedList)):
        chart = sortedList[i]
        print(f"{i+1}\t{chart.sortingScore/30:.2%}\t{chart.objectNumber}\t{chart.bpm}\t{chart.audioLength}\t{chart.file}")
