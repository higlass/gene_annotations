## Installation

This repository just contains standalone scripts. Make sure to install requirements before running:

```
pip install -r requirements.txt
```

## Example 1: From UCSC GTF file

1. Download the UCSC `gtfToGenePred` binary from http://hgdownload.soe.ucsc.edu/admin/exe/

2. Get the GTF and chromsizes files for an assembly (the `-NP .` parameters ensure that a file isn't downloaded if it's already present)


```
https://hgdownload.soe.ucsc.edu/goldenPath/danRer10/bigZips/genes/danRer10.refGene.gtf.gz
wget -NP . https://hgdownload.soe.ucsc.edu/goldenPath/danRer10/bigZips/danRer10.chrom.sizes
```

3. Convert to higlass-compatible format:


```
cat danRer10.refGene.genepred | python genepredext_to_hgbed.py | python exonU.py - > danRer10.refGene.hgbed
clodius aggregate bedfile --chromsizes-filename danRer10.chrom.sizes danRer10.refGene.hgbed
```

4. Use in either HiGlass or Resgen using `filetype:beddb`, `datatype:gene-annotations`.


## Example 2: From NCBI GFF

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

