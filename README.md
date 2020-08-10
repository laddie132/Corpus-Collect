# 对话语料收集
基于tornado的网页版对话语料众包工具。

## Requirements
- Python>=3.6
- tornado>=4.5.3

## Usage

`python run.py --port 9999 --data doc.json --log logs`

1. 监听端口9999
2. 使用doc.json作为文档知识库，为每一个对话提供知识
3. 日志输出到logs目录下

## More
本项目基于tornado后端，可以修改`templates`文件夹下的html模板，适应不同的对话场景。
