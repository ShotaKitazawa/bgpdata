# Author: Arashi Hojo

import sys
import os
import ipaddress

if len(sys.argv) < 1 and not os.path.isfile(sys.argv[1]):
    print("err: invalid command: python", sys.argv[0], "analyzed_file")
    sys.exit(1)

DIR = os.path.abspath(os.path.dirname(__file__))

output = open(DIR + "/addCombined.txt", 'a')

with open(sys.argv[1],'r') as datas:
#下はファイルパス指定ver
#with open(os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))+"/sampling_analyzedfile/neighbors_100.txt" ,'r') as datas:
    
    for data in datas:
        line = data
    #下は数行テスト
    #for X in range(0,0):
        #datas.readline()
    #for X in range(0,3):
        #line = datas.readline()
        #print(line)
        
        if "ADDRESSES" in line:
            output.write("  ADDRESSES:")
            line = line.replace("  ADDRESSES: ", "").replace(" \n","").replace("\n","")

            line = line.split(" ")
            Nets = []
            for each in line:  #IPv4ネットワークオブジェクトをNetsに追加
                if each != "":
                    Nets.append(ipaddress.IPv4Network(each))

            isIntegrate = 1  #統合動作をするかのbool(while止める用)
            while(isIntegrate > 0):                
                isIntegrate = 0
                oldNets = []  #消すやーつリスト
                newNets = []  #追加やーつリスト

                #結合するか調査
                for Net in Nets:
                    #親ネットはホスト部の無駄表記を治さないといけないかもだから一度IPv4インターフェースを踏んでます(0.0.0.0の親はどうなる?)
                    SNet = ipaddress.IPv4Interface(str(Net.supernet())).network                    
                    A = list(SNet.address_exclude(Net))  #相棒の割り出し(要素1個リスト)
                    
                    for x in Nets:  #if A[0] in Nets:だとエラー?(inがipaddress用の関数だと判断されちゃう?)
                        if x == A[0]:
                            #print(A[0])
                            isIntegrate+=1
                            oldNets.append(Net)
                            oldNets.append(A[0])
                            newNets.append(SNet)
                
                #Nets更新(重複消してるだけで元のip順にソートされてない!)
                oldNets = sorted(set(oldNets),key=oldNets.index)
                newNets = sorted(set(newNets),key=newNets.index)
                #print(oldNets)
                #print(newNets)                
                for old in oldNets:
                    Nets.remove(old)
                for new in newNets:
                    Nets.append(new)
                #print(len(Nets))
            for net in Nets:
                output.write(" " + str(net))

        else:
            output.write(line)
output.close()

