# coding: utf-8

import os
import json
import argparse
import logging
from tornado import web, websocket, ioloop

from utils import init_logging, Dataset

base_dir = os.path.dirname(__file__)
clients = {}


def add_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='Text Dialog Corpus Aggregation Tool\n'
                                                 'Contact: liuhan132@foxmail.com')
    parser.add_argument('-P', '--port', help='port', default=9999, type=int, required=False)
    parser.add_argument('-D', '--data', help='data file', default='data/doc_marco_1.json',
                        required=False)
    parser.add_argument('-L', '--log', help='log path', default='logs/',
                        required=False)

    args = parser.parse_args()
    return args


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render(os.path.join(base_dir, 'templates', 'index.html'))


class ChatHandler(websocket.WebSocketHandler):
    def initialize(self, data_path, log_path):
        self.database = Dataset(data_path)
        print(id(self.database))
        self.log_path = log_path

    def open(self, uid):
        self.uid = uid
        logging.info("%s, %s connected." % (self.request.remote_ip, uid))

        self.school_number = None
        self.other_client = None
        self.send("请输入你的学号, 和服务器建立连接!")

    def send(self, msg, msg_type="MSG"):
        self.write_message({'type': msg_type, 'msg': msg})

    def on_message(self, msg):
        if self.school_number is None:
            if msg in clients:
                self.send("学号重复，请重新输入")
                return

            free_client_num = list(
                map(lambda y: y[0],
                    filter(lambda x: x[1].other_client is None,
                           clients.items()))
            )
            if len(free_client_num) > 10:
                free_client_num = free_client_num[:10]

            self.school_number = msg
            clients[self.school_number] = self
            self.send("连接服务器成功, 你的学号是%s, 如有错误请刷新页面重新开始. <br>\
                你可以输入对方学号发起连接, 或等待对方输入你的学号进行连接. <br>\
                刷新页面, 可以开启新的对话." % self.school_number)
            self.send("前十个空闲的用户学号如下：" + str(free_client_num))
            self.send(self.school_number, msg_type='SET_NUM')
        elif self.other_client is None:
            if msg == self.school_number:
                self.send("输入对方学号连接!")
            elif msg not in clients:
                self.send("对方尚未和服务器建立连接, 等待对方连接后, 重新输入!")
            elif clients[msg].other_client is not None:
                self.send("对方已经和其他用户连接, 请输入其他人的学号, 或让对方刷新页面重新开始!")
            else:
                self.other_client = clients[msg]
                self.other_client.other_client = self

                self.log_fn = '%s/%s-%s.%s-%s.txt' % (
                    self.log_path, self.school_number,
                    self.other_client.school_number, self.uid,
                    self.other_client.uid)
                self.other_client.log_fn = self.log_fn

                self.send("连接 %s 成功" % msg)
                self.send(msg, msg_type='SET_OTH_NUM')
                self.other_client.send("连接 %s 成功" % self.school_number)
                self.other_client.send(self.school_number, msg_type='SET_OTH_NUM')

                # random document
                data = self.database.select()

                self.send(data, 'DB')
                self.other_client.send(data, 'DB')
                with open(self.log_fn, 'a+') as f:
                    f.write(self.school_number + ':\t' + json.dumps(
                        data, ensure_ascii="False") + '\n')
                    f.write(self.other_client.school_number + ':\t' +
                            json.dumps(data, ensure_ascii="False") + '\n')
        else:
            self.other_client.send(msg)
            with open(self.log_fn, 'a+') as f:
                f.write('%s=>%s:\t%s\n' % \
                        (self.school_number, self.other_client.school_number, msg))

    def on_close(self):
        logging.info("%s disconnected with document idx=%d" % (self.uid, self.database.get_idx()))
        if self.school_number in clients and clients[self.
                school_number].uid == self.uid:
            clients.pop(self.school_number)

        if self.other_client is not None:
            self.other_client.send(self.school_number + "断开连接, 刷新页面后重新开始.")
            self.other_client.other_client = None
            self.other_client.on_close()


def run():
    args = add_args()
    init_logging()

    handlers = [
        (r'^/$', IndexHandler),
        (r'/ws/(.*)', ChatHandler, dict(data_path=args.data, log_path=args.log)),
        (r'/static/(.*)', web.StaticFileHandler, {
            'path': os.path.join(base_dir, 'static')
        }),
        (r"/(.*.html)", web.StaticFileHandler, {
            "path": os.path.join(base_dir, 'templates')
        }),
    ]

    app = web.Application(handlers)
    server = app.listen(args.port)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run()