# sort on date, doclength
curl -XPUT localhost:9200/kb_krant/_warmer/warmer_sortdate -d '{
    "query" : {
        "match_all" : {}
    },
    "sort": [
        { "date": { "order" : "asc" }}
    ]
}'

curl -XPUT localhost:9200/kb_krant/_warmer/warmer_sortdl -d '{
    "query" : {
        "match_all" : {}
    },
    "sort": [
        { "doclength": { "order" : "desc" }}
    ]
}'

