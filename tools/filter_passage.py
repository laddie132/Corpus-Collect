# -*- coding: utf-8 -*-

import pandas as pd
import json
import random

random.seed(123)

root_path = '/Users/han/dataset/marco/'

data_path = root_path + 'train_v2.1_wf.json'
out_path = root_path + 'train_v2.1_wf_no.json'
all_keys = ['passages', 'query', 'query_id', 'query_type', 'answers']


def filter_passages():
    with open(data_path, 'r') as f:
        data_json = json.load(f)

    print(data_json.keys())

    passages = data_json['passages']
    querys = data_json['query']
    query_ids = data_json['query_id']
    answers = data_json['answers']

    no_answers = list(filter(lambda k: len(answers[k]) == 0, answers))
    print(len(no_answers))

    print(len(passages), len(query_ids), len(querys))

    # with open(data_path + '.bak', 'w') as f:
    #     json.dump(data_json, f, indent=2)


class new_object:
    def __init__(self, object):
        self.object = object

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return self.object['passage_text'] == other.object['passage_text']


def filter_multi_passages():
    with open(data_path, 'r') as f:
        data_json = json.load(f)

    passages = data_json['passages']
    querys = data_json['query']
    query_type = data_json['query_type']
    answers = data_json['answers']

    multi_ids = []
    multi_ids_len = []
    new_passages = {}
    new_querys = {}
    new_query_type = {}
    new_answers = {}

    for k, p in passages.items():
        select_p = list(filter(lambda x: x['is_selected'], p))
        # select_p = list(map(lambda x: new_object(x), select_p))
        # select_p = set(select_p)
        # select_p = list(map(lambda x: x.object, select_p))

        multi_ids_len.append(len(select_p))

        if len(select_p) == 0:
            multi_ids.append(k)

            new_passages[k] = select_p
            new_querys[k] = querys[k]
            new_query_type[k] = query_type[k]
            new_answers[k] = answers[k]

    print(len(multi_ids))
    multi_df = pd.DataFrame(multi_ids_len, columns=['lens'])
    print(multi_df['lens'].value_counts())

    new_json = {'passages': new_passages, 'query': new_querys, 'query_type': new_query_type, 'answers': new_answers}

    with open(out_path, 'w') as f:
        json.dump(new_json, f, indent=2)


max_passage_num = 2

def select_passages():
    with open(data_path, 'r') as f:
        data_json = json.load(f)

    passages = data_json['passages']
    querys = data_json['query']
    query_type = data_json['query_type']
    answers = data_json['answers']

    out_json = []

    for k, p in passages.items():
        select_p = list(filter(lambda x: x['is_selected'], p))

        if len(select_p) == max_passage_num:
            doc = '\n'.join(map(lambda x: x['passage_text'], select_p))
            type = query_type[k]

            out_json.append({'document': doc, 'type': type})

    random.shuffle(out_json)
    out_json = out_json[:1000]

    with open('data/doc_marco_'+str(max_passage_num)+'.json', 'w') as f:
        json.dump(out_json, f, indent=2)


def filter_squad():
    with open('/Users/didi/dataset/squad2/train-v2.0.json', 'r') as f:
        data_json = json.load(f)

    p_qas_num = []
    min_p_qas = 14
    filter_data = []

    data_json = data_json['data']
    for ele in data_json:
        ps = ele['paragraphs']

        for p in ps:
            qas = p['qas']
            possible_qas = list(filter(lambda x: not x['is_impossible'], qas))
            p_qas_num.append(len(possible_qas))

            if len(possible_qas) >= min_p_qas:
                filter_data.append({'qas': possible_qas, 'context': p['context']})

    # print(sum(p_qas_num) / len(p_qas_num))
    # print(max(p_qas_num))
    # print(min(p_qas_num))

    print(len(list(filter(lambda x: x >= 14, p_qas_num))))

    with open('data/doc_squad.json', 'w') as f:
        json.dump(filter_data, f, indent=2)


if __name__ == '__main__':
    # filter_passages()
    select_passages()
    # filter_squad()