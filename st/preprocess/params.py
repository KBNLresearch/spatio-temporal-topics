
# ---------- Set the paramters for indexing -------------
# URL of the elastic search service
# Default: localhost:9200
ES_URL = 'localhost:9200'

# Cluster name
CLUSTER = 'kb_st'

# LM as similarity
SIM_SETTING = {
    "settings":{
        "index": {
            "similarity":{
                "LM":{
                    "type": "LMDirichlet",
                    "mu": 2000,
                }
            }
        }
    }
}


#--------- Setting for indexing KB news ----------
# Index constraints
NEWS_LOC = ['Landelijk', 'Regionaal/lokaal']
 

# Name of the index
# We only create one index to store everything
INDEX = 'kb_krant'

# We only index articles
DOC_TYPE = 'article'

# Define settings of individual field
# Note: I set all fields store=true, as I think I will
# actually need to return the values of all these values. 
# I am not really sure if this is the best way. Benchmarking
# the performance may help.  

# The unique article identifier
DOCID = {
    'type': 'string', 
    'index': 'not_analyzed',
}

# The publishing date of the news article
# Set doc_values to true for quicker filtering. 
DATE = {
    'type': 'date', 
    'format': 'date', # (yyyy-MM-dd)
    'doc_values': True,
    'store': True,
}

# Location of where the newspaper is published
LOC = {
    'type': 'string', 
    'index': 'not_analyzed',
    'doc_values': True,
    'store': True    
}

# Title of the article
# Set store to true and indexoptions to offsets 
# for highlighting
TITLE = {
    'type': 'string', 
    'index': 'analyzed',
    'analyzer': 'dutch',
    'store': True, 
    'index_options': 'offsets',
    'similarity': "LM",
    'term_vector': 'yes',
}

KRANT_TITLE = {
    'type': 'string',
    'index': 'not_analyzed',
    'doc_values': True,
    'store': True,
}

# The linked entities
# Note: this can be an array when indexing
ENTITY = {
    'type': 'string',
    'index': 'dutch',
    'store': True,
    'type': 'nested',
    'include_in_parents': True,
    'properties':{
        'concept': {'type': 'string'},
        'doc_score': {'type': 'float'},
        'col_score':{'type': 'float'},
        'score': {'type': 'float'},
        # Type of concept (person, location, organization, term)
        # 'type': {'type': 'string'},
    }
}

# The document content
OCR = {
    'type': 'string',
    'index': 'analyzed',
    'analyzer': 'dutch',
    'store': True,
    'index_options': 'offsets',
    'similarity': "LM",
    'term_vector': 'yes',
}


# Extra information
DOCLENGTH = {
    'type': 'long',
    'doc_values': True,
    'store': True,
    'null_value': 0,
} 

# properties of a news article
MAPPING = {
    'article':{
        'properties':{
            'docid': DOCID,
            'date': DATE,
            'title': TITLE,
            'loc': LOC,
            'papertitle': KRANT_TITLE,
            'entity_person': ENTITY,
            'entity_organization': ENTITY,
            'entity_location': ENTITY,
            'entity_other': ENTITY,
            'text': OCR,
            'doclength': DOCLENGTH,
        }
    } 
}


