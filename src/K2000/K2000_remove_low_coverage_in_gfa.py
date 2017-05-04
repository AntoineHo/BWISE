#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

'''
From a GFA file representing a graph of phasitigs, remove low covered nodes.
@author  pierre peterlongo pierre.peterlongo@inria.fr
'''                

import sys
import getopt
import K2000_common as kc
   
        
             
def print_filtered_GFA(gfa_file, threshold):
    '''print gfa nodes as fasta'''
    GFAs = open(gfa_file,"r")
    printed_nodes=[]
    for line in GFAs:
        tabline = line.strip().split() 
        if line[0] == 'S': #S       3       TTCGATAAATTGATCCAGGCTGCCGTCCAGCACGGCC...   FC:i:2319165    #AVG:f:549.30
            average_coverage = float(tabline[-1].split(":")[-1])
            if average_coverage > threshold: 
                print(line.strip())
                printed_nodes.append(tabline[1])
        if line[0] == 'L': #L	400	+	279	+	36312M
            if tabline[1] in printed_nodes and tabline[3] in printed_nodes: 
                print(line.strip())
    GFAs.close()
            
    
            

def main():
    '''
    Creation of a fasta file from a GFA file.
    '''
    printed_nodes = print_filtered_GFA(sys.argv[1], int(sys.argv[2]))
    

if __name__ == "__main__":
     main()  
