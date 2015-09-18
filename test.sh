#!/bin/bash
source install.sh > /dev/null
pylint2 -E elife_hw_metrics/*.py
#python -m unittest --verbose --failfast --catch elife_hw_metrics.test.tests
