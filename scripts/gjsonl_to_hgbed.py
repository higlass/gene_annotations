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

class HGExon(pydantic.BaseModel):
    start: int
    end: int

class HGRecord(pydantic.BaseModel):
    chrom: str
    start: int
    end: int
    name: str
    score: float
    strand: Literal['+','-','.']
    transcript_id: str
    gene_id: str
    gene_type: str
    description: str
    cds_start: int
    cds_end: int
    exons: List[HGExon]


GFFRecord.update_forward_refs()

def intersect(exon1, exon2):
    """Return true if these exons intersect, otherwise return false."""
    if exon1.start <= exon2.end and exon1.end >= exon2.start:
        return True

    return False

def merge_exons(exons):
    """Merge a set of exons so that overlapping entries are consolidated."""
    merged = True

    while merged:
        merged = False
        for exon1, exon2 in it.combinations(exons, 2):
            if intersect(exon1, exon2):
                new_exon = HGExon(
                        start = min(exon1.start, exon2.start),
                        end = max(exon1.end, exon2.end)
                    )

                merged = True
                exons.remove(exon1)
                exons.remove(exon2)
                exons.append(new_exon)
                break
    return exons

def merge_mrnas(gene):
    """Merge the exons of the mrnas."""
    mrnas = [r for r in gene.children if r.annotation_type == 'mRNA']

    if len(mrnas) == 0:
        # logger.warning("No mrnas found: %s", gene)
        return

    cds = [r for r in mrnas[0].children if r.annotation_type == 'CDS']

    if len(cds) == 0:
        logger.warning("No cds found for mrna: %s", mrnas[0])
        return

    hg_record = HGRecord(
        chrom= gene.chrom,
        start= gene.start,
        end= gene.end,
        name= gene.attributes['Name'],
        score=0,
        strand=gene.strand,
        transcript_id=f"union_{gene.attributes['ID']}" ,
        gene_id=gene.attributes['ID'],
        gene_type='gene',
        description=mrnas[0].attributes['product'],
        cds_start=cds[0].start,
        cds_end=cds[0].end,
        exons=[]
    )

    for mrna in mrnas:
        cds = [r for r in mrnas[0].children if r.annotation_type == 'CDS']

        hg_record.cds_start = min(cds[0].start, hg_record.cds_start)
        hg_record.cds_end = max(cds[0].end, hg_record.cds_end)

        exons = [r for r in mrna.children if r.annotation_type == 'exon']

        hg_record.exons += exons
    
    hg_record.exons = merge_exons(hg_record.exons)

    return hg_record    

def main():
    parser = argparse.ArgumentParser(description="""

    python gjsonl_to_hgbed.py
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

        if record.annotation_type == 'gene':
            merged = merge_mrnas(record)
            if merged:
                print("\t".join(map(str,
                    [
                        chrom_names[merged.chrom],
                        merged.start,
                        merged.end,
                        merged.name,
                        merged.score,
                        merged.strand,
                        merged.transcript_id,
                        merged.gene_id,
                        merged.gene_type,
                        merged.description,
                        merged.cds_start,
                        merged.cds_end,
                        ",".join([str(e.start) for e in merged.exons]),
                        ",".join([str(e.end) for e in merged.exons])
                    ])))
        elif record.annotation_type == 'region':
            if 'chromosome' in record.attributes:
                chrom_names[record.chrom] = f"chr{record.attributes['chromosome']}"


if __name__ == '__main__':
    main()
