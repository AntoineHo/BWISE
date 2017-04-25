#! /usr/bin/env bash
if (( $# < 5 )); then
       echo "Need 5 parameters in the following order < dbg_path_file - unitig_file - k_value - out_file_gfa - out_file_fasta >"
       echo "see the readme file"
       exit
fi


EDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )


python3 ${EDIR}/check_python3_or_greater.py
if [ $? -ne 0 ] ; then
echo "*** K2000 needs python3 or greater to be ran *** "
echo "Please use python3 and re-run K2000"
exit 1
fi

in_sr=$1
original_in_sr=$1
in_unitigs=$2
in_k=$3
out_gfa=$4
echo "*** REMOVE DUPLICATES AND COMPACT MAXIMAL SUPER READS *******"

for min_overlap in 251; do       # TODO: input list
    echo ${min_overlap}; 
    python3 ${EDIR}/K2000.py ${in_sr} ${in_unitigs} ${in_k} ${min_overlap} > ${original_in_sr}_compacted_${min_overlap}
    if [ $? -ne 0 ] ; then
       echo "There was a problem in the unitig compaction, K2000 ABORDED"
       exit 1
    fi
done


echo "*** GENERATE GFA GRAPH FROM COMPACTED MAXIMAL SUPER READS ***"
python3 ${EDIR}/K2000_msr_to_gfa.py ${original_in_sr}_compacted_${min_overlap} ${in_unitigs} ${in_k} ${original_in_sr} > ${out_gfa}
if [ $? -ne 0 ] ; then
       echo "There was a problem in the unitig compaction during the GFA construction, K2000 ABORDED"
       exit 1
fi


echo "*** GENERATE FASTA FILE ***"
out_fasta=$5
python3 ${EDIR}/K2000_gfa_to_fasta.py ${out_gfa} > ${out_fasta}
if [ $? -ne 0 ] ; then
       echo "There was a problem in the unitig compaction during the Fasta construction, K2000 ABORDED"
exit 1
fi

############### GENERATION OF CRUSHED BUBBLE GRAPH. UNSAFE AND COMMENTED FOR NOW ###############
# echo "*** GENERATE A SIMPLIFIED CONSENSUS GRAPH***"
# python3 ${EDIR}/K2000_msr_to_simplified_msr.py ${original_in_sr}_compacted_${min_overlap} ${in_unitigs} ${in_k} > ${original_in_sr}_compacted_${min_overlap}_simplified
# if [ $? -ne 0 ] ; then
#        echo "There was a problem in the graph simplification, K2000 ABORDED"
#        exit 1
# fi
# python3 ${EDIR}/K2000.py ${original_in_sr}_compacted_${min_overlap}_simplified ${in_unitigs} ${in_k} ${min_overlap} > ${original_in_sr}_compacted_${min_overlap}_simplified2
# if [ $? -ne 0 ] ; then
#    echo "There was a problem in the unitig compaction, K2000 ABORDED"
#    exit 1
# fi
#
#
# echo "*** GENERATE GFA GRAPH FROM SIMPLIFIED COMPACTED MAXIMAL SUPER READS ***"
# python3 ${EDIR}/K2000_msr_to_gfa.py ${original_in_sr}_compacted_${min_overlap}_simplified2 ${in_unitigs} ${in_k} ${original_in_sr} > ${out_gfa}_simplified
# if [ $? -ne 0 ] ; then
#        echo "There was a problem in the unitig compaction during the GFA construction, K2000 ABORDED"
#        exit 1
# fi
#
#
# echo "*** GENERATE FASTA FILE FROM SIMPLIFIED MAXIMAL SUPER READS ***"
# out_fasta=$5
# python3 ${EDIR}/K2000_gfa_to_fasta.py ${out_gfa}_simplified > ${out_fasta}_simplified
# if [ $? -ne 0 ] ; then
#        echo "There was a problem in the unitig compaction during the Fasta construction, K2000 ABORDED"
# exit 1
# fi

echo "*** K2000 DONE ***"
exit 0
