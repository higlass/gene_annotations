#!/usr/bin/python

import argparse
import gzip
import json
import sys
from typing import Any, Dict, List, Literal, Optional, Union

import pydantic


class GFFRecord(pydantic.BaseModel):
    chrom: str
    source: str
    annotation_type: str
    start: int
    end: int
    score: Union[str,int]
    strand: Literal['+','-','.']
    phase: Union[int, Literal['.']]
    attributes: Dict[str,Any]
    children: List['GFFRecord'] = []

GFFRecord.update_forward_refs()

def main():
    parser = argparse.ArgumentParser(description="""

    python gff_to_jsonl.py
""")

    parser.add_argument('gff')
    #parser.add_argument('-o', '--options', default='yo',
    #                    help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true',
    #                    help='Another useless option')

    args = parser.parse_args()

    if args.gff == '-':
        f = sys.stdin
    elif args.gff.endswith('.gz'):
        f = gzip.open(args.gff, 'rt')
    else:
        f = open(args.gff, 'r')

    records = {}

    for line in f:
        if line.startswith('#'):
            continue
        
        parts = dict(zip(
            ("chrom", "source", "annotation_type", "start", "end", "score", "strand", "phase", "attributes"),
            line.strip().split('\t')
        ))
        parts['attributes'] = dict([p.split('=') for p in parts['attributes'].split(';')])
        
        record = GFFRecord(**parts)
        records[record.attributes['ID']] = record

        if 'Parent' in record.attributes:
            records[record.attributes['Parent']].children.append(record)

    top_level_records = [r for r in records.values() if 'Parent' not in r.attributes]
    for record in top_level_records:
        print(record.json())


if __name__ == '__main__':
    main()
