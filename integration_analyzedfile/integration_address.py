# Author: T.Sato
output = open(r"addCombined.txt", 'a')
with open(r"../neighbors_100.txt",'r') as datas:
    for data in datas:
        line = data
        if "ADDRESSES" in line:
            output.write("  ADDRESSES:")
            line = line.replace("  ADDRESSES: ", "").replace(" \n","").replace("\n","")
            if len(line) > 5:
                line = line.split(" ")
                remake = []
                for each in line:
                    add = [int(i) for i in each.replace('/','.').split('.')]
                    addr = ""
                    for i in range(len(add)-1):
                        bit = str(bin(add[i]).replace("0b",""))
                        addr = addr + "0" * (8 - len(bit)) + bit
                    bits = addr[0:add[4]]
                    remake = remake + [bits]
                mark = remake[0]
                adjust = [mark]
                for i in range(1,len(remake)):
                    test = remake[i]
                    length = min(len(mark),len(test))
                    if mark[0:length] != test[0:length]:
                        adjust = adjust + [test]
                        mark = test
                for i in range(len(adjust)):
                    bit = adjust[i] + ("0" * (32-len(adjust[i])))
                    a = [int(bit[i:i+8],2) for i in range(0, len(bit), 8)]
                    back = str(a[0]) + "." + str(a[1]) + "." + str(a[2]) + "." + str(a[3]) + "/" + str(len(bits))
                    output.write(" " + back)
            output.write("\n")
        else:
            output.write(line)
output.close()

