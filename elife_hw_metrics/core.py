__author__ = [
    'Luke Skibinski <l.skibinski@elifesciences.org>',
]

from os.path import join
from collections import Counter
import os, sys, json
from pprint import pprint
import csv
import logging
from datetime import datetime
from collections import OrderedDict
import calendar

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.level = logging.INFO

#OUTPUT_DIR = join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
OUTPUT_DIR = '/var/metrics/hw/output/'

INCEPTION = datetime(year=2012, month=12, day=1)

def exsubdict(d, kl):
    return {k:v for k, v in d.items() if k not in kl}

def format_date(val):
    if len(val) == 6:
        # monthly
        return "%s-%s" % (val[:4], val[4:])
    if len(val) == 8:
        # daily
        return "%s-%s-%s" % (val[:4], val[4:6], val[6:8])
    raise ValueError("unhandled date format for value %r" % val)

def write_results(key, grouped_results):
    grouped_results.sort(key=lambda r: r['date'])
    path = join(OUTPUT_DIR, key + ".json")
    json.dump(grouped_results, open(path, 'w'), indent=4, sort_keys=True)
    LOG.debug('wrote %s', path)
    return path

def write_groups(results):
    return [write_results(key, group) for key, group in results.items()]

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


#
# bootstrap
#

def main(args):
    "takes the csv file and outputs a chunked version"
    assert len(args) > 0, "a path to dump.csv file is required"
    if not os.path.exists(OUTPUT_DIR):
        assert os.system("mkdir -p %s" % OUTPUT_DIR) == 0, "failed to make output dir %r" % OUTPUT_DIR

    fname = args[0]
    with open(fname, 'r') as csvfile:
        header = map(lambda s: s.strip('"').strip(), csvfile.readline().split(","))
        reader = csv.DictReader(csvfile, delimiter=",", quotechar='"', fieldnames=header)
        results = {}
        for row in reader:
            # nid == node id, not used
            # html == full + abstract
            # source == always null/hw
            # type == always null
            # xml == always 0
            row = exsubdict(row, ['nid', 'html', 'source', 'type', 'xml'])
            row['date'] = format_date(row['date'])

            key = row['date']
            
            group = results.get(key, [])
            group.append(row)
            results[key] = group
        return write_groups(results)

if __name__ == '__main__':
    main(sys.argv[1:])
