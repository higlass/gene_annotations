#!/bin/bash


if [[ $# -ne 3 ]]; then
    echo "Usage ./gene_annotations.sh ASSEMBLY TAXID BASE_DIR";
    exit 1;
fi

set -x
set -e

ASSEMBLY=$1
TAXID=$2
BASE_DIR=$3
echo "ASSEMBLY: $ASSEMBLY"

mkdir -p ${BASE_DIR}/${ASSEMBLY}
wget -N -P${BASE_DIR}/${ASSEMBLY}/ \
    http://hgdownload.cse.ucsc.edu/goldenPath/${ASSEMBLY}/database/xenoRefGene.txt.gz
    # remove entries to chr6_...
gzcat ${BASE_DIR}/${ASSEMBLY}/xenoRefGene.txt.gz \
    | awk -F $'\t' '{if (!($3 ~ /_/)) print;}' \
    | sort -k2 > ${BASE_DIR}/${ASSEMBLY}/sorted_refGene
wc -l ${BASE_DIR}/${ASSEMBLY}/sorted_refGene


wget -N -P ${BASE_DIR}/ \
    ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2refseq.gz
zgrep ^${TAXID} ${BASE_DIR}/gene2refseq.gz \
     > ${BASE_DIR}/${ASSEMBLY}/gene2refseq
head ${BASE_DIR}/${ASSEMBLY}/gene2refseq
# output -> geneid \t refseq_id
cat ${BASE_DIR}/${ASSEMBLY}/gene2refseq \
    | awk -F $'\t' '{ split($4,a,"."); if (a[1] != "-") print $2 "\t" a[1];}' \
    | sort \
    | uniq  \
    > ${BASE_DIR}/${ASSEMBLY}/geneid_refseqid
head ${BASE_DIR}/${ASSEMBLY}/geneid_refseqid
wc -l ${BASE_DIR}/${ASSEMBLY}/geneid_refseqid


wget -N -P ${BASE_DIR}/ \
    ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz
zgrep ^${TAXID} ${BASE_DIR}/gene_info.gz \
    | sort -k 2 \
     > ${BASE_DIR}/${ASSEMBLY}/gene_info
head ${BASE_DIR}/${ASSEMBLY}/gene_info

wget -N -P ${BASE_DIR}/ \
    ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2pubmed.gz
zgrep ^${TAXID} ${BASE_DIR}/gene2pubmed.gz \
    > ${BASE_DIR}/${ASSEMBLY}/gene2pubmed
head ${BASE_DIR}/${ASSEMBLY}/gene2pubmed
cat ${BASE_DIR}/${ASSEMBLY}/gene2pubmed \
    | awk '{print $2}' \
    | sort \
    | uniq -c \
    | awk '{print $2 "\t" $1}' \
    | sort \
    > ${BASE_DIR}/${ASSEMBLY}/gene2pubmed-count
head ${BASE_DIR}/${ASSEMBLY}/gene2pubmed-count

# awk '{print $2}' ${BASE_DIR}/hg19/gene_info \
# | xargs python scripts/gene_info_by_id.py \
# | tee ${BASE_DIR}/hg19/gene_summaries.tsv
# output -> geneid \t citation_count


#output -> geneid \t refseq_id \t citation_count
join ${BASE_DIR}/${ASSEMBLY}/geneid_refseqid \
    ${BASE_DIR}/${ASSEMBLY}/gene2pubmed-count  \
    | sort -k2 \
    > ${BASE_DIR}/${ASSEMBLY}/geneid_refseqid_count
head ${BASE_DIR}/${ASSEMBLY}/geneid_refseqid_count
wc -l ${BASE_DIR}/${ASSEMBLY}/geneid_refseqid_count
# output -> geneid \t refseq_id \t chr (5) \t strand(6) \t txStart(7) \t txEnd(8) \t cdsStart(9) \t cdsEnd (10) \t exonCount(11) \t exonStarts(12) \t exonEnds(13)
join -1 2 -2 2 \
    ${BASE_DIR}/${ASSEMBLY}/geneid_refseqid_count \
    ${BASE_DIR}/${ASSEMBLY}/sorted_refGene \
    | awk '{ print $2 "\t" $1 "\t" $5 "\t" $6 "\t" $7 "\t" $8 "\t" $9 "\t" $10 "\t" $11 "\t" $12 "\t" $13 "\t" $3; }' \
    | sort -k1   \
    > ${BASE_DIR}/${ASSEMBLY}/geneid_refGene_count
head ${BASE_DIR}/${ASSEMBLY}/geneid_refGene_count
wc -l ${BASE_DIR}/${ASSEMBLY}/geneid_refGene_count
# output -> geneid \t symbol \t gene_type \t name \t citation_count
join -1 2 -2 1 -t $'\t' \
    ${BASE_DIR}/${ASSEMBLY}/gene_info \
    ${BASE_DIR}/${ASSEMBLY}/gene2pubmed-count \
    | awk -F $'\t' '{print $1 "\t" $3 "\t" $10 "\t" $12 "\t" $16}' \
    | sort -k1 \
    > ${BASE_DIR}/${ASSEMBLY}/gene_subinfo_citation_count
head ${BASE_DIR}/${ASSEMBLY}/gene_subinfo_citation_count
wc -l ${BASE_DIR}/${ASSEMBLY}/gene_subinfo_citation_count
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
# 14: exonStarts (52301201,52306253,52306882,52307342,52307757,52308222,52309008,52309819,52312768,52314542,)
# 15: exonEnds (52301479,52306319,52307134,52307554,52307857,52308369,52309284,52310017,52312899,52317145,)
join -t $'\t' \
    ${BASE_DIR}/${ASSEMBLY}/gene_subinfo_citation_count \
    ${BASE_DIR}/${ASSEMBLY}/geneid_refGene_count \
    | awk -F $'\t' '{print $7 "\t" $9 "\t" $10 "\t" $2 "\t" $16 "\t" $8 "\t" $6 "\t" $1 "\t" $3 "\t" $4 "\t" $11 "\t" $12 "\t" $14 "\t" $15}' \
    > ${BASE_DIR}/${ASSEMBLY}/geneAnnotations.bed
head ${BASE_DIR}/${ASSEMBLY}/geneAnnotations.bed
wc -l ${BASE_DIR}/${ASSEMBLY}/geneAnnotations.bed
python scripts/exonU.py \
    ${BASE_DIR}/${ASSEMBLY}/geneAnnotations.bed \
    > ${BASE_DIR}/${ASSEMBLY}/geneAnnotationsExonUnions.bed
wc -l ${BASE_DIR}/${ASSEMBLY}/geneAnnotationsExonUnions.bed
