#!/usr/bin/python

import argparse
import gzip
import itertools as it
import json
import logging
import sys
from typing import Any, Dict, List, Literal, Optional, Union

import pydantic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    python gjsonl_to_chromsizes.py
""")

    parser.add_argument('input_file')
    #parser.add_argument('-o', '--options', default='yo',
    #                    help="Some option", type='str')
    #parser.add_argument('-u', '--useless', action='store_true',
    #                    help='Another useless option')

    args = parser.parse_args()

    if args.input_file == '-':
        f = sys.stdin
    elif args.input_file.endswith('.gz'):
        f = gzip.open(args.input_file, 'r')
    else:
        f = open(args.input_file, 'r')

    chrom_names = {}

    for line in f:
        record = GFFRecord(**json.loads(line))

        if record.annotation_type == 'region':
            if 'chromosome' in record.attributes:
                print(f"chr{record.attributes['chromosome']}\t{record.end}")


if __name__ == '__main__':
    main()
