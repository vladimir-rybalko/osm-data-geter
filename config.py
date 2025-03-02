query_filters = [{
    "name": "tourism",
    "filter": [
        'nwr["tourism"="hotel"]',
    ],
    "properties": ["tourism", "name"],
    "replaceProperties": "tourism-type"
},{
    "name": "leisure",
    "filter": [
        'nwr["leisure"]',
    ],
    "properties": ["leisure", "name", "sport"],
    "replaceProperties": "leisure-type"
},{
    "name": "historic",
    "filter": [
        'nwr["historic"]',
    ],
    "properties": ["historic", "name", "memorial"],
    "replaceProperties": "historic-type"
},{
    "name": "amenity",
    "filter": [
        'nwr["amenity"]',
    ],
    "properties": ["amenity", "name", "healthcare"],
    "replaceProperties": "amenity-type"
}]
