#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date: Created on 09 Oct 2023 09:08
# @Author: Yao LI
# @File: spagrn/auroc.py

import sys
import glob
import json
import pandas as pd
import matplotlib.pyplot as plt
from itertools import product
from sklearn.metrics import precision_recall_curve, roc_curve, auc


def plot_prec_recall(prec, recall, fn='Precision-Recall.png'):
    plt.fill_between(recall, prec)
    plt.ylabel("Precision")
    plt.xlabel("Recall")
    plt.title("Train Precision-Recall curve")
    plt.savefig(fn)
    plt.close()


def sort_df(df, col_name, corder: list):
    df['CustomOrder'] = df[col_name].apply(lambda x: corder.index(x))
    df = df.sort_values(by='CustomOrder')
    df = df.drop(columns=['CustomOrder'])
    return df


def fill_in_gt(tfs, all_genes, tf_col, tg_col, value_col):
    ground_truth = pd.DataFrame(product(tfs, all_genes), columns=['regulator.gene', 'regulated.gene']).astype(str)
    ground_truth['regulator.effect'] = [0] * ground_truth.shape[0]
    ground_truth = pd.concat([ground_truth, df_true])
    ground_truth = ground_truth.drop_duplicates(['regulator.gene', 'regulated.gene'], keep='last')
    names = pd.read_csv('name_df.csv')
    ground_truth[['regulator.gene', 'regulated.gene']] = ground_truth[['regulator.gene', 'regulated.gene']].replace(
        list(names['id']), list(names['name']))
    ground_truth.to_csv('ground_truth_all_and_noise.csv', index=False)


def dir2df(mydict, col=['Name', 'Values']):
    mylist = [(key, x) for key, val in mydict.items() for x in val]
    df = pd.DataFrame(mylist, columns=col)
    return df


def random_list(num, seed=1):
    import random
    random.seed(seed)
    y3 = []
    for i in range(0, num):
        n = random.randint(1, 10)
        y3.append(n)
    return y3


class AUROC:
    def __init__(self, tfs=None,
                 tf_names=None):
        if tf_names is None:
            tf_names = ['Adf1', 'Aef1', 'grh', 'kn', 'tll', 'disco-r', 'Med', 'Dfd', 'br', 'so']
        if tfs is None:
            tfs = [2, 232, 408, 805, 1006, 1140, 1141, 1142, 1143, 1144]
        self.tfs = tfs
        self.tf_names = tf_names
        self.regulons = None
        self.ground_truth = None
        self.prediction = None
        self.baseline = None
        self.value_col = None
        self.tf_col = None
        self.target_col = None


if __name__ == '__main__':
    # 1. TFs
    tfs = [2, 232, 408, 805, 1006, 1140, 1141, 1142, 1143, 1144]
    tf_names = ['Adf1', 'Aef1', 'grh', 'kn', 'tll', 'disco-r', 'Med', 'Dfd', 'br', 'so']
    real_tfs = [2, 232, 408, 805, 1006]
    false_tfs = [1140, 1141, 1142, 1143, 1144]
    real_tf_names = ['Adf1', 'Aef1', 'grh', 'kn', 'tll']
    false_tf_names = ['disco-r', 'Med', 'Dfd', 'br', 'so']

    # 2. regulons
    # regs = json.load(open('hotspot_danb/hotspot_regulons.json'))
    regs = json.load(open(sys.argv[1]))

    # 3 true labels
    # fl = glob.glob('./GRN_params_*.csv')
    # df_true = pd.concat([pd.read_csv(i) for i in fl]).astype(str)
    # # create a ground true matrix that contains all the genes
    # fl_c = glob.glob('./counts_*.csv')
    # counts = pd.concat([pd.read_csv(i, index_col=0) for i in fl_c]).fillna(0).astype(int)
    # all_genes = list(counts.index)
    # ground_truth = pd.DataFrame(product(tfs, all_genes), columns=['regulator.gene', 'regulated.gene']).astype(str)
    # ground_truth['regulator.effect'] = [0] * ground_truth.shape[0]
    # ground_truth = pd.concat([ground_truth, df_true])
    # ground_truth = ground_truth.drop_duplicates(['regulator.gene', 'regulated.gene'], keep='last')
    # names = pd.read_csv('name_df.csv')
    # ground_truth[['regulator.gene', 'regulated.gene']] = ground_truth[['regulator.gene', 'regulated.gene']].replace(
    #     list(names['id']), list(names['name']))
    # ground_truth.to_csv('ground_truth_all_and_noise.csv', index=False)

    # t_ground_truth = ground_truth[ground_truth['regulator.gene'].isin(real_tf_names)]
    # f_ground_truth = ground_truth[ground_truth['regulator.gene'].isin(false_tf_names)]
    # f_ground_truth['regulator.effect'] = [0.0] * f_ground_truth.shape[0]

    ground_truth = pd.read_csv('ground_truth_all_and_noise.csv')
    agt = ground_truth[ground_truth['regulator.gene']=='Adf1']
    rgt = ground_truth[ground_truth['regulator.gene']!='Adf1']
    agt['regulator.effect'] = [0.0] * agt.shape[0]
    ground_truth = pd.concat([rgt, agt])
    # 4. prediction and TF-tg values
    # df_pred = pd.read_csv('hotspot_danb/predicted_outcome_ver7.csv')
    # adj = pd.read_csv('hotspot_danb/hotspot_adj.csv')
    # df_pred = pd.read_csv(sys.argv[2])
    adj = pd.read_csv(sys.argv[2])
    df_pred = dir2df(regs, col=['regulator.gene', 'regulated.gene'])
    df_pred['regulator.gene'] = df_pred['regulator.gene'].str.strip('(+)')

    # ratio of positives
    baseline = 1 - ground_truth[ground_truth['regulator.effect'] == 0].shape[0] / ground_truth.shape[0]

    # ll = []
    # for tf in tf_names:
    #     tg = sorted(regs[f'{tf}(+)'])
    #     sub = ground_truth[(ground_truth['regulator.gene'] == tf) & (ground_truth['regulated.gene'].isin(tg))]
    #     # sort by target gene order
    #     sub = sort_df(sub, 'regulated.gene', tg)
    #     ll.append(sub)
    # matched_truth = pd.concat(ll)

    #
    # pred = df_pred.merge(adj, left_on=['regulator.gene', 'regulated.gene'], right_on=['TF', 'target'], how='left').drop(['TF', 'target'], axis=1)

    # pred = df_pred.merge(adj, left_on=['regulator.gene', 'regulated.gene'], right_on=['TF', 'target'], how='left').drop(['TF', 'target'], axis=1)
    pred_index = pd.merge(df_pred[['regulator.gene', 'regulated.gene']],
                          ground_truth[['regulator.gene', 'regulated.gene']], on=['regulator.gene', 'regulated.gene'],
                          how='outer')
    pred_full = pred_index.merge(adj, left_on=['regulator.gene', 'regulated.gene'], right_on=['TF', 'target'],
                                 how='left').drop(['TF', 'target'], axis=1)
    pred_full.columns = ['regulator.gene', 'regulated.gene', 'regulator.effect']
    pred = pred_full.fillna(int(pred_full['regulator.effect'].min()) - 2)

    pred = pred.sort_values(['regulator.gene', 'regulated.gene'], ascending=[True, True])
    ground_truth['regulator.effect'] = ground_truth['regulator.effect'].astype('float64')
    # convert y_true into a binary matrix
    ground_truth.loc[ground_truth['regulator.effect'] > 0, 'regulator.effect'] = 1
    ground_truth = ground_truth.sort_values(['regulator.gene', 'regulated.gene'], ascending=[True, True])

    pred['regulator.effect'] = pred['regulator.effect'].astype('float64')
    plt.hist(pred['regulator.effect'])
    plt.savefig('regulator.effect.png')
    plt.close()
    # ensure two TF-target orders are the same in two dataframe

    # calculate xx
    prec, recall, thresholds = precision_recall_curve(y_true=ground_truth['regulator.effect'],
                                                      probas_pred=pred['regulator.effect'],
                                                      pos_label=1)
    print(prec, recall, thresholds)
    plot_prec_recall(prec, recall)

    new_auc = auc(recall, prec)

    auprc_ratio = new_auc / baseline
    print(auprc_ratio)

    fpr, tpr, thresholds = roc_curve(y_true=ground_truth['regulator.effect'],
                                     y_score=pred['regulator.effect'],
                                     pos_label=1)
    print(fpr, tpr, thresholds)
    plt.fill_between(fpr, tpr)
    plt.ylabel("true positive")
    plt.xlabel("false positive")
    plt.title("auroc")
    plt.savefig('aucroc.png')
    plt.close()
