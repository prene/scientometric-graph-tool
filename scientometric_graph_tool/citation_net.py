##Author: Rene Pfitzner
##August 2013

#This module implements functions for citation networks

import graph_tool.all as gt
import csv
import itertools
import random
import time

######################################################################################################

class PaperCitationNet():
    'Paper Citation Network Structure'
    
###############################################################
    def __init__(self):
        #create empty citation_net
        self.graph = gt.Graph(directed=True)
        self.graph.vertex_properties['year']=self.graph.new_vertex_property('int')
        self.graph.vertex_properties['_graphml_vertex_id']=self.graph.new_vertex_property('string')
        self.graph.edge_properties['year']=self.graph.new_edge_property('int')        
        
        self._citation_graphml_vertex_id_to_gt_id = {}
    
###############################################################
    def read_edgelist(self,citation_file,delimiter=' ',cited_column=0,citing_column=1,header=True):
        
        with open(citation_file,'r') as f:
            if header==True:
                header_text=f.readline()
            cou=0
            t_prev=time.time()
            t_cum=0
            for line in f:
                cou+=1
                if cou-10000*(cou/10000)==0:
                    print cou
                    t=time.time()
                    t_cum+=t-t_prev
                    t_prev=t
                    print t_cum
                tmp=line.split(delimiter)
                cited_paper=tmp[cited_column].rstrip()
                citing_paper=tmp[citing_column].rstrip()
                try:
                    self.add_citation(cited_paper,citing_paper)
                except NoSuchPaperError:
                    try:
                        self.add_paper(cited_paper,0)
                    except PaperIDExistsAlreadyError:
                        pass
                    try:
                        self.add_paper(citing_paper,0)
                    except PaperIDExistsAlreadyError:
                        pass
                    try:
                        self.add_citation(cited_paper,citing_paper)
                    except NoSuchPaperError:
                        print 'Something is terribly wrong...'
                        break
                except CitationExistsAlreadyError:
                    #print "should be new: "+cited_paper+' '+citing_paper
                    pass
                    
            
        
        
###############################################################    
    def add_metadata(self,citation_file):
        pass
    
###############################################################
    def read_graphml(self,citation_file,citation_meta):
        self.graph = gt.load_graph(citation_file)
        self.graph.vertex_properties['year']=self.graph.new_vertex_property('int')
        
        self._citation_graphml_vertex_id_to_gt_id = {}
        for v in self.graph.vertices(): 
            self._citation_graphml_vertex_id_to_gt_id[self.graph.vertex_properties['_graphml_vertex_id'][v]]=int(self.graph.vertex_index[v])
        
        f=open(citation_meta,'r')
        dialect=csv.Sniffer().sniff(f.readline())
        csv_delimiter=dialect.delimiter
        f.close()
        
        with open(citation_meta,'r') as f:
            #read header to determine property name
            header = f.readline()
            header = header.split(csv_delimiter)
            multiplex_edge_property_name = header[2].rstrip()

            #write multiplex edges with multiplex edge property (year)
            for line in f:
                tmp = line.split(csv_delimiter)
                paper_tmp = tmp[0]
                author_tmp = tmp[1]
                year = int(tmp[2].rstrip())
                    
                try:
                    paper_obj = self.graph.vertex(self._citation_graphml_vertex_id_to_gt_id[paper_tmp])
                except KeyError:
                    v=self.graph.add_vertex()
                    self.graph.vertex_properties['_graphml_vertex_id'][v]=paper_tmp
                    paper_obj = v    
                
                self.graph.vertex_properties['year'][paper_obj]=year
        
        self.min_year=min(self.graph.vertex_properties['year'].get_array())
        self.max_year=max(self.graph.vertex_properties['year'].get_array())
        
        

###############################################################
    #Function to add new papers, incl. collaborations
    def add_paper(self,paper_id,year):
        '''Add a paper with paper_id (str), publication year (int)'''    
        #try whether paper exists already in citation network
        try:
            self._citation_graphml_vertex_id_to_gt_id[paper_id]
            raise PaperIDExistsAlreadyError() #stop execution here with this error
        except KeyError:
            pass
    
        #add new paper to citation network and additional data structures
        new_paper=self.graph.add_vertex()
        self._citation_graphml_vertex_id_to_gt_id[paper_id]=self.graph.vertex_index[new_paper]
        self.graph.vertex_properties['_graphml_vertex_id'][new_paper]=paper_id
        self.graph.vertex_properties['year'][new_paper]=int(year)
    

    ################################################################
    ##
    #Funtion to add citation to citation network
    def add_citation(self,cited_paper,citing_paper):
        '''Add citation between two paper in citation network.'''
        try:
            cited_paper_gt=self._citation_graphml_vertex_id_to_gt_id[cited_paper]
        except KeyError:
            raise NoSuchPaperError()
        
        try:
            citing_paper_gt=self._citation_graphml_vertex_id_to_gt_id[citing_paper]
        except KeyError:
            raise NoSuchPaperError()

        if self.graph.edge(cited_paper_gt,citing_paper_gt)==None:
            new_citation=self.graph.add_edge(cited_paper_gt,citing_paper_gt)
            self.graph.edge_properties['year'][new_citation]=self.graph.vertex_properties['year'][self.graph.vertex(citing_paper_gt)]
        else:
            #print 'existing:'
            #print list(self.vertex_id(list(self.graph.edge(cited_paper_gt,citing_paper_gt))))
            raise CitationExistsAlreadyError()
    

################################################################
    ##
    #Function to get vertex_id's from vertex objects
    def vertex_id(self,iterable_of_vertices):
        'Returns an iterator of vertex id strings of the vertex objects specified in iterable_of_vertices'
        return itertools.imap(lambda x: self.graph.vertex_properties['_graphml_vertex_id'][x],iterable_of_vertices)


##########################################################
        ##
        #Calculate statistics of long-range-correlation motif
        def long_range_motif(self):
            pass
              

##########################################################################################################################
            
class MolloyReedCitationInstance(PaperCitationNet):
    'A class for Molloy-Reed shuffled citation graphs'
     
##########################################################   
    def __init__(self,citation_net):
        '''This calculates ONE random alternative multiplex, with citations reshuffled, such that a) time is still respected and b) degrees are kept the same.'''
        ############
        
        #initialize new graph that will hold the shuffled realization
        self.graph=citation_net.graph.copy()
        
        ##first we create the necessary data structures
        #keep track of empty in- and out-links of nodes in a double dictionary; the outer keys (year), are very few
        #This will be a few kb data structure, plus content to-be-filled below
        #outer key: year
        #inner key: _empty_in_links
        
        #self.min_year=min(self.graph.vertex_properties['year'].get_array())
        #self.max_year=max(self.graph.vertex_properties['year'].get_array())
        
        self.min_year=citation_net.min_year
        self.max_year=citation_net.max_year
        
        max_in_degree = int(max(self.graph.degree_property_map('in').get_array()))
        max_out_degree = int(max(self.graph.degree_property_map('out').get_array()))

        self._empty_in_links={}
        self._empty_out_links={}
        
        for y in range(self.min_year,self.max_year+1):
            self._empty_in_links[y]={}
            for k in xrange(max_in_degree+1):
                self._empty_in_links[y][k]=[]
            self._empty_out_links[y]={}
            for k in xrange(max_out_degree+1):
                self._empty_out_links[y][k]=[]
    
        #create property map
        self._vertex_empty_in_links = self.graph.new_vertex_property('int')
        self._vertex_empty_out_links = self.graph.new_vertex_property('int')
    
        #initialize _empty_in_links and _empty_out_links list as well as property map
        for v in self.graph.vertices():
            v_year = self.graph.vertex_properties['year'][v]
            v_in = v.in_degree()
            v_out = v.out_degree()
            if v_in>0:
                self._empty_in_links[v_year][v.in_degree()].append(v)
                self._vertex_empty_in_links[v] = v.in_degree()
            if v_out>0:
                self._empty_out_links[v_year][v.out_degree()].append(v)
                self._vertex_empty_out_links[v] = v.out_degree()
        
        #cut all edges
        self.graph.clear_edges()
        
        ###########
        #then we define internal functions needed for the algorithm
        ###
        def select_free_out(year):
            #get list of list of all youngest nodes with empty out-links (i.e. with k>0 !!)
            #flatten this list of lists
            all_youngest = list(itertools.chain.from_iterable(self._empty_out_links[year].values()[1:]))
            try:
                x = random.choice(all_youngest)
                return x
            except IndexError: #when list is empty
                raise NoFreeOutLinksError()
        
        ###
        def select_free_in(year,exclude_node):
            #get list of list of all nodes with empty in-links (i.e. with k>0 !!) from years > year
            #flatten this list of lists
            #if no exclude_node list is specified, then select from all possible
            if exclude_node == None:
                all_youngest=[]
                for i in range(year+1,self.max_year+1):
                    all_youngest.extend(list(itertools.chain.from_iterable(self._empty_in_links[i].values()[1:])))
                try:
                    y = random.choice(all_youngest)
                    return y
                except IndexError: #when list is empty
                    raise NoFreeInLinksError()
            #if exclude_node list is specified, then remove these nodes from the choice
            else:
                all_youngest=[]
                for i in range(year+1,self.max_year+1):
                    all_youngest.extend(list(itertools.chain.from_iterable(self._empty_in_links[i].values()[1:])))
                for ex in exclude_node:
                    try:
                        all_youngest.remove(ex)
                    except ValueError:
                        pass
                try:
                    y = random.choice(all_youngest)
                    return y
                except IndexError: #when list is empty
                    raise NoFreeInLinksError()
                
                
        ###
        def cut(year):
            all_occupied=[]
            for i in range(year+1,self.max_year+1):
                all_occupied.extend(self._empty_in_links[i].values()[0])
            try:
                y = random.choice(all_occupied)
            except IndexError: #when list is empty ... should not be possible ... 
                raise BadError()
            
            #choose an edge
            all_in_nodes = []
            for v in y.in_neighbours():
                all_in_nodes.append(v) 
            x = random.choice(all_in_nodes)
            #change empty_link properties
            y_year=self.graph.vertex_properties['year'][y]
            
            self._empty_in_links[y_year][self._vertex_empty_in_links[y]].remove(y)
            self._vertex_empty_in_links[y]+=1
            self._empty_in_links[y_year][self._vertex_empty_in_links[y]].append(y)
            
            x_year=self.graph.vertex_properties['year'][x]
            
            self._empty_out_links[x_year][self._vertex_empty_out_links[x]].remove(x)
            self._vertex_empty_out_links[x]+=1
            self._empty_out_links[x_year][self._vertex_empty_out_links[x]].append(x)
            
            #remove_edge
            self.graph.remove_edge(self.graph.edge(x,y))
            
            #return            
            return x,y
        
        ##
        def new_edge(out_link_node,in_link_node):
            #change empty_in_link and empty_out_link properties accordingly
            in_link_node_year = self.graph.vertex_properties['year'][in_link_node]
            
            self._empty_in_links[in_link_node_year][self._vertex_empty_in_links[in_link_node]].remove(in_link_node)
            self._vertex_empty_in_links[in_link_node]-=1
            self._empty_in_links[in_link_node_year][self._vertex_empty_in_links[in_link_node]].append(in_link_node)
            
            out_link_node_year = self.graph.vertex_properties['year'][out_link_node]
            
            self._empty_out_links[out_link_node_year][self._vertex_empty_out_links[out_link_node]].remove(out_link_node)
            self._vertex_empty_out_links[out_link_node]-=1
            self._empty_out_links[out_link_node_year][self._vertex_empty_out_links[out_link_node]].append(out_link_node)
            
            #write new edge
            self.graph.add_edge(out_link_node,in_link_node)
            
        
        ############
        #then we go on with actually shuffling edges
        all_years = range(self.min_year,self.max_year+1)
        try:
            #find youngest year of nodes that have empty out-links
            year_index = 0
            while True:
                try:
                    year = all_years[year_index]
                except IndexError: #Error occurs if all possible years are exhausted
                    raise ExhaustedPossibleYearsError()
                    
                try:
                    out_link_node = select_free_out(year)
                
                    while True:
                        try:
                            #exclude self node and all already neighbors from choice of where to link to
                            exclude_nodes_from_choice=[out_link_node]
                            exclude_nodes_from_choice.extend(list(out_link_node.out_neighbours()))
                            in_link_node=select_free_in(year,exclude_nodes_from_choice)
                            year_index=0
                            break
                        except NoFreeInLinksError: #if no older than "year" in-link is free ...
                            #cut a suitable in-link
                            in_link_node = cut(year)[1]
                            year_index=0
                            break

                    #write new edge
                    new_edge(out_link_node,in_link_node)
                
                except NoFreeOutLinksError: #when list is empty, second line above
                    year_index+=1
                #         
        except ExhaustedPossibleYearsError:
            print('Finished shuffling!')
            print ('Old edges:')
            for e in citation_net.graph.edges():
                print e
            print ('New edges:')
            for e in self.graph.edges():
                print e
            check_citation_causality(self.graph)
                
###############################################################################################################################
##define global functions

#check causality constraint of citation network
def check_citation_causality(citation_net):
    print 'Causality check ...'
    problems = []
    for e in citation_net.edges():
        s = e.source()
        t = e.target()
        if citation_net.vertex_properties['year'][s]>=citation_net.vertex_properties['year'][t]:
            problems.append(str(e))
    
    if len(problems)>0:
        print 'Causality Problems with edge(s):'
        for e in problems:
            print e
    else:
        print 'No causality problems!'

            
#################################################
#define Error Classes

class NoFreeInLinksError(Exception):
    pass
    
class NoFreeOutLinksError(Exception):
    pass
    
class ExhaustedPossibleYearsError(Exception):
    pass
    
class BadError(Exception):
    pass

class PaperIDExistsAlreadyError(Exception):
    pass
    
class CitationExistsAlreadyError(Exception):
    pass
    
class NoSuchPaperError(Exception):
    pass
