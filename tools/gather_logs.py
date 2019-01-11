# -*- coding: utf-8 -*

import os
import json
import time
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

date = time.strftime('%Y%m%d', time.localtime(time.time()))

root_path = '/Users/han/Text-Dialog/corpus_collect/logs-20190109/'

doc_index = {}

dia_index = []
dia_user1 = []
dia_user2 = []
dia_doc = []
dia_turns = []

data_json = []


def gen_df():
    num_zero_turns = 0

    for file in os.listdir(root_path):
        if '.txt' not in file:
            continue

        # read logs
        file_path = os.path.join(root_path, file)
        with open(file_path, 'r') as f:
            file_lines = f.readlines()

        # dialog turns
        num_tunes = (len(file_lines) - 2) / 2
        if num_tunes == 0:
            num_zero_turns += 1
            continue
        dia_turns.append(num_tunes)

        cur_json = {'filename': file}

        # user num, idx
        user_num, idx, _ = file.split('.')
        dia_index.append(idx)
        cur_json['id'] = idx

        user1, user2 = user_num.split('-')
        user1 = user1.strip()
        user2 = user2.strip()
        dia_user1.append(user1)
        dia_user2.append(user2)

        cur_json['user_A'] = user1
        cur_json['user_B'] = user2

        # document id
        doc_start = len(user1)+2
        doc = file_lines[0][doc_start:]
        doc = eval(doc.strip())['document']

        if doc not in doc_index:
            doc_index[doc] = len(doc_index)
        doc_id = doc_index[doc]
        dia_doc.append(doc_id)

        cur_json['document_id'] = doc_id
        cur_json['document'] = doc

        # dialogs
        cur_json['dialog'] = []
        turn_id = 0
        text_id = 1
        first_user = ''
        last_user = ''
        for line in file_lines[2:]:
            cur_data = {}

            if ':' not in line:
                continue

            line_split = line.split(':')
            line_user = line_split[0]
            line_text = ':'.join(line_split[1:])
            left_user, right_user = line_user.replace('=>', '@').split('@')
            text = line_text.strip()
            label = 'user_A' if left_user == user1 else 'user_B'

            cur_data['label'] = label
            cur_data['text'] = text

            if first_user == '':
                first_user = left_user
            if first_user == left_user and left_user != last_user:
                turn_id += 1
            last_user = left_user

            cur_data['turn_id'] = turn_id
            cur_data['text_id'] = text_id
            text_id += 1

            cur_json['dialog'].append(cur_data)

        data_json.append(cur_json)

    # save data
    out_json = {'version': '1.0', 'data': data_json}
    with open('data/text_dialogs_{}.json'.format(date), 'w') as f:
        json.dump(out_json, f, indent=2, ensure_ascii=False)

    print('number of remove dialogs with zero turns:', num_zero_turns)
    print('all_users:', len(set(dia_user1 + dia_user2)))
    print('all_dialogs_valid:', len(dia_user1))

    dia_df = pd.DataFrame({'index': dia_index, 'user1': dia_user1, 'user2': dia_user2, 'doc_id': dia_doc,
                           'num_turns': dia_turns})
    # saved
    dia_df.to_csv('data/corpus_analysis_{}.csv'.format(date), index=False)

    return dia_df


def get_usr_dialogs(dia_df):
    user_df = dia_df.copy()
    user_df['user1'] = user_df['user2']
    user_df = pd.concat([dia_df, user_df])

    usr_dialog_num = user_df.groupby(['user1']).size()
    return usr_dialog_num


def analysis_logs(dia_df):
    per_dialog_num = get_usr_dialogs(dia_df)

    num_person_dialog = per_dialog_num.value_counts().to_frame(name='cnt')
    num_person_dialog['person_dialog_num'] = num_person_dialog.index
    num_person_dialog.plot.scatter('person_dialog_num', 'cnt', title='number of dialog/person')

    print('min_dialog_per_person:', per_dialog_num.min())
    print('max_dialog_per_person:', per_dialog_num.max())
    print('mean_dialog_per_person:', per_dialog_num.mean())

    # number of turns distribution
    num_turns_cnt = dia_df['num_turns'].value_counts().to_frame(name='cnt')
    num_turns_cnt['turns'] = num_turns_cnt.index
    num_turns_cnt.plot.scatter('turns', 'cnt', title='number of turns')

    print('min_num_turns:', dia_df['num_turns'].min())
    print('max_num_turns:', dia_df['num_turns'].max())
    print('mean_num_turns:', dia_df['num_turns'].mean())

    inv_doc_index = dict(map(lambda x: (x[1], x[0]), doc_index.items()))
    with open('data/corpus_users_doc_{}.json'.format(date), 'w') as f:
        json.dump(inv_doc_index, f, indent=2)


def analysis_person(min_num_turns=2):
    dia_df = pd.read_csv('data/corpus_analysis_20190109.csv')
    dia_df['user1'] = dia_df['user1'].apply(str)
    dia_df['user2'] = dia_df['user2'].apply(str)

    dia_df['is_failed'] = dia_df['num_turns'] < min_num_turns
    failed_df = dia_df[dia_df['is_failed']]
    success_df = dia_df[~dia_df['is_failed']]

    usr_dia_num_suc = get_usr_dialogs(success_df).to_frame('成功对话数')
    usr_dia_num_failed = get_usr_dialogs(failed_df).to_frame('失败对话数（轮次小于2）')

    stu_info_df = pd.read_csv('/Users/han/Downloads/sch_num.csv')
    stu_info_df.index = stu_info_df['学号'].apply(str)

    stu_grade_df = pd.merge(stu_info_df, usr_dia_num_suc, how='left', left_index=True, right_index=True)
    stu_grade_df = pd.merge(stu_grade_df, usr_dia_num_failed, how='left', left_index=True, right_index=True)

    stu_grade_df['成功对话数'] = stu_grade_df['成功对话数'].fillna(0).astype(int)
    stu_grade_df['失败对话数（轮次小于2）'] = stu_grade_df['失败对话数（轮次小于2）'].fillna(0).astype(int)

    stu_grade_df.to_csv('/Users/han/Downloads/students_grade.csv', index=False)


def remove_used_doc():
    doc_used_path = 'data/corpus_users_doc_{}.json'.format(date)
    with open(doc_used_path, 'r') as f:
        doc_used = json.load(f)

    doc_all_path = 'data/doc_marco_1.json'
    with open(doc_all_path, 'r') as f:
        doc_all = json.load(f)

    doc_used = list(doc_used.values())

    doc_not_used = list(filter(lambda x: x['document'] not in doc_used, doc_all))

    with open('data/doc_marco_not_used_{}.json'.format(date), 'w') as f:
        json.dump(doc_not_used, f)

    print(len(doc_used), len(doc_not_used), len(doc_all))


if __name__ == '__main__':
    dia_df = gen_df()
    analysis_logs(dia_df)
    analysis_person()
    plt.show()
    # remove_used_doc()
