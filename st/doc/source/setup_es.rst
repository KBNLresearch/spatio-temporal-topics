======================================
Configuration of elastic search
======================================

Locations
---------------
For our convinence, we assign names to locations 

* ``HOME_ES``: Home directory where elastic search is installed.
* ``HOME_PROJ``: Home directory of the project 


Run an ES server
------------------
1. Download and install elasticsearch as described `here`_. 

.. _`here`: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/_installation.html

2. Download and install `elasticsearch-servicewrapper`_. The download contains a directory called ``service/``. Place this directory under ``$HOME_ES/bin/``.

.. _`elasticsearch-servicewrapper`: https://github.com/elasticsearch/elasticsearch-servicewrapper

3. Configure the ES server by editing the configuration file under ``$HOME_ES/config/elasticsearch.yml`` 

    * An example configure file can be found at ``$HOME_PROJ/etc/elasticsearch.yml``. You can also simply replace the default configuration file with this example.

    * By default, we set the cluster name to ``kb_st``, and only use one node, and without replicates for the index.  

4. Edit the script ``HOME_PROJ/run_es.sh`` to set the ``HOME_ES`` to the home directory of elasiticsearch.

5. To start/stop/restart the ES service, go to ``$HOME_PROJ/``, and do the following::

    # Run the script without option will list the valid options.
    $ ./run_es.sh option





