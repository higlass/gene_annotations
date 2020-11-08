## Example

```
gzcat GCF_000146045.2_R64_genomic.gff.gz | python ../scripts/gff_to_jsonl.py - | python ../scripts/gjsonl_to_hgbed.py - > annotations.hgbed
```
