## Installation

This repository just contains standalone scripts. Make sure to install requirements before running:

```
pip install -r requirements.txt
```

## Usage by example

Find the genome information page for sacCer3 at https://www.ncbi.nlm.nih.gov/assembly/GCF_000146045.2/.

Download the gff file by clicking on "Download Assembly" and selecting "Genomic GFF".

Convert to higlass-compatible format using these commands:

```
gzcat GCF_000146045.2_R64_genomic.gff.gz \
	| python scripts/gff_to_jsonl.py - \
	| python scripts/gjsonl_to_chromsizes.py - > sacCer3.chrom.sizes

gzcat GCF_000146045.2_R64_genomic.gff.gz \
	| python scripts/gff_to_jsonl.py - \
	| python scripts/gjsonl_to_hgbed.py - > sacCer3.hgbed

clodius aggregate bedfile sacCer3.hgbed \
	--delimiter $`\t' \
	--chromsizes-filename sacCer3.chrom.sizes
```

The `sacCer2.chrom.sizes` file just contains the names of the chromosomes and their sizes.

View in higlass:

```
higlass-manage view sacCer3.hgbed.beddb --datatype gene-annotations
```

Note that this process omits all RNAs and takes the union of all exons in a gene to represent it as if it were just one transcript.

