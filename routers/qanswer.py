import requests
import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question, example_lang, example_kb, parse_gerbil, cache_question, find_in_cache

answer_api_url = "http://qanswer-core1.univ-st-etienne.fr/api/gerbil" # fetches one (first) answer and corresponding query
query_candidates_api_url = "https://qanswer-core1.univ-st-etienne.fr/api/qa/full?question={question}&lang={lang}&kb={kb}"

router = APIRouter(
    prefix="/qanswer",
    tags=["QAnswer"],
    responses={404: {"description": "Not found"}},
)

def prettify_answers(answers_raw):
    if 'results' in answers_raw.keys() and len(answers_raw['results']['bindings']) > 0:
        res = list()
        for uri in answers_raw['results']['bindings']:
            res.append(uri[list(uri.keys())[0]]['value'])
        return res
    else:
        return []
# TODO: restrict language and KB parameter https://fastapi.tiangolo.com/tutorial/body-fields/#declare-model-attributes

@router.get("/answer", description="Get answer URI")
async def get_answer(request: Request, question: str = example_question, lang: str = example_lang, kb: str = example_kb):
    cache = find_in_cache("qanswer", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    query_data = {'query': question, 'lang': lang, 'kb': kb}
    response = requests.post(answer_api_url, query_data).json()['questions'][0]['question'] # query to QAnswer
    # preparation of the final response
    final_response = { 'answer': None, 'answers_raw': None, 'SPARQL': None, 'confidence': None}
    final_response['answers_raw'] = json.loads(response['answers'])
    final_response['answer'] = prettify_answers(final_response['answers_raw'])
    final_response['SPARQL'] = response['language'][0]['SPARQL']
    final_response['confidence'] = response['language'][0]['confidence']
    # cache request and response
    cache_question('qanswer', request.url.path, question, query_data, final_response)
    ###
    return JSONResponse(content=final_response)


@router.get("/query_candidates", description="Get SPARQL query candidates")
async def get_query_candidates(request: Request, question: str = example_question, lang: str = example_lang, kb: str = example_kb):
    cache = find_in_cache("qanswer", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.get(
        query_candidates_api_url.format(question=question, lang=lang, kb=kb)
    ).json()
    final_response = {'queries': [q['query'] for q in response['queries']]}
    # cache request and response
    cache_question('qanswer', request.url.path, question, {'query': question, 'lang': lang, 'kb': kb}, final_response)
    ###
    return JSONResponse(content=final_response)


@router.get("/query_candidates_raw", description="Get raw SPARQL query candidates")
async def get_query_candidates_raw(request: Request, question: str = example_question, lang: str = example_lang, kb: str = example_kb):
    cache = find_in_cache("qanswer", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.get(
        query_candidates_api_url.format(question=question, lang=lang, kb=kb)
    ).json()
    final_response = [{'query': q['query'], 'confidence': q['confidence']} for q in response['queries']]
    # cache request and response
    cache_question('qanswer', request.url.path, question, {'query': question, 'lang': lang, 'kb': kb}, final_response)
    ###
    return JSONResponse(content=final_response)

@router.post("/gerbil_wikidata", description="Get response for GERBIL platform")
async def get_response_for_gerbil_over_wikidata(request: Request):
    cache = find_in_cache("qanswer", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)
        
    query, lang = parse_gerbil(str(await request.body()))
    query_data = {'query': query, 'lang': lang, 'kb': example_kb}
    response = requests.post(answer_api_url, query_data).json()['questions'][0]['question']
    final_response = {
        "questions": [{
            "id": "1",
            "question": [{
                "language": lang,
                "string": query
		    }],
            "query": {
			    "sparql": ""
		    },
            "answers": [json.loads(response['answers'])]   
        }]
    }
    # cache request and response
    cache_question('qanswer', request.url.path, query, query_data, final_response)
    ###
    return JSONResponse(content=final_response)