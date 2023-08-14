import Hue

log = 'HiBench_4k.log' # default
feedback = False # whether to enable feedback query
analysis = False # whether to analysis for all templates

idir = '../../datasets/' + log + '/'
odir = '../../results/' + log + '/'

parser = Hue.Parser(idir, odir, config=idir + 'config.yml',feedback=feedback)
parser.parse(log)
parser.print()

gt = idir + log + '_structured.log'
pd = odir + 'meta.log'