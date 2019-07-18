# omega-topology-taxonomy

> Gives to omega-topology-graph needed taxonomic tree and taxonomic terms.

Compute a minimal tree according to some taxonomic ids, or give terms related to some taxonomic ids.

> This micro-service is an REST JSON API, responding ONLY to JSON formatted requests.

## Installation

Simply clone the repo, then setup the virtual environnement.
```bash
git clone https://github.com/alkihis/omega-topology-taxonomy.git
mkdir ~/.envs
virtualenv --python=/usr/bin/python3.6 ~/.envs/omega-topology-taxonomy
cd omega-topology-taxonomy
source ~/.envs/omega-topology-taxonomy/bin/activate
pip3 install flask ete3 flask-cors
deactivate
```

In order to use properly the service, you need to force ete3 to generate taxonomy database:
```bash
# Enter virtual env
source ~/.envs/omega-topology-taxonomy/bin/activate
# Create script
echo "from ete3 import NCBITaxa
ncbi = NCBITaxa()
ncbi.update_taxonomy_database()" > init.py
# Run script then remove it
python init.py
rm init.py
# Exit virtual env
deactivate
```

## Starting the service
```bash
Usage: python src/main.py [options]

Options:
  -p, --port [portNumber]              Server port number (default: 3278)
```

- -p, --port &lt;portNumber&gt; : Port used by the micro-service to listen to request

```bash
# Enter inside the virtual env
source ./start.sh

# Run the service
python src/main.py
```

## Available endpoints

All endpoints are CORS-ready.

All endpoints use JSON-formatted body in request. In order to use JSON in body, **don't forget to add header `Content-Type: application/json`** in your request !

### POST /term
Get the organism name associated to a taxonomic ID.

Body must be JSON-formatted, and contain a object with one key `term`, linked to an array of stringified taxonomic ids.

- `@url` POST http://<µ-service-url>/term
- `@returns`
```json
{
    "success": true,
    "terms": {
        [taxId: string]: string
    }
}
```

### POST /tree
Get the minimal tree needed to link the multiple taxonomic ids together.

Body must be JSON-formatted, and contain a object with one key `taxids`, linked to an array of stringified taxonomic ids.

- `@url` POST http://<µ-service-url>/tree
- `@returns`
```ts
{
    "success": true,
    "tree": NodeTree
}

with interface NodeTree {
    [taxId: string]: { children: NodeTree[], name: string }
}
```


## Examples

### Getting organisms taxonomic names
```bash
curl -H "Content-Type: application/json" -d '{"term":["3719", "2384"]}' http://<µ-service-url>/term
```
```json
{
    "success": true,
    "terms": {
        "2384": "Epulopiscium sp.",
        "3719":" Capsella bursa-pastoris"
    }    
}
```
---
### Getting minimal taxonomic tree for the following taxonomic ids
```bash
curl -H "Content-Type: application/json" -d '{"taxids":["3719", "2384"]}' http://<µ-service-url>/tree
```
```json
{
    "success":true,
    "tree": {
        "131567": {
            "children": {
                "2384": {
                    "children": {},
                    "name": "Epulopiscium sp."
                },
                "3719":{ 
                    "children": {},
                    "name": "Capsella bursa-pastoris"
                }
            },
            "name": "cellular organisms"
        }
    }
}
```
