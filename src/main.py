from ete3 import NCBITaxa
from flask import Flask, request, jsonify
from flask_cors import CORS
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int, default=3278, help="Port")

program_args = parser.parse_args()

"""
Convert a TreeNodeObject returned by NCBITaxa to a dictionary (filled by reference)
@param ncbi: NCBITaxa object
@param root: Dictionnary used as root of current (sub)tree
@param curr_node: Current used node of explored tree (instanceof TreeNodeObject)
"""
def node_to_dict(ncbi, curr_node):
    taxid = curr_node.name

    return {
        'children': { node.name: node_to_dict(ncbi, node) for node in curr_node.children },
        'name': ncbi.get_taxid_translator([int(taxid)])[int(taxid)]
    }

app = Flask("omega-topology-taxonomy")
CORS(app)

term_cache = {}

"""
Respond a JSON containing the organisms name of the given taxids.
@expecting HTTP POST; Content-Type: application/json; Body: { "term" [:listofIDs] }
@returns JSON response; Body: { success: true, terms: TermsObj }; TermsObj as { [taxId: string]: string }
"""
@app.route('/term', methods=['POST'])
def get_term_of():
    if not request.is_json:
        return jsonify(success=False, reason="Bad content type"), 400

    data = request.json

    if not 'term' in data:
        return jsonify(success=False, reason="Taxonomic IDs are missing"), 400

    if not isinstance(data['term'], list) and not isinstance(data['term'], str):
        return jsonify(success=False, reason="Taxonomic IDs must be sended as a string array or a simple string"), 400

    ncbi = NCBITaxa() # Obligé de l'instancier à chaque requête; Requiert un SQLite qui demande un thread ID == thread appelant

    terms = {}

    if isinstance(data['term'], str):
        data['term'] = [data['term']]

    for term in data['term']:
        if term in term_cache:
            terms[term] = term_cache[term]
        else:
            taxnames = ncbi.get_taxid_translator([int(term)])
            if len(taxnames) > 0:
                for term_fetched in taxnames:
                    terms[str(term_fetched)] = term_cache[str(term_fetched)] = taxnames[term_fetched]
            else:
                # No term!
                return jsonify(success=False, reason="Term not found"), 404
        


    return jsonify(success=True, terms=terms)


"""
Respond a JSON containing taxonomic tree of requested IDs
@expecting HTTP POST; Content-Type: application/json; Body: { "taxids" [:listofIDs] }
@returns JSON response; Body: { success: true, tree: NodeTree }; NodeTree as { [taxId: string]: { children: NodeTree[], name: string } }
"""
@app.route('/tree', methods=['POST'])
def get_taxo_of():
    if not request.is_json:
        return jsonify(success=False, reason="Bad content type"), 400

    data = request.json

    if not 'taxids' in data:
        return jsonify(success=False, reason="Taxonomic IDs are missing"), 400

    if not isinstance(data['taxids'], list):
        return jsonify(success=False, reason="Taxonomic IDs must be sended as a string array"), 400

    ncbi = NCBITaxa() # Obligé de l'instancier à chaque requête; Requiert un SQLite qui demande un thread ID == thread appelant
    sended_list = data['taxids']

    # Convert every string ID of the list to integers
    # Map returns an iterator, so the value error will not append when creating it
    sended_list = map(lambda x: int(x), sended_list)

    try: # Use the iterator
        tree_topology = ncbi.get_topology(sended_list)
    except ValueError:
        return jsonify(success=False, reason="One of the sended IDs is not a valid integer"), 400

    # Constructing root
    tree = { tree_topology.name: node_to_dict(ncbi, tree_topology) }

    return jsonify(success=True, tree=tree)

@app.errorhandler(405) # Method Not Allowed
def method_not_allowed(e):
    return jsonify(success=False, reason="Method not allowed"), 400

@app.errorhandler(404) # Page Not Found
def page_not_found(e):
    return '', 404

@app.errorhandler(500)
def server_error(e):
    return jsonify(success=False, reason="Unexpected internal server error", error=repr(e)), 500

# Run integrated Flask server
app.run(host='0.0.0.0', port=program_args.port)
