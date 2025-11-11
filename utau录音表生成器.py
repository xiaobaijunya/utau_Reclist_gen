import re

# 定义存储数据的类，仅包含初始化属性
class CVVCData:
    def __init__(self):
        self.V = []     #存储所有的V
        self.C = []     #存储所有的C
        self.VR = []    #存储V+R
        self.VC = []    #存储所有的V+C
        self.VC_VV = []    #存储所有的V+C和V+V
        self.VV = []    #存储所有的V+V
        self.CV = []    #存储所有的C+V
        self.CVsta = [] #存储所有的-+C+V
        self.CVend = [] #存储所有的C+V+R
        self.CV_C = []  #存储所有的C列表的CV
        self.CV_V = []  #存储所有的V列表的CV
        self.V_dict = {}    #存储V：CV V对应的CV列表
        self.C_dict = {}    #存储C：CV C对应的CV列表
        self.V2_dict = {}   #存储CV：V CV对应的V列表
        self.C2_dict = {}   #存储CV：C CV对应的C列表
        self.CV_reclist = []    #CV采集的录音表
        self.VC_reclist = []    #VC采集的录音表
        self.CV_add_reclist = []    #剩余的CV采集的录音表
        self.VC_bis ={}     #存储重复次数
        self.VV_bis = {}    #存储重复次数
        self.V_sum = [] #存储还需要继续生成的VC的V
        self.C_sum = [] #存储还需要继续生成的VC的C
        self.sum = 0


# 读取文件的函数
def cvvc_presamp_read(data, presamps_path):
    with open(presamps_path, 'r') as file:
        ini_text = file.read()
        # 提取 [VOWEL] 部分
        vowel_match = re.search(r'\[VOWEL\](.*?)\[', ini_text, re.DOTALL)
        vowels = vowel_match.group(1).strip()
        for vowel in vowels.split('\n'):
            data.V.append(vowel.split('=')[0])
            for CV1 in vowel.split('=')[2].split(','):
                data.V_dict[vowel.split('=')[0]] = vowel.split('=')[2].split(',')
                if CV1 != '':
                    data.CV.append(CV1)
                    data.V2_dict[CV1] = vowel.split('=')[0]

        # 提取 [CONSONANT] 部分
        consonant_match = re.search(r'\[CONSONANT\](.*?)\[', ini_text, re.DOTALL)
        if consonant_match is not None:
            consonants = consonant_match.group(1).strip()
            for consonant in consonants.split('\n'):
                data.C.append(consonant.split('=')[0])
                data.C_dict[consonant.split('=')[0]] = consonant.split('=')[1].split(',')
                for CV2 in consonant.split('=')[1].split(','):
                    if CV2 != '':
                        data.CV_C.append(CV2)
                        data.C2_dict[CV2] = consonant.split('=')[0]


    data.V = list(dict.fromkeys(data.V))
    data.C = list(dict.fromkeys(data.C))
    for V1 in data.V:
        for C1 in data.C:
            data.VC.append(V1+' '+C1)
    data.VC = list(dict.fromkeys(data.VC))
    data.CV = list(dict.fromkeys(data.CV))
    data.CV_C = list(dict.fromkeys(data.CV_C))
    data.CV_V = [x for x in data.CV if x not in data.CV_C]
    for V1 in data.V:
        for C1 in data.CV_V:
            data.VV.append(V1 + ' ' + C1)
    # data.C2_dict['R'] = 'R'
    for CV_V in data.CV_V:  #把纯V添加到C列表用于生成VV
        data.C_dict[CV_V]=[CV_V]
        data.C2_dict[CV_V]=CV_V
    data.VV = list(dict.fromkeys(data.VV))
    data.CVsta = list(data.CV)
    data.CVend = list(data.CV)
    data.VR = list(data.V)

# 检查电话的函数
def phone_check_CV(data,reclist):
    for _reclist in reclist:
        _reclist=_reclist+['R']
        #CV
        for i in range(0, len(_reclist) - 1):
            if i == 0 or _reclist[i - 1] == 'R':
                if _reclist[i] in data.CVsta:
                    data.CVsta.remove(_reclist[i])
            elif _reclist[i + 1] == 'R':
                if _reclist[i] in data.CVend:
                    data.CVend.remove(_reclist[i])
            else:
                if _reclist[i] in data.CV:
                    data.CV.remove(_reclist[i])
    # print(data.VC_bis)
    # print(data.VV_bis)
    print(f'CVsta:{len(data.CVsta)},CVend:{len(data.CVend)},CV:{len(data.CV)},VC:{len(data.VC)},VV:{len(data.VV)}')
        #VC
def phone_check_VC(data,reclist):
    for _reclist in reclist:
        _reclist=_reclist+['R']
        #CV
        for i in range(0, len(_reclist) - 1):
            if _reclist[i + 1] in data.CV_C:
                phone = f'{data.V2_dict[_reclist[i]]} {data.C2_dict[_reclist[i + 1]]}'
                if phone not in data.VC_bis:#记录数量
                    data.VC_bis[phone] = 0
                data.VC_bis[phone] = data.VC_bis.get(phone, 0) + 1#记录数量
                if phone in data.VC:
                    data.VC.remove(phone)
            elif _reclist[i + 1] in data.CV_V:
                # phone = f'{data.V2_dict[_reclist[i]]} {data.V2_dict[_reclist[i+1]]}'
                phone = phone = f'{data.V2_dict[_reclist[i]]} {_reclist[i+1]}'
                if phone not in data.VV_bis:#记录数量
                    data.VV_bis[phone] = 0
                data.VV_bis[phone] = data.VV_bis[phone] + 1#记录数量
                if phone in data.VV:
                    data.VV.remove(phone)
    # print(data.VC_bis)
    # print(data.VV_bis)
    print(f'CVsta:{len(data.CVsta)},CVend:{len(data.CVend)},CV:{len(data.CV)},VC:{len(data.VC)},VV:{len(data.VV)}')

# 生成 reclist 的函数
def Reclist(data, length):
    row = []
    cont = 0
    print(f'CVsta:{len(data.CVsta)},CVend:{len(data.CVend)},CV:{len(data.CV)},VC:{len(data.VC)},VV:{len(data.VV)}')
    #CV_V读取V列表的CV
    for _CV in data.CV:
        if cont < length:
            row.append(_CV)
            cont += 1
        else:
            data.CV_reclist.append(row)
            row = []
            cont = 0
            row.append(_CV)
            cont += 1
    else:
        data.CV_reclist.append(row)
        row = []
        cont = 0
    print('CV列表：')
    print(len(data.CV_reclist),data.CV_reclist)
    phone_check_CV(data,data.CV_reclist)
    phone_check_VC(data,data.CV_reclist)
    phone_V = ''
    phone_C = ''

    start = '0'
    #只保证生成完整的VC
    if start == 'test':
        data.CVsta = []
        data.CVend = []
        data.CV = []
        # data.VC = []
        data.VV = []

    print('VC列表：')
    while len(data.VC)+len(data.VV) !=0:
        for VC in data.VC:
            data.V_sum.append(VC.split(' ')[0])
            data.C_sum.append(VC.split(' ')[1])
        for VC in data.VV:
            data.V_sum.append(VC.split(' ')[0])
            data.C_sum.append(VC.split(' ')[1])
        data.VC_VV = data.VC+data.VV
        data.V_sum = list(dict.fromkeys(data.V_sum))
        data.C_sum = list(dict.fromkeys(data.C_sum))
        # print('V:',data.V_sum,'\nC',data.C_sum)
        for V in data.V_sum:
            #开头音生成
            for cvsta in data.CVsta:  # 创建列表副本用于遍历
                if cvsta in data.V_dict[V]:
                    data.CVsta.remove(cvsta)
                    row.append(cvsta)
                    cont += 1
                    phone_V = V
                    break
            else:   #找不到CVsta，就取第一个CV
                row.append(data.V_dict[V][0])
                cont += 1
                phone_V = V
            break
        print('-CV',row)
        #VC从这里开始生成
        while cont < length-1:
            for VC in data.VC_VV:
                VC = VC.split(' ')
                if VC[0] == phone_V:
                    phone_C = VC[1]
                    # print('phone_V',phone_V,'phone_C:',phone_C)
                    break
            else:
                break
            for cv in data.CV:
                if cv in data.C_dict[phone_C]:
                    data.CV.remove(cv)
                    row.append(cv)
                    cont += 1
                    phone_VC = f'{phone_V} {phone_C}'
                    data.VC_VV.remove(phone_VC)
                    # if phone_VC in data.VC:
                    #     data.VC.remove(phone_VC)
                    # else:
                    #     print(phone_VC)
                    #     data.VV.remove(phone_VC)
                    phone_V = data.V2_dict[cv]
                    break
            else:
                for cv in data.C_dict[phone_C]:
                    # print('1',data.V2_dict[cv])
                    if data.V2_dict[cv] in data.V_sum:
                        row.append(cv)
                        cont += 1
                        phone_VC = f'{phone_V} {phone_C}'
                        data.VC_VV.remove(phone_VC)
                        # if phone_VC in data.VC:
                        #     data.VC.remove(phone_VC)
                        # else:
                        #     print(phone_VC)
                        #     data.VV.remove(phone_VC)
                        phone_V = data.V2_dict[cv]
                        break
                else:
                    cv = data.C_dict[phone_C][0]
                    row.append(cv)
                    cont += 1
                    phone_VC = f'{phone_V} {phone_C}'
                    data.VC_VV.remove(phone_VC)
                    phone_V = data.V2_dict[cv]
                    break
        if len(row) < length-2:
            # print('过短')
            data.sum += 1

        #VV列表从这里开始生成
        while len(row) < length-2:
            for V in data.V_sum:
                row.append(data.V_dict[V][0])
                cont += 1
                phone_V = V
                break
            for VC in data.VC_VV:
                VC = VC.split(' ')
                if VC[0] == phone_V:
                    phone_C = VC[1]
                    # print('phone_V',phone_V,'phone_C:',phone_C)
                    break
            else:
                break
            for cv in data.C_dict[phone_C]:
                # print('1',data.V2_dict[cv])
                if data.V2_dict[cv] in data.V_sum:
                    row.append(cv)
                    cont += 1
                    phone_VC = f'{phone_V} {phone_C}'
                    data.VC_VV.remove(phone_VC)
                    # if phone_VC in data.VC:
                    #     data.VC.remove(phone_VC)
                    # else:
                    #     print(phone_VC)
                    #     data.VV.remove(phone_VC)
                    phone_V = data.V2_dict[cv]
                    break
            else:
                cv = data.C_dict[phone_C][0]
                row.append(cv)
                cont += 1
                phone_VC = f'{phone_V} {phone_C}'
                data.VC_VV.remove(phone_VC)
                phone_V = data.V2_dict[cv]

        #CVend
        for VC in data.VC_VV:
            VC = VC.split(' ')
            if VC[0] == phone_V:
                phone_C = VC[1]
                # print('phone_V', phone_V, 'phone_C:', phone_C)
                for cv in data.CVend:
                    if cv in data.C_dict[phone_C]:
                        data.CVend.remove(cv)
                        row.append(cv)
                        cont += 1
                        phone_VC = f'{phone_V} {phone_C}'
                        data.VC_VV.remove(phone_VC)
                        # if phone_VC in data.VC:
                        #     data.VC.remove(phone_VC)
                        # else:
                        #     print(phone_VC)
                        #     data.VV.remove(phone_VC)
                        phone_V = data.V2_dict[cv]
                        break
                else:
                    for cv in data.C_dict[phone_C]:
                        # print('1',data.V2_dict[cv])
                        if data.V2_dict[cv] in data.V_sum:
                            row.append(cv)
                            cont += 1
                            phone_VC = f'{phone_V} {phone_C}'
                            data.VC_VV.remove(phone_VC)
                            # if phone_VC in data.VC:
                            #     data.VC.remove(phone_VC)
                            # else:
                            #     print(phone_VC)
                            #     data.VV.remove(phone_VC)
                            phone_V = data.V2_dict[cv]
                            break
                    else:
                        cv = data.C_dict[phone_C][0]
                        row.append(cv)
                        cont += 1
                        phone_VC = f'{phone_V} {phone_C}'
                        data.VC_VV.remove(phone_VC)
                        phone_V = data.V2_dict[cv]
                        break
                break

        if len(row) < length:
            # print('补充CVend')
            # 如果只差一个直接添加一个结尾音
            if len(data.CVend) > 0:
                cont += 1
                row.append(data.CVend[0])
                data.CVend.remove(data.CVend[0])



        data.V_sum = []
        data.C_sum = []
        data.VC_VV = []
        print(row)
        # phone_check(data, [row])
        data.VC_reclist.append(row)
        phone_check_VC(data,[row])
        row = []
        cont = 0
    phone_check_CV(data, data.VC_reclist)
    print(len(data.VC_reclist), data.VC_reclist)
    print(len(data.CV_reclist)+len(data.VC_reclist))
    print(data.sum)
    print(data.CV)
    #生成完整-CV和CVR和CV
    print('生成完整-CV和CVR和CV')
    while len(data.CVsta)+len(data.CV)+len(data.CVend) !=0:
        row = []
        cont = 0
        while len(row) < length and len(data.CVsta)+len(data.CV)+len(data.CVend) !=0:
            CV = 'R'
            if len(data.CVsta) > 0:
                CV=data.CVsta[0]
                row.append(CV)
                data.CVsta.remove(CV)
                cont+=1
            else:
                print()
            if len(data.CV) > 0 and len(data.CVsta) == 0:
                CV=data.CV[0]
                row.append(CV)
                row.append(CV)
                data.CV.remove(CV)
                cont += 1
            elif len(data.CV) > 0 and len(data.CVsta) > 0:
                row.append(data.CV[0])
                data.CV.remove(data.CV[0])
                cont += 1
            if len(data.CVend) > 0:
                row.append(data.CVend[0])
                data.CVend.remove(data.CVend[0])
                cont += 1
            else:
                row.append(CV)
                cont += 1
            if len(data.CV) > 0 and len(row) < length:
                row.append('R')
                row.append('R')
            elif len(data.CV) == 0 and len(row) < length:
                row.append('R')
                # row.append('R')
        print(row)
        data.CV_add_reclist.append(row)
    print(len(data.CV_add_reclist), data.CV_add_reclist)
    print(len(data.CV_reclist)+len(data.VC_reclist)+len(data.CV_add_reclist))

def Rec_oto(data,reclist):
    cont = 0
    oto = []
    phone = []
    oto_repeat =[]
    oto_rec = []
    reclist1 = [rec.strip().split('_') for rec in reclist]
    reclist1 = [[rec for rec in recs if rec != ''] for recs in reclist1]
    print('oto')
    data.C2_dict['R'] = 'R'
    for rec in reclist:
        cont = 0
        phone = []
        rec = rec.strip()
        rec1 = rec.split('_')
        for CV in rec1:
            if CV != '' :
                phone.append(CV)
        #CV
        for i in range(0,len(phone)) :
            if i==0 or phone[i-1] == 'R':
                oto.append(f'{rec}.wav=- {phone[i]},{i},{i},{i},{i},{i}')
            elif i==len(phone)-1 or phone[i+1] == 'R':
                oto.append(f'{rec}.wav={phone[i]}_R,{i},{i},{i},{i},{i}')
            else:
                oto.append(f'{rec}.wav={phone[i]},{i},{i},{i},{i},{i}')
        for i in range(0,len(phone)-1) :
            if phone[i] == 'R':
                continue
            elif phone[i+1] == 'R':
                oto.append(f'{rec}.wav={data.V2_dict[phone[i]]} R,{i}00,{i}00,{i}00,{i}00,{i}00')
            else:
                oto.append(f'{rec}.wav={data.V2_dict[phone[i]]} {data.C2_dict[phone[i+1]]},{i}00,{i}00,{i}00,{i}00,{i}00')
    # print(oto,len(oto))
    for oto1 in oto:
        if oto1.split('=')[1].split(',')[0] not in oto_repeat:
            oto_repeat.append(oto1.split('=')[1].split(',')[0])
            oto_rec.append(oto1)
    # print(oto_rec,len(oto_rec))
    with open('oto.ini', 'w',encoding='utf-8') as file:
        for rec in oto_rec:
            file.write(rec + '\n')


if __name__ == "__main__":
    #记录时间
    import time
    start = time.time()

    data = CVVCData()
    cvvc_presamp_read(data,'仿vocaloid_presamp.ini')
    length = 8
    Reclist(data,length)
    with open('Reclist.txt', 'w',encoding='utf-8') as file:
        for reclist in data.CV_reclist:
            file.write('_'+'_'.join(reclist) + '\n')
        for reclist in data.VC_reclist:
            file.write('_'+'_'.join(reclist) + '\n')
        for reclist in data.CV_add_reclist:
            file.write('_'+'_'.join(reclist) + '\n')
    end = time.time()
    print('Running time: %s Seconds'%(end-start))
    with open('Reclist.txt', 'r',encoding='utf-8') as file:
        reclist = file.readlines()
        # reclist1 = [rec.strip().split('_') for rec in reclist]
        # reclist1 = [[rec for rec in recs if rec != ''] for recs in reclist1]
    Rec_oto(data,reclist)