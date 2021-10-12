## Installation

This repository just contains standalone scripts. Make sure to install requirements before running:

```
pip install -r requirements.txt
```

## Expected format

HiGlass expects the gene annotations file to have following format:

```
# 1: chr (chr1)
# 2: txStart (52301201) [9]
# 3: txEnd (52317145) [10]
# 4: geneName (ACVRL1)   [2]
# 5: citationCount (123) [16]
# 6: strand (+)  [8]
# 7: refseqId (NM_000020)
# 8: geneId (94) [1]
# 9: geneType (protein-coding)
# 10: geneDesc (activin A receptor type II-like 1)
# 11: cdsStart (52306258)
# 12: cdsEnd (52314677)
# 13: exonStarts (52301201,52306253,52306882,52307342,52307757,52308222,52309008,52309819,52312768,52314542,)
# 14: exonEnds (52301479,523063
```

This bed-like format then needs to be aggregated using `clodius aggregate bedfile` in order to limit the amount of data displayed at once and to enable searching by gene name.

## Example 1: From UCSC GTF file

1. Download the UCSC `gtfToGenePred` binary from http://hgdownload.soe.ucsc.edu/admin/exe/

2. Get the GTF and chromsizes files for an assembly (the `-NP .` parameters ensure that a file isn't downloaded if it's already present) and convert to genepred format:

```
wget -NP . https://hgdownload.soe.ucsc.edu/goldenPath/danRer10/bigZips/genes/danRer10.refGene.gtf.gz
wget -NP . https://hgdownload.soe.ucsc.edu/goldenPath/danRer10/bigZips/danRer10.chrom.sizes
gtfToGenePred -genePredExt -geneNameAsName2 danRer10.refGene.gtf.gz danRer10.refGene.genepred
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
