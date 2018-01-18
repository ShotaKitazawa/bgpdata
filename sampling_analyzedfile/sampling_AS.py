# Author: Shigemitsu Misato
import sys
import linecache

if len(sys.argv) < 1 and type(sys.argv[1]) == "int":
    print("err: invalid command: python", sys.argv[0], "number_of_as (Integer)")
    sys.exit(1)

as_num = set()
read = open('../result.all', 'r')
number = int(sys.argv[1]) - 4

line = read.readline()
#verizon
while True:
    line = read.readline()
    if(line == 'AS: 701\n'):
        break
line = read.readline()
line = read.readline()
verizon_n = set(line.split(' '))

#iij
while True:
    line = read.readline()
    if(line == 'AS: 2497\n'):
        line = read.readline()
        break
line = read.readline()
iij_n = set(line.split(' '))

#ocn
while True:
    line = read.readline()
    if(line == 'AS: 4713\n'):
        line = read.readline()
        break
line = read.readline()
ocn_n = set(line.split(' '))

#google
while True:
    line = read.readline()
    if(line == 'AS: 15169\n'):
        line = read.readline()
        break
google_a = line.split(' ')
line = read.readline()
google_n = set(line.split(' '))


new_ocn_n = ocn_n.difference(google_n) #OCNのneighber - Googleのneighber

ocn_verizon = new_ocn_n.intersection(verizon_n) #OCNとverizonの共通要素 - Google
ocn_verizon_iij = ocn_verizon.intersection(iij_n) #3社の共通要素 - Google

number = number - len(ocn_verizon_iij)


#1段目のneighbor
neighbors_1 = set()
for i in range(len(ocn_verizon_iij)):
    a = ocn_verizon_iij.pop()
    neighbors_1.add("AS: " + a + "\n")
    as_num.add(a)
    
result = set()
neighbors_1.add("AS: 701\n")
neighbors_1.add("AS: 2497\n")
neighbors_1.add("AS: 4713\n")
neighbors_1.add("AS: 15169\n")
for i in neighbors_1:
    result.add(i)

as_num.add('701')
as_num.add('2497')
as_num.add('4713')
as_num.add('15169')

n_x = set()
while True:
    for x in result:
        read.seek(0,0)
        while True:
            l = read.readline()
            if l == x:
                l = read.readline()
                l = read.readline()
                x_neighbors = set(l.split())
                x_neighbors.remove("NEIGHBOR:")
                diff = x_neighbors.difference(as_num)
                if len(diff) != 0:
                    as_num.add(diff.pop())
                    number = number - 1
                    if number <= 0:
                        break
                break
        if number <= 0:
            break
    for x in as_num:
        result.add("AS: " + x + "\n")
    print(len(result))
    
    if number <= 0:
        break
    

read.seek(0,0)
write = open('../neighbors_{}.txt'.format(argv[1]), 'w')

count = 0
for l in read:
    count += 1
    for AS in result:
        if l == AS:
            write.write(l)
            n_line = linecache.getline('result.all', int(count + 2))
            neighbors = set(n_line.split()) #各ASのneighborの集合
            neighbors.intersection_update(as_num)
            write.write(linecache.getline('result.all', int(count + 1)))
            write.write("  NEIGHBOR:")
            for x in sorted(list(map(lambda x: int(x), neighbors))):
                write.write(" " + str(x))
            write.write("\n")

read.close()
write.close()
   
    

print(len(as_num))
print(len(result))
