
import os
import re
import yaml
import time
import hashlib
from tqdm import tqdm

class Parser:
    def __init__(self, idir='./', odir='./', config='config.yml', feedback=True):
        self.idir = idir
        self.odir = odir
        self.config = yaml.load(open(config), Loader=yaml.SafeLoader)
        self.feedback = feedback

        self.min_length = self.config['min_length']
        self.max_length = self.config['max_length']
        self.max_depth = self.config['max_depth']
        self.max_child = self.config['max_child']
        self.t_extract = self.config['t_extract']
        self.t_aggregate = self.config['t_aggregate']
        self.t_feedback = self.config['t_feedback']
        self.regex = self.config['regex']

    def __sim(self, s1, s2):
        
        l = min((len(s1), len(s2)))
        k = 0
        simPosList = []
        for i in range(l):
            if s1[i] == s2[i]:
                k += 1
                simPosList.append(i)
        if l == 0:
            return 0
        else:
            return k / l

    def __find(self, s1, s2, f): # f=True: find same elements; f=False: find different elements
        l = min((len(s1), len(s2)))
        seq = []
        if f:
            for i in range(l):
                if s1[i] == s2[i]:
                    seq.append(s1[i])
        else:
            for i in range(l):
                if s1[i] != s2[i]:
                    seq.append(s1[i])
        return seq

    def __match(self, seq, group):

        if self.feedback:
            maxsim = self.t_extract - self.t_feedback
        else:
            maxsim = self.t_extract
        maxtid = None
        for tid in group.dict.keys():
            templ = group.dict[tid]
            sim = self.__sim(seq, templ)
            if sim >= maxsim:
                maxsim = sim
                maxtid = tid
        if maxtid != None and len(seq) != len(group.dict[maxtid]):
            return None
        return maxtid

    def __flush(self, msg):
        if msg is not None:
            if msg.type == 's':
                ttype = self.single
            elif msg.type == 'm':
                ttype = self.multiple
            else:
                ttype = self.table

            if msg.tid not in ttype.dict.keys():
                ttype.dict[msg.tid] = Class()
                ttype.num += 1
                ttype.dict[msg.tid].symbol = msg.type + str(ttype.num)
            cls = ttype.dict[msg.tid]
            cls.list.append((msg.idx, msg.lines)) 
            cls.template = msg.template # always keep template updated
            meta_template = msg.template.copy()
            for i in range(len(meta_template)):
                if re.search(r'<\*.+?>', meta_template[i]):
                    meta_template[i] = '<*>'
                elif re.search(r'<\?>', meta_template[i]):
                    meta_template[i] = '<?>'
            self.meta.list.append(cls.symbol + ', ' + str(msg.idx) + ', ' + ' '.join(meta_template))
            self.meta.num += 1
        return Msg()

    def parse(self, logname):
        begintime = time.time()
        self.logpath = self.idir + logname
        self.log = open(self.logpath, 'r', encoding='UTF-8')

        self.root = Node() # initialate root node
        self.root.child['*'] = Group() # initialate rubbish bucket
        self.single = Type()
        self.multiple = Type()
        self.table = Type()
        self.meta = Meta()

        msg = Msg()
        lastseq = []
        lastSpaceCounter = -1
        C = None
        beginIdx = 0
        lines = self.log.readlines() 
        for idx, line in tqdm(enumerate(lines)):

            node = self.root
            mf = True # match flag
            nf = False # new msg flag
            lf = False # last line flag

            """ 
                key casting
            """
            tline = line
            for r in self.regex:
                tline = re.sub(r['re'], r['symbol'], tline) # tokenization line
            tseq = tline.split() # token sequence

            # if tseq == [] or tseq == ['<!>']: # skip the empty line and empty header line
            if tseq == []: # skip the empty line
                continue
            if tseq[0] == '<!>': # if this line is a new message's first line, then flush the old message to its Type
                # get rid of timestamp
                tseq = tseq[1 :] 
                nf = True
            if tseq == ['<?>']: # skip splitter line
                continue
            for shift in range(1, len(lines)-idx):
                nline = lines[idx + shift]
                nline = re.sub(self.regex[-1]['re'], self.regex[-1]['symbol'], nline)
                nlineseq = re.sub(self.regex[0]['re'], self.regex[0]['symbol'], nline).split()
                if nlineseq == []: # skip empty line
                    continue
                elif nlineseq == ['<?>']: # skip splitter line
                    continue
                else:
                    if nlineseq[0] == '<!>': # if next line is a new line, then lf = True
                        lf = True
                    break
            if idx == len(lines)-1: # the last line 
                lf = True

            """
                line aggregating or pattern extracting
            """
            if nf:
                beginIdx = idx + 1
                lastSpaceCounter = -1
                msg.lines.append([re.sub(self.regex[0]['re'],'',line)])
            else: # if this line is a inter-line (because it has a header): Line aggregating
                if msg.type == 's':
                    msg.type = 'm'
                    C = 0
                spaceCounter = line.split(' ')[0].count('\t')
                if self.__sim(tseq, lastseq) >= self.t_aggregate: # if it can be aggregate, then put them together
                    C -= 1
                    if C <= 0:
                        msg.type = 't'
                    msg.lines[-1].append(line)  
                elif spaceCounter == lastSpaceCounter and spaceCounter != 0:
                    C += 1
                    if C > 0:
                        msg.type = 'm'
                    msg.lines[-1].append(line)  
                else: # or split them
                    msg.lines.append([line])
                lastSpaceCounter = spaceCounter
            
            if lf: # if it is the last line: pattern extracting
                # conbine sequence
                if msg.type == 'm':
                    # blocks = [msg.lines[0], msg.lines[-1]]
                    blocks = msg.lines
                    sf = False # False: Traceback; True: KV-Pair
                    for block in blocks:
                        if len(block) > 1:
                            sf = True
                            break
                    if not sf: 
                        blocks = [msg.lines[0], msg.lines[-1]]
                    tseq = []
                    for block in blocks:
                        tseqs = []
                        for tline in block:
                            for r in self.regex:
                                tline = re.sub(r['re'], r['symbol'], tline) # tokenization line
                            tseqs.append(re.sub(self.regex[0]['re'],'',tline).split())
                        cseq = tseqs[0]
                        for i in range(1, len(tseqs)):
                            if len(tseqs[i]) == len(cseq) and self.__sim(cseq, tseqs[i]) >= self.t_aggregate:
                                for j in range(len(cseq)):
                                    if cseq[j] != tseqs[i][j]:
                                        cseq[j] = '<*>'
                            else:
                                break
                        tseq += cseq
                elif msg.type == 't':
                    maxLinesNum = 1
                    maxBlockID = 0
                    for i in range(1, len(msg.lines)): # recorrect table message's template
                        if len(msg.lines[i]) > maxLinesNum and len(msg.lines[i-1]) == 1:
                            maxBlockID = i - 1
                    tseq = re.sub(self.regex[0]['re'],'',msg.lines[maxBlockID][0]).split() # get rid of timestamp (if any)      
                
                kseq = re.findall(r'<\*.+?>', ' '.join(tseq))
                pseq = [token for token in tseq if token not in kseq]
                tlen = len(tseq)
                klen = len(kseq)

                if tlen > self.max_length or tlen < self.min_length: # lost match : too long or too short token length
                    mf = False
                else:
                    # match by token length
                    if str(tlen) not in node.child.keys(): 
                        node.child[str(tlen)] = Node(2)
                    node = node.child[str(tlen)]

                    # match by key length
                    if str(klen) not in node.child.keys():
                        node.child[str(klen)] = Node(3)
                    node = node.child[str(klen)]

                    # search in order of layers 
                    maxdepth = min(self.max_depth, tlen - 1) # for some sentence, it is too short for self.max_depth tree parsing
                    l2d = min(maxdepth, klen)
                    l3d = maxdepth - l2d
                    for depth in range(4, 4+l2d):
                        key = kseq[-(depth - 3)]
                        if key not in node.child.keys():
                            node.child[key] = Node(depth)
                        node = node.child[key]
                    for depth in range(4+l2d, 4+l2d+l3d): 
                        prefix = pseq[depth - 4 - l2d]
                        if prefix not in node.child.keys():
                            if len(node.child.keys()) > self.max_child: # lost match: too many children
                                mf = False
                                break
                            node.child[prefix] = Node(depth)
                        node = node.child[prefix]
                if not mf: # if failed in matching group (because > max_length or > max_child)
                    group = self.root.child['*']
                else: 
                    if len(node.child.keys()) == 0:
                        node.child['*'] = Group()
                    group = node.child['*']
                tid = self.__match(tseq, group)

                """
                    Online updating
                """
                if tid == None:
                    tid = hashlib.md5(" ".join(tseq).encode('utf-8')).hexdigest()[0:8] # hash to get a new tid
                    group.dict[tid] = tseq
                    group.num += 1
                else: # update template
                    templ =  group.dict[tid]
                    cf = False # continue flag
                    # for i in range(min(tlen,len(templ))):
                    for i in range(tlen):
                        if templ[i] != tseq[i]:
                            if self.feedback:
                                if not re.match(r"(<\*.+?>)|(<\*>)", templ[i]) and not cf:
                                    print()
                                    # print("Old template:\t" + ' '.join(templ))
                                    # print("New message:\t" + ' '.join(tseq))
                                    print(re.sub(r"(<\*.+?>)|(<\*>)", "<*>","Old S_T:\t" + ' '.join(templ)))
                                    print(re.sub(r"(<\*.+?>)|(<\*>)", "<*>","New S_ID:\t" + ' '.join(tseq)))
                                    option = input("Are they belong to the same template? [y] or n.\n")
                                    if option == 'n':
                                        tid = hashlib.md5(" ".join(tseq).encode('utf-8')).hexdigest()[0:8] # hash to get a new tid
                                        group.dict[tid] = tseq
                                        group.num += 1
                                        cf = None
                                        break
                                    else:
                                        cf = True
                                        # for i in range(min(tlen,len(templ))):
                                        for i in range(tlen):
                                            if templ[i] != tseq[i]:
                                                templ[i] = '<*>'
                                        # if len(templ) < tlen:
                                        #     templ += tseq[len(templ):]
                                        print("S_T merged to:\t" + ' '.join(templ))
                                        
                            else:
                                templ[i] = '<*>'   
                    if cf != None:         
                        group.dict[tid] = templ
                

            """
                Flush log to cache
            """
            # flush the last message
            if lf:
                msg.idx = beginIdx
                msg.template = group.dict[tid]
                msg.tid = tid
                msg = self.__flush(msg) 

            lastseq = tseq

        print("Parsing Done.")
        endtime = time.time()
        print("Parsing running time = {}s".format(endtime-begintime))

    # use the structure to output a parsed log file
    
    def print(self):

        """
            print meta file
        """
        begintime = time.time()
        print("Building meta file...")
        if not os.path.exists(self.odir):
            os.makedirs(self.odir)
        f = open(self.odir + "meta.log",'w', encoding='UTF-8')
        for item in self.meta.list:
            f.write(item + '\n')
        f.close()

        """
            build directories
        """
        if not os.path.exists(self.odir + "event logs"):
            os.makedirs(self.odir + "event logs")
        if not os.path.exists(self.odir + "text logs"):
            os.makedirs(self.odir + "text logs")
        if not os.path.exists(self.odir + "table logs"):
            os.makedirs(self.odir + "table logs")

        """
            print parsed log files
        """

        # event log
        print("Building event log files...")
        for tid in tqdm(self.single.dict.keys()):
            cls = self.single.dict[tid]
            templseq = cls.template
            for i in range(len(templseq)):
                if re.search(r'<\*.+?>', templseq[i]):
                    templseq[i] = '<*>'
                elif re.search(r'<\?>', templseq[i]):
                    templseq[i] = '<?>'
            templstr = " ".join(templseq)
            f = open(self.odir + "event logs/" + cls.symbol + '.log', 'w', encoding='UTF-8')
            f.write("symbol: " + cls.symbol + '\n')
            f.write("template: " + templstr + '\n')
            for (idx, msg) in cls.list:
                line = msg[0][0]
                seq = line.split()
                paramlist = self.__find(seq, templseq, False)
                f.write(str(idx) + ",")
                for p in paramlist:
                    f.write(p + ",")
                f.write('\n')
            f.close()
        
        # text log
        print("Building text log files...")
        for tid in tqdm(self.multiple.dict.keys()):
            cls = self.multiple.dict[tid]
            templseq = cls.template
            for i in range(len(templseq)):
                if re.search(r'<\*.+?>', templseq[i]):
                    templseq[i] = '<*>'
                elif re.search(r'<\?>', templseq[i]):
                    templseq[i] = '<?>'
            templstr = " ".join(templseq)
            f = open(self.odir + "text logs/" + cls.symbol + '.log', 'w', encoding='UTF-8')
            f.write("symbol: " + cls.symbol + '\n')
            f.write("identifier: " + templstr + '\n')
            for (idx, msg) in cls.list:
                line = msg[0][0]
                seq = line.split()
                line = msg[-1][-1]
                seq += line.split()
                paramlist = self.__find(seq, templseq, False)
                f.write(str(idx) + ",")
                for p in paramlist:
                    f.write(p + ",")
                f.write('\n')
                for lines in msg:
                    if len(lines) == 1:
                        line = lines[0]
                        f.write('||' + line)
                    else:
                        for line in lines:
                            f.write('|>' + line)
            f.close()

        # table log
        print("Building table log files...")
        for tid in tqdm(self.table.dict.keys()):
            cls = self.table.dict[tid]
            templseq = cls.template
            for i in range(len(templseq)):
                if re.search(r'<\*.+?>', templseq[i]):
                    templseq[i] = '<*>'
                elif re.search(r'<\?>', templseq[i]):
                    templseq[i] = '<?>'
            templstr = " ".join(templseq)
            f = open(self.odir + "table logs/" + cls.symbol + '.log', 'w', encoding='UTF-8')
            f.write("symbol: " + cls.symbol + '\n')
            f.write("identifier: " + templstr + '\n')
            for(idx, msg) in cls.list:
                f.write(str(idx) + "," + '\n')
                for lines in msg:
                    if len(lines) > 1: 
                        for line in lines:
                            seq = line.split()
                            paramlist = []
                            for token in seq:
                                if token not in templseq:
                                    paramlist.append(token)
                            for p in paramlist:
                                f.write(p + ",")
                            f.write('\n')
            f.close()

        print("Printing Done.")
        endtime = time.time()
        print("Printing running time = {}s".format(endtime-begintime))
        
    # show parse tree
    def show(self):
        # Using Queue(FIFO) method to display the parse tree structure
        """TODO"""
        pass


class Msg:
    def __init__(self):
        self.idx = 0
        self.lines = [] # - lines
        self.type = 's'
        self.template = [] # token list
        self.tid = "" # template id

class Node:
    def __init__(self, depth = 1):
        self.child = {} # key : childNode or prefix : childNode
        self.depth = depth

class Group:
    def __init__(self):
        self.dict = {} # tid: template
        self.num = 0

class Class:
    def __init__(self):
        self.template = [] # template is a sequence (a token list)
        self.list = [] # - msgs
        self.symbol = ""
        self.num = 0
        self.entropy = {}

class Type:
    def __init__(self):
        self.dict = {} # tid : class
        self.num = 0

class Meta:
    def __init__(self):
        self.list = [] # "s1, 1"
        self.num = 0