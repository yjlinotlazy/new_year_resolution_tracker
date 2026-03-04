# daka

simple new year resolution tracker “daka”

# 用户需求 Requirements

保姆级别的新年愿望打卡。

简单的用户输入：选单里用数字表示不同的项目或者条目，可以直接选择数字，也可以添加条目。
不输入数字代表添加条目。什么也不输入直接回车则返回上一页。

有两种数据，存储于`~/.config/daka/`
 - resolutions.json：保存项目细节。增加的项目会写进这个文件。
 - data.csv：保存打卡记录。打卡的项目会写进这个文件。

# 使用方法 Usage

1. 安装（开发模式）
```
python -m pip install -e . --user
```

2. 进入程序
```
daka -d <date> # default date is today's date
```

3. 选择打卡项目或者增加项目（resolution）

4. 选择具体条目或者增加条目（item）
