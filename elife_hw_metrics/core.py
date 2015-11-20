__author__ = [
    'Luke Skibinski <l.skibinski@elifesciences.org>',
]

from os.path import join
from collections import Counter
import os, sys, json, glob
from pprint import pprint
import csv
import logging
from datetime import datetime
from collections import OrderedDict
import calendar

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.level = logging.INFO

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = join(THIS_DIR, 'output')

INCEPTION = datetime(year=2012, month=12, day=1)

def intorbust(x):
    "returns value cast to an integer if possible, else the original value"
    try:
        return int(x)
    except (ValueError, TypeError):
        try:
            return int(float(x))
        except (ValueError, TypeError):
            return x

def exsubdict(d, kl):
    "returns a map excluding those items whose keys are in kl"
    return {k:v for k, v in d.items() if k not in kl}

def dictmap(f, d):
    "returns new map where f has been applied to every value"
    return {k:f(v) for k, v in d.items()}

def format_date(val):
    "takes an unseparated month or day date value and returns a version separated by hyphens"
    if len(val) == 6:
        # monthly
        return "%s-%s" % (val[:4], val[4:])
    if len(val) == 8:
        # daily
        return "%s-%s-%s" % (val[:4], val[4:6], val[6:8])
    raise ValueError("unhandled date format for value %r" % val)

def write_results(key, grouped_results):
    grouped_results.sort(key=lambda r: r['doi'])
    path = join(OUTPUT_DIR, key + ".json")
    json.dump(grouped_results, open(path, 'w'), indent=4, sort_keys=True)
    LOG.info('wrote %s', path)
    return path

def write_groups(results):
    return [write_results(key, group.values()) for key, group in results.items()]

def grouper(fname):
    return 'daily' if len(fname) == 15 else 'monthly'

def metrics_paths():
    results = OrderedDict({})
    for fname in os.listdir(OUTPUT_DIR):
        key = grouper(fname)
        group = results.get(key, [])
        group.append(join(OUTPUT_DIR, fname))
        results[key] = group
    return results

def in_range(dt, from_date, to_date):
    return dt >= from_date and dt <= to_date

def fname_to_dt(path):
    dt = os.path.basename(path)
    dt = os.path.splitext(dt)[0]
    if len(dt) == 7:
        dt = dt + "-01" # monthly dt
    return datetime.strptime(dt, "%Y-%m-%d")

def metrics_between(from_date=None, to_date=None, period='daily'):
    "returns a list of row data for the given time range and period type"
    if not from_date:
        from_date = INCEPTION

    if not to_date:
        # don't import today's partial results. they're available but lets wait until tomorrow
        to_date = datetime.now()

    if period == 'monthly':
        from_date = datetime(year=from_date.year, month=from_date.month, day=1)
        to_date = datetime(year=to_date.year, month=to_date.month, day=\
                           calendar.monthrange(year=to_date.year, month=to_date.month)[0])

    # figure out 
    path_list = metrics_paths().get(period, [])
    path_list = filter(lambda path: in_range(fname_to_dt(path), from_date, to_date), path_list)
    results = OrderedDict({})
    for path in path_list:
        dt_key = os.path.splitext(os.path.basename(path))[0]
        group = results.get(dt_key, [])
        group.extend(json.load(open(path, 'r')))
        results[dt_key] = group
    return results


def parse(fname, results={}):
    print 'processing file',fname
    with open(fname, 'r') as csvfile:
        header = map(lambda s: s.strip('"').strip(), csvfile.readline().split(","))
        reader = csv.DictReader(csvfile, delimiter=",", quotechar='"', fieldnames=header)
        #results={}
        for row in reader:
            # nid == node id, not used
            # html == full + abstract
            # source == always null/hw
            # type == always null
            # xml == always 0
            row = exsubdict(row, ['nid', 'html', 'source', 'type', 'xml'])
            row['date'] = format_date(row['date'])
            row = dictmap(intorbust, row)

            group_key = row['date']
            row_key = row['doi']
            
            group = results.get(group_key, {})
            if group.has_key(row_key):
                try:
                    assert group[row_key] == row, "inequal duplicate found in %s:\nold:%s\nnew:%s\n" % (fname, group[row_key], row)
                except Exception, e:
                    print e
                    print 'using most recent result'
            group[row_key] = row
            results[group_key] = group
        return results

#
# bootstrap
#

def parse_hw_files():
    file_list = sorted(glob.glob("hw_stats.*.csv"))
    results = {}
    for f in file_list:
        results = parse(f, results)
    return write_groups(results)

def main(args):
    "takes the csv file and outputs a chunked version"
    if not os.path.exists(OUTPUT_DIR):
        assert os.system("mkdir -p %s" % OUTPUT_DIR) == 0, "failed to make output dir %r" % OUTPUT_DIR
    return parse_hw_files()

if __name__ == '__main__':
    main(sys.argv[1:])
