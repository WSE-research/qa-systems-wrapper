import requests
import json
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question, example_lang, example_kb, cache_question, find_in_cache, parse_gerbil

api_url = "https://qa.askplatyp.us/v0/ask?q={question}&lang={lang}"

router = APIRouter(
    prefix="/platypus",
    tags=["Platypus"],
    responses={404: {"description": "Not found"}},
)

@router.get("/answer", description="Returns list of answer URIs")
async def get_answer(request: Request, question: str = example_question, lang: str = example_lang):
    cache = find_in_cache("platypus", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    time.sleep(1) # requested by maintainer to reduce load on the server

    response = requests.get(
        api_url.format(question=question, lang=lang)
    ).json()
    
    result = list()
    if type(response['member']) == list:
        result = [m['result']['@id'].replace('wd:', 'http://www.wikidata.org/entity/') for m in response['member'] if '@id' in m['result'].keys()]
    else:
        result = [response['member']['result']['@id'].replace('wd:', 'http://www.wikidata.org/entity/')]
    final_response = {'answer': result}
    # cache request and response
    cache_question('platypus', request.url.path, question, {'question': question, 'lang': lang}, final_response)
    ###
    return JSONResponse(content=final_response)

@router.get("/answer_raw", description="Returns raw output from the system")
async def get_raw_answer(request: Request, question: str = example_question, lang: str = example_lang):
    cache = find_in_cache("platypus", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    time.sleep(1) # requested by maintainer to reduce load on the server

    response = requests.get(
        api_url.format(question=question, lang=lang)
    ).json()
    # cache request and response
    cache_question('platypus', request.url.path, question, {'question': question, 'lang': lang}, response)
    ###
    return JSONResponse(content=response)


@router.post("/gerbil_wikidata", description="Get response for GERBIL platform")
async def get_response_for_gerbil_over_wikidata(request: Request):
    # cache = find_in_cache('qanswer_' + kb, request.url.path, question)
    # if cache:
        # return JSONResponse(content=cache)
        
    query, lang = parse_gerbil(str(await request.body()))
    print('GERBIL input:', query, lang)
    
    time.sleep(1) # requested by maintainer to reduce load on the server

    response = requests.get(
        api_url.format(question=query, lang=lang)
    ).json()
    
    result = list()
    if type(response['member']) == list:
        result = [m['result']['@id'].replace('wd:', 'http://www.wikidata.org/entity/') for m in response['member'] if '@id' in m['result'].keys()]
    else:
        result = [response['member']['result']['@id'].replace('wd:', 'http://www.wikidata.org/entity/')]

    answers = [{"x": {"type": "uri", "value": u }} for u in result]
    
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
            "answers": [{
                'head': {
                    'vars': ['x']
                },
                'results': {
                    'bindings': answers
                }
            }]   
        }]
    }
    print(final_response)
    # cache request and response
    # cache_question('qanswer_' + kb, request.url.path, query, query_data, final_response)
    ###
    return JSONResponse(content=final_response)