import requests
from rdflib import RDF, RDFS, OWL
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question, parse_gerbil, cache_question, find_in_cache, read_json
import re
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
api_url = "http://141.57.8.18:9999/gSolve/?data={{question:{question}}}"

# generate dict inline

concepts = {prefix + ":": read_json(f"static/gAnswer/{prefix}_concepts.json") for prefix in ["rdf", "rdfs", "owl", "dbo"]}
pref_uri = {
    "rdf:": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs:": "http://www.w3.org/2000/01/rdf-schema#",
    "owl:": "http://www.w3.org/2002/07/owl#",
    "dbo:": "http://dbpedia.org/ontology/",
    "dbr:": "http://dbpedia.org/resource/",
}
prefixes_query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?x  
WHERE {{
  VALUES ?x {{ {candidate_entities} }} 
  ?x ?a ?b .
}}
"""

router = APIRouter(
    prefix="/gAnswer",
    tags=["gAnswer"],
    responses={404: {"description": "Not found"}},
)

def add_prefixes(source_query):
    # load all possible prefixes and their corresponding classes and search for matches otherwise use dbr:
    prefixes = ['rdf:', 'rdfs:', 'owl:', 'dbo:']
    no_pref_ents = [e for e in re.findall(r'<(.*?)>', source_query) if ':' not in e]

    for ent in no_pref_ents:
        replacement = ''
        for prefix in prefixes:
            if prefix + ent in concepts[prefix]:
                replacement = pref_uri[prefix] + ent
                source_query = source_query.replace(ent, replacement)
                break
        # fallback to dbr:    
        if replacement == '':
            source_query = source_query.replace(ent, pref_uri['dbr:'] + ent)
        
    return source_query

@router.get("/answer", description="Returns list of SPARQL queries")
async def get_answer(request: Request, question: str = example_question):
    cache = find_in_cache("gAnswer", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.get(
        api_url.format(question=question)
    ).json()
    query = add_prefixes(response['sparql'][0].replace('\t',' '))
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    answer = list()
    for res in results["results"]["bindings"]:
        for v in list(res.values()):
            answer.append(v['value'])

    final_response = {'answer': answer}
    # cache request and response
    # cache_question('gAnswer', request.url.path, question, {'question': question}, final_response)
    ###
    return JSONResponse(content=final_response)

@router.get("/query_candidates", description="Returns list of SPARQL queries")
async def get_query_candidates(request: Request, question: str = example_question):
    cache = find_in_cache("gAnswer", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.get(
        api_url.format(question=question)
    ).json()
    final_response = {'queries': [add_prefixes(rq.replace('\t',' ')) for rq in response['sparql']]}
    # cache request and response
    cache_question('gAnswer', request.url.path, question, {'question': question}, final_response)
    ###
    return JSONResponse(content=final_response)


@router.get("/query_candidates_raw", description="Returns raw response")
async def get_query_candidates_raw(request: Request, question: str = example_question):
    cache = find_in_cache("gAnswer", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.get(
        api_url.format(question=question)
    ).json()
    # cache request and response
    cache_question('gAnswer', request.url.path, question, {'question': question}, response)
    ###
    return JSONResponse(content=response)


@router.post("/gerbil_dbpedia", description="Get response for GERBIL platform")
async def get_response_for_gerbil_over_dbpedia(request: Request):
    # cache = find_in_cache("gAnswer", request.url.path, question)
    # if cache:
    #    return JSONResponse(content=cache)

    question, lang = parse_gerbil(str(await request.body()))
    print('GERBIL input:', query, lang)
    response = requests.get(
        api_url.format(question=question)
    ).json()
    try:
        query = add_prefixes(response['sparql'][0].replace('\t',' '))
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        answers = sparql.query().convert()
    except:
        answers = {'head': {'link': [], 'vars': ['x']}, 'results': {'distinct': False, 'ordered': True, 'bindings': []}}

    final_response = {
        "questions": [{
            "id": "1",
            "question": [{
                "language": lang,
                "string": question
		    }],
            "query": {
			    "sparql": ""
		    },
            "answers": [answers]   
        }]
    }
    # cache request and response
    # cache_question('gAnswer', request.url.path, question, {'question': question}, final_response)
    ###
    return JSONResponse(content=final_response)