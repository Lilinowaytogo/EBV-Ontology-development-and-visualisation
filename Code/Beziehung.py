import graphviz
from owlready2 import *
import difflib
from PIL import Image
import pydot

type2str_restriction = class_construct._restriction_type_2_label
owl.ClassConstruct
def _process_entity(entity, job_name, orig_entity, graph):
    """Helper: Append entity for the specified job.
    """
    edge = (orig_entity, job_name, entity)
    if edge not in graph:
        graph.append(edge)
    return graph

def _process_restriction(restriction, entity, graph):
    """Helper: Append restriction.
    """
    assert restriction.__module__ == 'owlready2.class_construct'
    
    # Grab object_property --type--> value
    object_property, value = restriction.property, restriction.value
    restriction_type = type2str_restriction[restriction.type]
    
    # Separate logical or for 'only'
    if restriction_type == 'only':
        for or_value in value.Classes:
            edge = (entity, '{},{}'.format(object_property.name, restriction_type), or_value)
            if edge not in graph:
                graph.append(edge)
            
    # No more processing for 'some'
    else:
        edge = (entity, '{},{}'.format(object_property.name, restriction_type), value)
        if edge not in graph:
            graph.append(edge)
        
    return graph
def _process_subclasses(entity, graph):
    """Helper: Append subclasses.
    """
    # Safely grab all subclasses
    try:
        subclasses = list(entity.subclasses())
    except:
        subclasses = []

    for subcls in subclasses:
        if (entity, 'has_subclass', subcls) not in graph:
            graph.append((entity, 'has_subclass', subcls))
        if (subcls, 'subclass_of', entity) not in graph:
            graph.append((subcls, 'subclass_of', entity))

    return graph

def _populate_subclass_rel(graph):
    """Helper: Ensure 'subclass_of' and 'has_subclass' always appear in pairs.
    """
    for edge in graph:
        if edge[1] == 'subclass_of' and (edge[2], 'has_subclass', edge[0]) not in graph:
            graph.append((edge[2], 'has_subclass', edge[0]))
        elif edge[1] == 'has_subclass' and (edge[2], 'subclass_of', edge[0]) not in graph:
            graph.append((edge[2], 'subclass_of', edge[0]))
    return graph

def _process_instances(entity, graph):
    """Helper: Append individuals.
    """
    # Safely grab all individuals
    try:
        instances = entity.instances()
    except:
        instances = []

    for instance in instances:
        if instance.is_a[0] == entity:
            if (entity, 'has_individual', instance) not in graph:
                graph.append((entity, 'has_individual', instance))

    return graph
def ontograf_simple(orig_entity, onto):
    """Interface func to search and retrieve infor for a given
    entity inside onto.
    """
    if orig_entity is None:
        return []
    
    # Initial graph search
    graph = generate_knowledge_graph(orig_entity)
    
    # Prep for other key entities given the initial graph
    entities = []
    for edge in graph:
        entities.append(edge[2])

    # 1st-level of filters, append more info from children and parent nodes
    for entity in entities:
        sub_graph = generate_knowledge_graph(entity)
        for edge in sub_graph:
            if edge[2] == orig_entity:
                if (entity, edge[1], orig_entity) not in graph and entity != orig_entity:
                    graph.append((entity, edge[1], orig_entity))

    # 2nd-level of filters, filter some ill-logical nodes
    graph = _filter_graph(graph, onto)

    # Convert everything inside graph into str
    graph = _to_string(graph)

    return graph
def generate_knowledge_graph(entity):
    """Helper function to grab entity-relation from onto and 
    return as knowledge graph.
    """
    graph = []

    # Part 1: Append subclasses
    graph = _process_subclasses(entity, graph)

    # Part 2: Collect equivalent_to
    try:
        equivalent_to_list = entity.INDIRECT_equivalent_to  # NOTE: Weird bug here, have to use INDIRECT
    except:
        equivalent_to_list = []
    for et in equivalent_to_list:
        # equivalent_to AND objects:
        if et.__module__ == 'owlready2.class_construct':
            for x in et.Classes:
                # For class restriction, retrieve relevant infos inside
                if x.__module__ == 'owlready2.class_construct':
                    graph = _process_restriction(x, entity, graph)
                    
    # Part 3: Look into is_a
    is_a_list = entity.is_a
    for x in is_a_list:
        # Entity: is_a indicates subclasses
        if x.__module__ == 'owlready2.entity':
            graph = _process_entity(x, 'subclass_of', entity, graph)
                
        # Restriction
        elif x.__module__ == 'owlready2.class_construct':
            graph = _process_restriction(x, entity, graph)
        
    # Part 4: Look into instances
    graph = _process_instances(entity, graph)
    
    # Part 5: Some additional filters
    graph = _populate_subclass_rel(graph)
    
    return graph

def _filter_graph(graph, onto):
    """Helper: filter graph from some ill-logical entries.
    """
    filtered_graph = []
    # Grab all individuals
    individuals = list(onto.individuals())

    for edge in graph:
        passed = True
        # Ill-logical individuals
        if edge[0] in individuals:
            passed = False
        if passed:
            filtered_graph.append(edge)
    return filtered_graph
def keyword_search_onto(keyword, onto):
    """Search and index key entity from onto given keyword.
    """
    classes = list(onto.classes())
    classes_str = [x.name for x in classes]
    all_res = difflib.get_close_matches(keyword, classes_str)
    # Only grab the most probable search keyword
    if len(all_res) > 0:
        res = all_res[0]
        return classes[classes_str.index(res)]
    else:
        return None
    
def keyword_search(keyword, onto):
    """Search and index key entity from onto given keyword.
    """
    classes = list(onto.classes())
    classes_str = [x.name for x in classes]
    all_res = difflib.get_close_matches(keyword, classes_str)
    # Only grab the most probable search keyword
    if len(all_res) > 0:
        res = all_res[0]
        return classes[classes_str.index(res)]
    else:
        return None

def _to_string(graph):
    """Helper: Convert everything collected inside graph list into
    string.
    """
    for i in range(len(graph)):
        edge = list(graph[i])
        for k in range(len(edge)):
            if type(edge[k]) is not str:
                edge[k] = edge[k].name
            edge[k] = edge[k].replace(',', ', ')
        graph[i] = (edge[0], edge[1], edge[2])
    return graph
def convert_to_graphviz(graph, name='KG'):
    """Helper function to convert edge graph into graphviz.Digraph.
    """
    e = graphviz.Digraph(name)
    e.attr('node', shape='box')
    for edge in graph:
        e.attr('node', shape='box')
        e.node(edge[0])
        e.node(edge[2])
        e.edge(edge[0], edge[2], label=edge[1])
    return e
def show_graph(graph):
    graph.render("mygraph.dot","./")
    (g,) = pydot.graph_from_dot_file('mygraph.dot')
    g.write_png("mygraph.png")
    im = Image.open('mygraph.png')
    im.show()
    import time
    time.sleep(3)
    im.close()
if __name__ == "__main__":
    onto = get_ontology("./pizza.owl").load()
    entity = keyword_search_onto('Pizza', onto)
    kg = ontograf_simple(entity, onto)
    print(kg)
    e = convert_to_graphviz(kg)    
    show_graph(e)
    print(e)