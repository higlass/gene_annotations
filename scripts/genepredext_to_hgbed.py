#!/usr/bin/python

import argparse
import sys
from hashlib import sha256


def main():
    parser = argparse.ArgumentParser(
        description="""

    python genepredext_to_hgbed
"""
    )
    f = sys.stdin

    for line in f:
        parts = line.split("\t")
        geneName = parts[11]
        score = int(sha256(geneName.encode("utf8")).hexdigest()[:5], 16)  # pseudoscore

        print(
            "\t".join(
                [
                    str(x)
                    for x in [
                        parts[1],  # chr
                        parts[3],  # txStart
                        parts[4],  # txEnd
                        geneName,  # geneName
                        score,
                        parts[2],  # strand
                        parts[0],  # transcript_id
                        parts[11],  # gene id
                        "gene",  # gene type
                        f"{parts[10]}_desc",
                        parts[5],  # cdsStart
                        parts[6],  # cdsEnd
                        parts[8],  # exonStarts
                        parts[9],  # exonEnds
                    ]
                ]
            )
        )

    # parser.add_argument('argument', nargs=1)
    # parser.add_argument('-o', '--options', default='yo',
    #                    help="Some option", type='str')
    # parser.add_argument('-u', '--useless', action='store_true',
    #                    help='Another useless option')

    args = parser.parse_args()


if __name__ == "__main__":
    main()
