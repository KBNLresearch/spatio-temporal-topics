# Run elastic search service wrapper.
# Note: the wrapper is not included in the elsaticsearch itself.
# It can be obtained at:
# https://github.com/elasticsearch/elasticsearch-servicewrapper.git
#
# The wrapper contains one directory called service,
# and it needs to be placed under:
# elasticsearch-*.*/bin/

# You can change the path to where you prefer to 
# install elastic search, and put the wrapper 
# in the corresponding location.

ES_HOME=es/elasticsearch-1.1.1/

$ES_HOME/bin/service/elasticsearch $1