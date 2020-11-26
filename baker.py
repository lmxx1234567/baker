#!/usr/bin/env python
import argparse
import json
from case_parsers import case_info

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Legal document parser')
    parser.add_argument(
        'attr', help='Which attributes to resolve', choices=['casename', 'caseid'])
    parser.add_argument('filepath', help='Path to legal document')
    args = parser.parse_args()
    lines = []
    with open(args.filepath) as f:
        lines = f.readlines()

    if args.attr == 'casename':
        print(case_info.get_case_name(lines))
    elif args.attr == 'caseid':
        print(case_info.get_case_id(lines))
