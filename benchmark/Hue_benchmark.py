

import sys
sys.path.append('')
import time
from parsers import Hue
from parsers.Hue.utils import *

# traditional_logs = ['HDFS', 'Spark', 'BGL', 'Windows', 'Linux', 'Andriod', 'Mac', 'Hadoop', 'HealthApp', 'OpenSSH', 'Thunderbird', 'Proxifier', 'Apache', 'HPC', 'Zookeeper', 'OpenStack']
traditional_logs = []
hybrid_logs = ['HiBench', 'CTS']
logs = traditional_logs + hybrid_logs
feedback = False # whether to enable feedback query
acclist = []
meanacc, meanf1 = 0, 0

begintime = time.time()
for log in logs:
    print("Parsing log dataset: {}".format(log))
    idir = 'datasets/' + log +'/'
    odir = 'results/' + log + '/'

    parser = Hue.Parser(idir, odir, config='parsers/Hue/config_' + log + '.yml',feedback=feedback)
    parser.parse(log + '_2k.log')
    parser.print()

    gt = idir + log + '_2k.log_structured.log'
    pd = odir + 'meta.log'
    ans = evaluate(gt, pd, analysis=False)
    meanacc += ans[0]
    meanf1 += ans[3]
    acclist.append("Dataset: {}\tAccuracy: {:.4f}\tRecall: {:.4f}\tPrecision: {:.4f}\tF1-Score: {:.4f}".format(log, ans[0], ans[1], ans[2], ans[3]))
endtime = time.time()
print("Total time = {}s".format(endtime-begintime))
for acc in acclist:
    print(acc)
