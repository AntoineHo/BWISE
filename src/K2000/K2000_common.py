#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
'''
Compaction of super reads. Non ambiguous paths from a set of super reads are compacted
Resulting super reads are called MSR for Maximal Super Reads
Common file
@author (except for the 'unique' function) pierre peterlongo pierre.peterlongo@inria.fr
'''            

import sys
import getopt
import sorted_list
    
    
    
# Create structures used by dict and array methods.
basecomplement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
def complement(s): 
    letters = list(s) 
    letters = [basecomplement[base] for base in letters] 
    return ''.join(letters)
    

def reverse_complement(seq):
    return ''.join(basecomplement[c] for c in seq[::-1])
    
def get_reverse_sr(x):
    ''' reverse of a super read x. Example is super read x = [4,2,6], reverse(x) = [-6,-2,-4] '''
    return [-b for b in x][::-1]
    
def is_palindromic(x):
    ''' return true is a sr x is palindromic, eg [1,2,-2,-1]'''
    if len(x)%2 == 1: return False 
    for i in range(0,int(len(x)/2)):
        if x[i] != -x[-i-1]: return False
    return True

def generate_SR(file_name):
    ''' Given an input file storing super reads, store them in the SR array'''
    sr_file = open(file_name, 'r')
    sl = sorted_list.sorted_list()
    for line in sr_file:
        if line[0]==">": continue # compatible with fasta-file format
        line = line.rstrip()[:-1].split(';')
        sr=[]
        for unitig_id in line: 
            sr_val=int(unitig_id)
            sr=sr+[sr_val]    
        sl.add(sr)
    return sl
    
def add_reverse_SR(SR):
    ''' For all super reads in SR, we add there reverse in SR 
    This double the SR size, unless there are palindromes ([1,-1] for instance). Those are not added.
    We don't check that this does not create any duplicates'''
    SR_ = sorted_list.sorted_list()
    for sr in SR.traverse():
        if not is_palindromic(sr):
            SR_.add(get_reverse_sr(sr))
    for sr in SR_.traverse():
        SR.add(sr)
    return SR
        
    
def colinear(x,X,starting_positions):
    ''' Check that all sr in X are colinear with x
    For each sr in X, one knows its starting position on x, with table starting_positions'''
    for i in range(len(X)):
        other = X[i]
        starting_position = starting_positions[i]
        pos=0
        while True:
            if pos>=len(other) or pos+starting_position>=len(x) : break
            if other[pos] != x[pos+starting_position]:          # "non colinear"
                return False
            pos+=1
            
             
    return True
    
    
def canonical(sr):
    ''' return the canonical representation of a sr (the smallest version of a sr and its reverse complement'''

    if len(sr)==1:
        if sr[0]>0:
            return [sr]
        else:
            return [-sr]
    sr_=get_reverse_sr(sr)
    if sr>sr_:  return sr
    else :      return sr_
    
def is_canonical(sr):

    ''' return True if the canonical representation of sr is itself'''
    if len(sr)==1:
        if sr[0]>0: return True
        else:       return False
    if sr>get_reverse_sr(sr):    return True
    else:                           return False
    
         
def print_maximal_super_reads(SR):
    '''print all maximal super reads as a flat format'''
    for sr in SR.traverse():
        if is_canonical(sr) or is_palindromic(sr):
            if len(sr)==1:
                print (str(sr[0])+";")
            else:
                for unitig_id in sr: 
                    print (str(unitig_id)+";", end="")
                print ()
             

            
def load_unitigs(file_name):
    unitigs=[]
    file=open(file_name,'r')
    for line in file:
        line=line.rstrip()
        if line[0]=='>': continue
        unitigs+=[line]
    return unitigs
    
            
def load_unitig_lengths(file_name):
    unitig_lengths=[]
    file=open(file_name,'r')
    for line in file:
        line=line.rstrip()
        if line[0]=='>': continue
        unitig_lengths+=[len(line)]
    return unitig_lengths

def get_len_ACGT(sr,unitig_lengths,k):
    ''' provides the cumulated length of the unitigs of a sr '''
    lenACGT = k
    for unitig_ids in sr:
        if unitig_ids>0:
            lenACGT+=unitig_lengths[unitig_ids-1]-k       # add the ACGT len of the corresponding unitig. -1 is due to the fact that unitigs start at zero while sr indices start at one.
        else:
            lenACGT+=unitig_lengths[-unitig_ids-1]-k

    return lenACGT

def at_least_a_successor(SR,sr):
    ''' Checks if sr as at least a successor. Return True in this case, else return False '''
    n=len(sr)
    for len_u in range(n-1,0,-1):
        Y=SR.get_lists_starting_with_given_prefix(sr[-len_u:])
        if len(Y)>0: 
            return True
    return False

def is_a_dead_end(SR,sr):
    ''' A sr is a dead end if it has no successor or no predecessor '''
    if not at_least_a_successor(SR,sr):                 return True # No predecesssor, this is a dead end
    if not at_least_a_successor(SR,get_reverse_sr(sr)): return True # No successor, this is a dead end
    return False # Sucessor(s) and predecessor(s), this is not a dead end. 


def get_msr_id(msr):
    ''' returns the id of a msr 
    WARNING: here msr contains as last value its unique id. 
    '''
    return int(msr[-1].split("_")[1])
    
def get_reverse_msr_id(msr,MSR):
    ''' returns the id of the reverse complement of msr 
    1/ find the sequence of the msr_ in SR
    2/ grab its id
    WARNING: here msr contains as last value its unique id. 
    '''
    #1/
    without_id_reverse_msr = get_reverse_sr(msr[:-1])                     # get the msr reverse complement
    Y=MSR.get_lists_starting_with_given_prefix(without_id_reverse_msr)        # find the reverse complement in the list. 
    for y in Y:                                                               # should be of size >= 1. One of them is exactly 'without_id_reverse_msr' plus its id. 
        if len(y) == len(without_id_reverse_msr)+1:                           # 'y' is 'without_id_reverse_msr' with its node id
            return get_msr_id(y)                                              # 2/
    return None                                                               # Should not happend

# SR=generate_SR("test.txt")
# SR.unique()
# SR=add_reverse_SR(SR)
# SR.unique()
# for sr in SR.traverse():
#     print (sr)
