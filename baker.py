#!/usr/bin/env python
import argparse
import json

from case_parsers import case_info

attrs = ['all', 'case_name', 'case_id', 'year', 'cause', 'trial_procedure',
         'case_type', 'court', 'document_type', 'judge', 'clerk', 'case_summary']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Legal document parser')
    parser.add_argument(
        'attr', help='Which attributes to resolve', choices=attrs)
    parser.add_argument('filepath', help='Path to legal document')
    args = parser.parse_args()
    lines = []
    with open(args.filepath) as f:
        lines = f.readlines()

    if args.attr == 'all':
        field_dict = {}
        for attr in attrs[1:]:
            module = __import__('case_parsers', fromlist=[
                                'case_info']).case_info
            func = getattr(module, 'get_'+attr)
            ret = func(lines)
            field_dict[attr] = ret
        print(json.dumps(field_dict, ensure_ascii=False))
    elif args.attr == 'case_name':
        print(case_info.get_case_name(lines))
    elif args.attr == 'case_id':
        print(case_info.get_case_id(lines))
    elif args.attr == 'year':
        print(case_info.get_year(lines))
    elif args.attr == 'cause':
        print(case_info.get_cause(lines))
    elif args.attr == 'trial_procedure':
        print(case_info.get_trial_procedure(lines))
    elif args.attr == 'case_type':
        print(case_info.get_case_type(lines))
    elif args.attr == 'court':
        print(case_info.get_court(lines))
    elif args.attr == 'document_type':
        print(case_info.get_document_type(lines))
    elif args.attr == 'judge':
        print(case_info.get_judge(lines))
    elif args.attr == 'clerk':
        print(case_info.get_clerk(lines))
    elif args.attr == 'case_summary':
        print(case_info.get_case_summary(lines))
