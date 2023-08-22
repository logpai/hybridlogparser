

import sys
sys.path.append('')
from parsers import Hue

feedback = False # whether to enable feedback query
idir = 'datasets/HiBench/'
odir = 'results/Hue_result/'
parser = Hue.Parser(idir, odir, config='parsers/Hue/config_HiBench.yml',feedback=feedback)
parser.parse('HiBench_2k.log')
parser.print()

gt = '../../datasets/HiBench/HiBench_2k.log_structured.log'
pd = odir + 'meta.log'