#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
'''
Creation of a GFA file from a set of compacted maximal super reads 
@author  pierre peterlongo pierre.peterlongo@inria.fr
'''            

import sys
import getopt
import K2000_common as kc

def get_right_edges (MSR,x,id_x,unitigs,k):
    ''' Main function, For a given super read x, we find y that overlap x, and we return the links together with their strands
    +12- (meaning that the forward strand (first '+') of x overlaps the reverse strand (last '-') of 12)
    Note that one treat x only if its canonical.
    Four cases :
    1/ x overlaps y, with y canonical. One prints x + y + blabla
    2/ x overlaps y_, with y_ non canonical. In this case, y_ overlaps x. One of the two solutions has to be chosen. We chose min(idx,idy) (with idx,idy being the ids of the MSR x,y in SR) One searches the id of y, and one prints x + y - blabla.
    3/ x_ overlaps y. same as 2.
    4/ x_ overlaps y_. We do nothing, this case is treated when the entry of the function is y that thus overlaps x.
    WARNING: here x and each msr in MSR contain as last value its unique id.
    '''
    x=x[:-1]                                # remove the x_id from the x msr
    if not kc.is_canonical(x): return
    n=len(x)
    res=[]
    # CASES 1 AND 2
    strandx='+'
    # print ("x is", x)
    for len_u in range(1,n): # for each possible x suffix
        u=x[-len_u:]
        # print ("u is", u)
        Y=MSR.get_lists_starting_with_given_prefix(u)
        # if x in Y: Y.remove(x)            # we remove x itself from the list of y : note that it should not occur.
        # print (x)
        # assert(x not in Y)
        if len(Y)==0: continue              # No y starting with u
        for y in Y:
            # detect the y strand
            # CASE 1/
            if kc.is_canonical(y[:-1]):     # remove the last value that corresponds to the node id
                strandy ='+'
                # id_y=indexed_nodes.index(y)                               # get the id of the target node
                id_y=kc.get_msr_id(y)                                           # last value is the node id, here the id of the target node
            # CASE 2/
            else:
                strandy='-'
#                id_y = indexed_nodes.index(get_reverse_msr(y))
                id_y=kc.get_reverse_msr_id(y,MSR)                                # find the reverse of list y in MSR to grab its id.
                if id_x>id_y: continue # x_.y is the same as y_.x. Thus we chose one of them. By convention, we print x_.y if x<y.
            # print the edges
            res.append( strandx+str(id_y)+strandy)


    # CASES 3 AND 4
    strandx='-'
    x_=kc.get_reverse_sr(x)
    for len_u in range(1,n): # for each possible x suffix
        u=x_[-len_u:]
        Y=MSR.get_lists_starting_with_given_prefix(u)
        # assert(x_ not in Y)
        if len(Y)==0: continue  # No y starting with u
        for y in Y:
            if kc.is_canonical(y[:-1]): # CASE 3
                strandy ='+'
               # id_y=indexed_nodes.index(y)                                # get the id of the target node
                id_y=kc.get_msr_id(y)                                           # last value is the node id, here the id of the target node
                # we determine min(id_x,id_y)
                if id_x>id_y: continue # x_.y is the same as y_.x. Thus we chose one of them. By convention, we print x_.y if x<y.

                res.append( strandx+str(id_y)+strandy) # note that strand x is always '-' and strandy is always '+' in this case.

#            else: continue # CASE 4, nothing to do.
    return res
    
    

    
         
def index_GFA_edges(MSR,unitigs,k):
    '''index each edges in GFA format.
    WARNING: here each msr in MSR contains as last value its unique id. 
    '''
    inverse={}
    inverse['+']='-'
    inverse['-']='+'
    out_edges={}
    for msr in MSR.traverse():
        x_id = kc.get_msr_id(msr)                                         # last value is the node id
        # if x_id%100==0: sys.stderr.write("\t%.2f"%(100*x_id/len(MSR))+"%\r")
        dests=get_right_edges(MSR,msr,x_id,unitigs,k)
        if dests == None: continue
        if x_id not in out_edges: out_edges[x_id]=[]
        for dest in dests: out_edges[x_id].append(dest)
        for dest in out_edges[x_id]:
            # dest = +795-
            # print (str(x_id)+" "+dest)
            dest_node_id=       int(dest[1:-1])
            dest_node_strand=   dest[-1]
            source_node_strand= dest[0]
            if dest_node_id not in out_edges: out_edges[dest_node_id]=[]
            if inverse[dest_node_strand]+str(x_id)+inverse[source_node_strand] not in out_edges[dest_node_id]:
                out_edges[dest_node_id].append(inverse[dest_node_strand]+str(x_id)+inverse[source_node_strand])

            
    # print(str(out_edges))
    sys.stderr.write("\t100.00%\n")
    # for x_id in out_edges:
    #     if out_edges[x_id]!=None:
    #         print(str(x_id)+" :::"+str(out_edges[x_id]))
    return out_edges
   
def remove_this_similar_msr(MSR,msr,out_edges):
    '''given a msr, checks if there is an other msr of same length and with same predecessors and successors. 
    In this case, remove this msr.
    Sort of bubble crushing'''
    x_id = kc.get_msr_id(msr)
    if x_id not in out_edges : return
    for target in out_edges[x_id]:                                                  # we could compare x_id to ALL other msr. However it is compared only to those that can be accessible, ie those that are son on soons (without taking the direction into account).
        target_node_id=int(target[1:-1])
        if target_node_id not in out_edges: continue
        for target_of_target_node_id in out_edges[target_node_id]:
            other_id=int(target_of_target_node_id[1:-1])
            if other_id==x_id: continue
            if other_id not in out_edges: continue
            if out_edges[x_id]==out_edges[other_id]:
                # TODO: verify approx same length
                MSR.remove(msr)
                return
                # MSR.removeindexedSR(kc.get_reverse_sr(msr)) #USELESS

def remove_similar_MSR(MSR,out_edges):
    for msr in MSR.traverse():
        remove_this_similar_msr(MSR,msr,out_edges)
             
    
     
            
def print_simplified_msr(MSR):
    '''print canonical unitigs ids
    WARNING: here each msr in MSR contains as last value its unique id. 
    '''
    for msr in MSR.traverse():
        node_id = kc.get_msr_id(msr)                        # last value is the node id
        msr = msr[:-1]                                   # remove the last value that corresponds to the node id
        if  kc.is_canonical(msr):                       # remove the last value that corresponds to the node id
            for unitig_id in msr:                       # remove the last value that corresponds to the node id
                print (str(unitig_id)+";", end="")
            print ()

def main():
    '''
    Creation of a msr file from a msr.
    If two phasitigs have the same length (almost +- 10) and they have the same predecessors and the same successors, then keep only one of them.
    '''
    # SR=[[1,3,4],[14],[4,6],[-6,-1,-2],[4,6,7,9],[9,10,11,12],[4,6],[-13, -12, -11]]
    
    MSR=kc.generate_SR(sys.argv[1])
    unitigs=kc.load_unitigs(sys.argv[2])
    k = int(sys.argv[3])
    kc.add_reverse_SR(MSR)
    MSR.sort()
    MSR.index_nodes()                          # This adds a final value to each sr, providing its node id. 
    # sys.stderr.write("Print GFA Nodes\n")
    # print_GFA_nodes(MSR,unitigs,k-1,mapped_len)
    # print_GFA_nodes_as_ids(SR,unitigs,k-1)
    sys.stderr.write("Index GFA Edges\n")
    out_edges = index_GFA_edges(MSR,unitigs,k)
    # in_edges = out_to_in_edges(out_edges)
    remove_similar_MSR(MSR,out_edges)
    print_simplified_msr(MSR)

if __name__ == "__main__":
     main()  
