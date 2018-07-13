# Author: Shigemitsu Misato

import os
import sys
import linecache

if len(sys.argv) < 2 and not os.path.isfile(sys.argv[1]) and type(sys.argv[2]) == "int":
    print("err: invalid command: python", sys.argv[0], "analyzed_file", "number_of_as (Integer)")
    sys.exit(1)

DIR = os.path.abspath(os.path.dirname(__file__))

as_num = set()
r_file = open(sys.argv[1], 'r')
number = int(sys.argv[2])
depth = 20  # 深さ

line = r_file.readline()

# verizon
while True:
    line = r_file.readline()
    if(line == 'AS: 701\n'):
        break
line = r_file.readline()
line = r_file.readline()
verizon_n = set(line.split(' '))  # verizonのneighbors

# iij
while True:
    line = r_file.readline()
    if(line == 'AS: 2497\n'):
        line = r_file.readline()
        break
line = r_file.readline()
iij_n = set(line.split(' '))  # iijのneighbora

# ocn
while True:
    line = r_file.readline()
    if(line == 'AS: 4713\n'):
        line = r_file.readline()
        break
line = r_file.readline()
ocn_n = set(line.split(' '))  # ocnのneighbors

# google
while True:
    line = r_file.readline()
    if(line == 'AS: 15169\n'):
        line = r_file.readline()
        break
line = r_file.readline()
google_n = set(line.split(' '))  # googleのneighbors


new_ocn_n = ocn_n.difference(google_n)  # OCNのneighber - Googleのneighber

ocn_verizon = new_ocn_n.intersection(verizon_n)  # OCNとverizonの共通要素 - Google
ocn_verizon_iij = ocn_verizon.intersection(iij_n)  # 3社の共通要素 - Google


# 1段目のneighbors
neighbors_1 = set()  # 1段目のASのAS番号行の集合(2個)

neighbors_1.add("AS: 701\n")
neighbors_1.add("AS: 2497\n")
neighbors_1.add("AS: 4713\n")
neighbors_1.add("AS: 15169\n")

result = set()  # 全ピックアップASのAS番号行

for i in neighbors_1:
    result.add(i)
    number -= 1

as_num.add('701')
as_num.add('2497')
as_num.add('4713')
as_num.add('15169')

if number > 0:
    for i in range(len(ocn_verizon_iij)):
        neighbor = ocn_verizon_iij.pop()
        neighbors_1.add("AS: " + neighbor + "\n")
        as_num.add(neighbor)
        number -= 1


def pick_up(file, asnam):
    file.seek(0, 0)
    while True:  # 対象のASが見つかるまで読む
        l = file.readline()
        if l == asnam:
            l = file.readline()
            l = file.readline()
            as_neighbors = set(l.split())  # あるASのneighbors
            as_neighbors.remove("NEIGHBOR:")
            diff = as_neighbors.difference(as_num)  # resultの中にあるASのneighborですでにピックアップした以外のAS
            break
    return diff


# 2段目以降のneighbors
while True:

    for x in result:

        if number < 1:
            for x in as_num:
                result.add("AS: " + x + "\n")
            break

        additional_neighbors = pick_up(r_file, x)
        dep = depth

        while True:
            if len(additional_neighbors) != 0:
                additional_as = additional_neighbors.pop()
                as_num.add(additional_as)
                print("add: {}".format(additional_as))
                number -= 1
                print("num: {}".format(number))
                dep -= 1
                if number <= 0 or dep <= 0:
                    break

            if len(additional_neighbors) == 0:
                break
            additional_neighbors = pick_up(r_file, "AS: " + additional_as + "\n")
        print("dep: {}".format(dep))
        dep = depth
        if number <= 0:
            break

    for x in as_num:
        result.add("AS: " + x + "\n")
    print("result: {}".format(len(result)))

    if number <= 0:
        break


# 書き込み
r_file.seek(0, 0)
w_file = open(DIR + '/neighbors_{}.txt'.format(sys.argv[2]), 'w')

count = 0
for l in r_file:
    count += 1
    for AS in result:
        if l == AS:
            w_file.write(l)  # AS番号行を書き込み
            n_line = linecache.getline(sys.argv[1], int(count + 2))  # neighborの行
            neighbors = set(n_line.split())  # 各ASのneighborの集合
            neighbors.intersection_update(as_num)  # neighborsをas_numにも含まれるもののみに更新
            w_file.write(linecache.getline(sys.argv[1], int(count + 1)))  # addressesの行を書き込み
            w_file.write("  NEIGHBOR:")
            for x in sorted(list(map(lambda x: int(x), neighbors))):  # neighborの中身をintにしてソートされたリストにする
                w_file.write(" " + str(x))  # neighbors行の書き込み
            w_file.write("\n")

r_file.close()
w_file.close()
