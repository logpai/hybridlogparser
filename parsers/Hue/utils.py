def structure(filepath):
    lines = open(filepath, "r", encoding='UTF-8').readlines()
    ln = len(lines)
    groups = {}
    for line in lines:
        seq = line.strip().split(', ', 2)
        symbol = seq[0]
        index = seq[1]
        if symbol in groups.keys():
            groups[symbol].append(index)
        else:
            groups[symbol] = [index]
    return groups, ln

def evaluate(gt_filepath, pd_filepath, analysis=True):

    gt, ln = structure(gt_filepath)
    pd, _ = structure(pd_filepath)

    if analysis:
        print("EVALUATION ANALYSIS EXECUTED!")
        maxi = 0
        maxt = 0

    TTP = 0 # template TP
    MTP = 0 # message TP

    EVENT = [0, 0]
    TEXT = [0, 0]
    TABLE = [0, 0]

    for gtkey in gt.keys():
        
        f = False

        for pdkey in pd.keys():
            if gt[gtkey] == pd[pdkey]:
                TTP += 1
                MTP += len(gt[gtkey])
                
                if analysis:
                    f = True
                    if len(gt[gtkey])>maxi:
                        maxi = len(gt[gtkey])
                        maxt = gtkey
                    print("TRUE GROUND TRUTH:{}, msgnum:{}, total:{}".format(gtkey, len(gt[gtkey]),MTP))

                    if gtkey[0] == 's':
                        EVENT[0] += 1
                        EVENT[1] += len(gt[gtkey])
                    elif gtkey[0] == 'm':
                        TEXT[0] += 1
                        TEXT[1] += len(gt[gtkey])
                    else:
                        TABLE[0] += 1
                        TABLE[1] += len(gt[gtkey])
                    break
        if analysis:
            if not f:
                print("WRONG GROUND TRUTH:{}, msgnum:{}".format(gtkey, len(gt[gtkey])))

    if analysis:
        print("Correct message number:{}".format(MTP))
        print("total message number:{}".format(ln))
        print("Biggest message number:{}".format(maxi))
        print("Biggest message ID:{}".format(maxt))
        print(EVENT, TEXT, TABLE)

    GMA = MTP / ln                  # group message accuracy
    GTR = TTP / len(gt.keys())      # group template recall
    GTP = TTP / len(pd.keys())      # group template precision
    try:
        GTF1 = 2 * GTP * GTR / (GTP + GTR)  # group template f1 score
    except:
        GTF1 = 0

    return GMA, GTR, GTP, GTF1 
