import sys
import pandas as pd
from collections import defaultdict


class Levenshtein:
    def init_array(self, str1, str2):
        distance = []
        for i in range(len(str1) + 1):
            distance.append([0] * (len(str2) + 1))
            distance[i][0] = i
        for j in range(len(str2) + 1):
            distance[0][j] = j
        return distance

    def edit_dist(self, str1, str2, distance):
        dist = [0] * 3
        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
                dist[0] = distance[i - 1][j - 1] if str1[i - 1] == str2[j - 1] else distance[i - 1][j - 1] + 1
                dist[1] = distance[i][j - 1] + 1
                dist[2] = distance[i - 1][j] + 1
                distance[i][j] = min(dist)
        return distance[i][j]

    def __init__(self, str1, str2):
        self.str1 = str1.split(' ')
        self.str2 = str2.split(' ')
        Levenshtein.distance = self.init_array(self.str1, self.str2)
        Levenshtein.dist = self.edit_dist(self.str1, self.str2, Levenshtein.distance)


def per_distance(src_path, trg_path):
    sentences_src = open(src_path, 'r')
    sentences_trg = open(trg_path, 'r')

    distance_list = []
    distance_dic = defaultdict(lambda: 0)
    for src, trg in zip(sentences_src, sentences_trg):
        distance = Levenshtein(src, trg).dist
        distance_dic[distance] += 1
        distance_list.append([distance / len(src.split(' ')), None])

    return distance_list


def main():
    src_path = str(sys.argv[1])
    trg_path = str(sys.argv[2])

    out_src_path = sys.argv[3]
    out_trg_path = sys.argv[4]

    df_per = pd.DataFrame(per_distance(src_path, trg_path), columns=['per', 'token']).sort_values('per')

    split_num = int(len(df_per)/5)
    start_num = 0
    end_num = split_num
    token_list = ['first', 'second', 'third', 'fourth', 'fifth']

    for i in range(5):
        if i == 4:
            df_per.iloc[start_num:, df_per.columns.get_loc('token')] = f'<{token_list[i]}>'
        else:
            df_per.iloc[start_num:end_num, df_per.columns.get_loc('token')] = f'<{token_list[i]}>'
            start_num = end_num
            end_num += split_num

    df_per = df_per.sort_index()

    with open(out_src_path, 'w') as out_src, open(out_trg_path, 'w') as out_trg:
        for index, (src_line, trg_line) in enumerate(zip(open(src_path, 'r'), open(trg_path, 'r'))):
            out_src.write(str(df_per.iloc[index, 1]) + ' ' + src_line)
            out_trg.write(trg_line)


if __name__ == '__main__':
    main()
