data/:
	The downloading scripts and downloaded data
	Data are downloaded via KB's jsru service. 

	An example query: http://jsru.kb.nl/sru/sru?x-collection=DDD_artikel&maximumRecords=1&query=*%20and%20date%20within%20%2201-01-1918%2031-12-1940%22%20and%20type%20=%20artikel		

	Note: it seems that the maximum number of returned results is 1000.

    download_data.py:

	It downloads the metadata and ocr data for a given period, stored in
	a given output directory, under meta/ and ocr/, respectively.
	Only articles are downloaded. (see the example query.)

	The meta data are stored as arrays of xml entries in a json file,
	each entry contains the content of <srw:record>.+?</srw:record> as in
	the retrieved results.
