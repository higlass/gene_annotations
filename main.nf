// Script parameters

params.chromSizesUrl = "https://hgdownload.soe.ucsc.edu/goldenPath/oryCun2/bigZips/oryCun2.chrom.sizes"
// params.gtfUrl = "https://hgdownload.soe.ucsc.edu/goldenPath/oryCun2/bigZips/genes/oryCun2.ncbiRefSeq.gtf.gz"
params.gtfUrl = "https://www.genoscope.cns.fr/externe/plants/data/Musa_acuminata_pahang_v4.gff"

// chromSizesChannel = Channel.from(params.chromSizesUrl)
// gtfChannel = Channel.from(params.gtfUrl)

process fetchFiles {
    input:
        val params.chromSizesUrl
        val params.gtfUrl

    output:
        file "*.chrom.sizes" into chromsizes
        file "*.gtf" into gtf
    """
    wget $params.gtfUrl
    wget $params.chromSizesUrl
    gunzip *.gz
    """
}

process sortChromSizes {
    publishDir 'results'
    
    input:
        file chromsizes

    output:
        file "*.sorted.chrom.sizes" into sortedChromsizes

    """
    gsort -k1,1 -V -s $chromsizes > ${chromsizes.simpleName}.sorted.chrom.sizes
    """
}

process gtfToGenePred {
    input: 
        file gtf

    output:
        file "*.genepred" into genepred

    """
    gtfToGenePred -genePredExt -geneNameAsName2 $gtf ${gtf.baseName}.genepred
    """
}

process exonUnions {
    publishDir 'results'

    input:
        file sortedChromsizes
        file genepred

    output:
        file "*.beddb"

    """
    cat ${genepred} | python ${workflow.projectDir}/scripts/genepredext_to_hgbed.py | python ${workflow.projectDir}/scripts/exonU.py - > ${genepred.baseName}.hgbed
    clodius aggregate bedfile --chromsizes-filename $sortedChromsizes ${genepred.baseName}.hgbed
    """
}
