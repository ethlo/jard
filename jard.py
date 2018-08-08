import csv, os
from subprocess import call
import pprint
import argparse
pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description='Extract results from JMeter CSV files')
parser.add_argument('--dir', type=str, required=True, help='The directory to read result files from')
parser.add_argument('--delta', type=int, default=2, help="The interval results should be calculated in seconds")
parser.add_argument('--splits', help='Comma-separated pairs of time ranges (seconds) to slice the results at', type=str, default='0,99999999')
parser.add_argument('--summary', const=True, help='Summary only', action='store_const')
args = vars(parser.parse_args())

directory = args['dir']
delta = args['delta']
ranges = [int(item) for item in args['splits'].split(',')]

def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0

def process_file(filepath):
	res = []
	with open(filepath, "rb") as f:
	    reader = csv.reader(f, delimiter=",")
	    next(reader, None)
	    count = 0
	    last = 0
	    for i, line in enumerate(reader):
		ts = int(line[0])
		if (ts - last > 1000):
			res.append(count)
			last = ts
			count = 0
		else:
			count+=1
	return res

results = {}
for filename in os.listdir(directory):
	f = os.path.join(directory, filename)
	call(['sort', '-o' + f, '-k1', '-n', '-t,', f])
    	if filename.endswith(".dat") or filename.endswith(".csv"):
		res = process_file(f)
		results[filename] = res
#pp.pprint(results)
file_count = len(results)

rows = len(next(iter(results.values())))
for start,end in zip(ranges[0::2], ranges[1::2]):
	print start,end
	print '# Elapsed,', ','.join(str(v) for v in sorted(results.keys()))
	elapsed = start
	sumVal = dict((el,0) for el in results.keys())
	maxVal = dict((el,0) for el in results.keys())
	for row in xrange(start, end + delta):
		r = []
		for filename, data in sorted(results.iteritems()):
			val = results[filename][row];
			sumVal[filename] += val
			maxVal[filename] = max(val, maxVal[filename])
			r.append(val)
		if elapsed % delta == 0 and not args['summary']:
			print str(elapsed) + ',' + (','.join(str(v) for v in r))

		elapsed += 1

	print '# Total'	
	print '#', ','.join(str(v) for v in sorted(results.keys()))
	print ','.join(str(a) for a in sumVal.values())

	print '# Max'
	print '#', ','.join(str(v) for v in sorted(results.keys()))
	print ','.join(str(a) for a in maxVal.values())

	print '# Average'
	print '#', ','.join(str(v) for v in sorted(results.keys()))
	avg = {}
	for k,v in sumVal.iteritems():
		avg[k] = ("%.2f" % (v / (float(end - start))))	
	print ','.join(str(a) for a in avg.values())
