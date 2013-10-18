#Documentation
This is the documentation of the python package scientometric-graph-tool.

## Index

### [A graph-tool primer](Documentation#a-graph-tool-primer)

### [Modules](Documentation#Modules)

[**`multiplex_structures`**](Documentation#multiplex_structures)
* [`PaperAuthorMultiplex()`](Documentation#PaperAuthorMultiplex)

[**`citation_net`**](Documentation#citation_net)
* [`PaperCitationNet()`](Documentation#PaperCitationNet)
* [`MolloyReedCitationInstance()`](Documentation#MolloyReedCitationInstance)
* [`check_citation_causality()`](Documentation#check_citation_causality)


##A graph-tool Primer
To understand the scientometric-graph-tool package it is import to have a working understanding of graph-tool. Of course, the best way to gain this is to read through the documentation of graph-tool [here](http://graph-tool.skewed.de/static/doc/index.html). However, here you can find a little primer in order to have the basics covered and to better understand scientometric-graph-tool.

More to come ...


##Modules
Documentation for the several modules within this package.

###`multiplex_structures`
####`PaperAuthorMultiplex`
A class for network multiplex's of paper citation networks and collaboration networks.

**`.add_paper(self,paper_id,year,author_list,update_collaborations=True)`**

Add a paper with paper_id (str), publication year (int) and authors specified in author_list (list<str>) to the multiplex. Collaborations are automatically updated, unless otherwise specified.

**`.add_citation(self,cited_paper,citing_paper)`**

Add citation between two papers in the citation network.

**`.add_collaboration(self,author1, author2, year)`**

Add collaboration between two authors, without adding a paper.

**`.add_multiplex(self,paper_id,author_id,year)`**

Function to add multiplex interconnections

**`.read_graphml(self,collab_file,citation_file,mult_file)`**

Read multiplex from files (graphml format) specifying the collaboration network, the citation network and multiplex meta data (csv).

**`.read_meta_create_collab(self,meta_file, header=True,paper_column=0,author_column=1,delimiter=' ')`**

Function to read meta-file and to create coauthorship network based on it on-the-fly.


**`.papers_by(self,author_id)`**

Returns a list of paper (citation) vertex objects that specified author has (co)authored.

**`.authors_of(self,paper_id)`**

Returns a list of author (collaboration) vertex objects that have (co)authored the specified paper.

**`.socially_biased_citations(self)`**

Calculate number of socially-biased citations for every paper. Defined as the number of citations, that are citations by people who have, at the time of citing the paper, previously collaborated with the authors.

**`.distribution_authors(self,paper_vertex_iterator)`**

Returns a list of the number of authors for the papers specified in the iterator.

**`.distribution_papers(self,author_vertex_iterator`**

Returns a list of the number of papers for the authors specified in the iterator.

**`.multiplex_property_mapping(self,origin_layer_iterator,origin_layer_property,target_layer_property,direction=None,aggregation_function=None)`**

Returns lists of a collaboration net property for a selection of nodes and their according multiplex-mapped property, aggregated using aggregation_function.

**`.multiplex_neighbours(self,vertex_object,layer=None)`**

Returns an iterator of vertices in layer, that are multiplex neighbours of vertex_object.

**`.vertex_id(self,iterable_of_vertices,layer=None)`**

Returns an iterator of vertex id strings of the vertex objects specified in iterable_of_vertices, being members of layer.

**`.pickle(self,filename)`**

Pickle the multiplex structure self into filename.

**`.unpickle(self,filename)`**

Unpickle a pickled multiplex structure stored in filename into self.


####Function of module multiplex_structures

**`check_one_to_one(multiplex)`**

Check whether the multiplex is a one-to-one multiplex.

###`citation_net`
####`PaperCitationNet`
A class for paper citation networks.

**`.read_graphml(self,citation_file,citation_meta)`**

Reads a paper citation network from citation_file in .graphml format. Metadata, like publication year, has to be given in citation_meta csv file.


####`MolloyReedCitationInstance(PaperCitationNetInstance)`
A derived class from PaperCitationNet. Every instance is a citation-shuffled version of PaperCitationNetInstance. Through inheritance, has all methods of [`PaperCitationNet()`](Documentation#PaperCitationNet)
