#!/usr/bin/python

import argparse
import gzip
import json
import logging
import sys
from typing import Any, Dict, List, Literal, Optional, Union

import pydantic
from smart_open import open

logging.basicConfig(level=logging.DEBUG)


class GFFRecord(pydantic.BaseModel):
    chrom: str
    source: str
    annotation_type: str
    start: int
    end: int
    score: Union[str, int]
    strand: Literal["+", "-", "."]
    phase: Union[int, Literal["."]]
    attributes: Dict[str, Any]
    children: List["GFFRecord"] = []


GFFRecord.update_forward_refs()


def main():
    parser = argparse.ArgumentParser(
        description="""

    python gff_to_jsonl.py
"""
    )

    parser.add_argument("gff")
    parser.add_argument(
        "-s", "--attribute-separator", default="=", help="Some option", type=str
    )

    # parser.add_argument('-u', '--useless', action='store_true',
    #                    help='Another useless option')

    args = parser.parse_args()

    if args.gff == "-":
        f = sys.stdin
    else:
        f = open(args.gff, "r")

    records = {}

    for line_num, line in enumerate(f):
        if line.startswith("#"):
            continue

        if line_num % 1000 == 0:
            logging.info("\rProcessing line #: %d", line_num)

        parts = dict(
            zip(
                (
                    "chrom",
                    "source",
                    "annotation_type",
                    "start",
                    "end",
                    "score",
                    "strand",
                    "phase",
                    "attributes",
                ),
                line.strip().split("\t"),
            )
        )

        try:
            attributes_array = [
                [at.strip('"') for at in p.strip().split(args.attribute_separator)]
                for p in parts["attributes"].strip(";").split(";")
            ]

            parts["attributes"] = dict(attributes_array)
        except ValueError as ve:
            logging.error(
                "Can't parse attributes. Make sure the --attribute-separator is set correctly."
            )
            logging.error("Error text: %s", str(ve))
            logging.error("attributes_array: %s", str(attributes_array))
            logging.error("Offending line: %s", line)
            return

        record = GFFRecord(**parts)
        if "ID" in record.attributes:
            records[record.attributes["ID"]] = record

        if "Parent" in record.attributes:
            parent = record.attributes["Parent"]

            if len(parent.split(",")) > 1:
                parent = parent.split(",")[0]

            parent_rec = records[parent]
            parent_rec.children.append(record)

    top_level_records = [r for r in records.values() if "Parent" not in r.attributes]
    for record in top_level_records:
        print(record.json())


if __name__ == "__main__":
    main()
