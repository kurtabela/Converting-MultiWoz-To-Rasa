#!/bin/bash
for filename in ./*_tmp.txt; do
    ../fast_align/build/fast_align -i $filename -d -o -v > ${filename}_forward.align
done
