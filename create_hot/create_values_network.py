# Author: Takehiko Momma

import os
import sys
import os.path

if len(sys.argv) < 1 and not os.path.isfile(sys.argv[1]):
    print("err: invalid command: python", sys.argv[0], "analyzed_file")
    sys.exit(1)

f = open(sys.argv[1],"r",encoding='utf-8')

s = 0
addx = 0
addy = 0
mask = 29 #xxx.xxx.xxx.xxx/mask
t = (32-mask)
n = 1

for q in range(t):
    n = n*2
address = "192.168.{0}.{1}/{2}"
for line in f:
    l = line[:-1].split(" ")
    if s == 0:
        AS = l[1]
        s = 1
    elif s == 1:
        s = 2
    elif s == 2:
        l.pop(0) #ここ
        l.pop(0) #らへんは
        l.pop(0) #てけとー（）　いらない要素を消してるだけ
        neighbor = l
        s = 0
        for i in neighbor:
            if int(AS) < int(i):
                if not os.path.exists("as{0}".format(AS)):
                    os.mkdir("as{0}".format(AS))
                if not os.path.exists("as{0}".format(i)):
                    os.mkdir("as{0}".format(i))
                filename = os.path.abspath(os.path.dirname(__file__)) + "/network/" + AS + "-" + i 
                g = open(filename,"w")
                a = address.format("{0}","{1}",str(mask))
                if addy > 200:
                    addx += 1
                    addy = 0
                a = a.format(str(addx),str(addy))
                g.write(a)
                addy += n
                g.close()

f.close()

