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
daka -s        # summarize all check-ins and exit
daka --rename  # rename a resolution or item and exit
```

3. CLI 选项说明
- `-d, --date <YYYY-MM-DD>`：指定打卡日期；不传则使用今天。
- `-s, --summary`：汇总显示所有历史打卡记录并退出。
- `--rename`：进入重命名工具，可重命名 resolution 或 item，并保存后退出。

4. 选择打卡项目或者增加项目（resolution）

5. 选择具体条目或者增加条目（item）
