__author__ = [
    'Luke Skibinski <l.skibinski@elifesciences.org>',
]

from os.path import join
from collections import Counter
import os, sys, json
from pprint import pprint
import csv
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.level = logging.INFO

OUTPUT_DIR = join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')

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
    return path

def write_groups(results):
    return [write_results(key, group) for key, group in results.items()]

def foo(fname):
    with open(fname, 'r') as csvfile:
        header = map(lambda s: s.strip('"').strip(), csvfile.readline().split(","))
        reader = csv.DictReader(csvfile, delimiter=",", quotechar='"', fieldnames=header)
        results = {}
        for row in reader:
            row = exsubdict(row, ['nid', 'html', 'source', 'type'])
            row['date'] = format_date(row['date'])

            key = row['date']
            
            group = results.get(key, [])
            group.append(row)
            results[key] = group
        paths = write_groups(results)
        for path in paths:
            print 'wrote',path
        




#
# bootstrap
#

def main(args):
    assert len(args) > 0, "a path to dump.csv file is required"
    if not os.path.exists(OUTPUT_DIR):
        assert os.system("mkdir -p %s" % OUTPUT_DIR) == 0, "failed to make output dir %r" % dirname

    return foo(args[0])

if __name__ == '__main__':
    main(sys.argv[1:])
