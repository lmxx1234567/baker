#!/usr/bin/env python
import argparse
import json

import case_parsers
from const import attrs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Legal document parser')
    parser.add_argument(
        'attr', help='Which attributes to resolve', choices=attrs)
    parser.add_argument('filepath', help='Path to legal document')
    args = parser.parse_args()
    lines = []
    with open(args.filepath, encoding='UTF-8') as f:
        lines = f.readlines()

    if args.attr == 'all':
        field_dict = {}
        for attr in attrs[1:]:
            try:
                func = getattr(case_parsers, 'get_'+attr)
                ret = func(lines)
                field_dict[attr] = ret
            except Exception:
                field_dict[attr] = None
        print(json.dumps(field_dict, ensure_ascii=False))
    elif args.attr in attrs:
        func = getattr(case_parsers, 'get_'+args.attr)
        print(func(lines))
