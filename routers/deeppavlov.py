import requests
import json
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question, example_lang, example_kb, cache_question, find_in_cache, parse_gerbil

api_url = "http://webengineering.ins.hs-anhalt.de:41120/answer?question={question}&lang={lang}"

router = APIRouter(
    prefix="/deeppavlov",
    tags=["DeepPavlov"],
    responses={404: {"description": "Not found"}},
)

@router.get("/answer", description="Returns list of answer URIs")
async def get_answer(request: Request, question: str = example_question, lang: str = example_lang):
    cache = find_in_cache("deeppavlov", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.get(
        api_url.format(question=question, lang=lang)
    ).json()
    final_response = {'answer': ['http://www.wikidata.org/entity/' + u for u in response['uri'] if u != 'NOTFOUND']}

    # cache request and response
    cache_question('deeppavlov', request.url.path, question, {'question': question, 'lang': lang}, final_response)
    ###
    return JSONResponse(content=final_response)

@router.get("/answer_raw", description="Returns raw output from the system")
async def get_raw_answer(request: Request, question: str = example_question, lang: str = example_lang):
    cache = find_in_cache("deeppavlov", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.get(
        api_url.format(question=question, lang=lang)
    ).json()
    # cache request and response
    cache_question('deeppavlov', request.url.path, question, {'question': question, 'lang': lang}, response)
    ###
    return JSONResponse(content=response)

def reinterpret(string):
    byte_arr = bytearray(ord(char) for char in string)
    return byte_arr.decode('utf8')

@router.post("/gerbil_wikidata", description="Get response for GERBIL platform")
async def get_response_for_gerbil_over_wikidata(request: Request):
    # cache = find_in_cache('qanswer_' + kb, request.url.path, question)
    # if cache:
        # return JSONResponse(content=cache)
        
    query, lang = parse_gerbil(str(await request.body()))
    print('GERBIL input:', query, lang)
    
    response = requests.get(
        api_url.format(question=query, lang=lang)
    ).json()

    if 'uri' in response.keys():
        answers = [{"x": {"type": "uri", "value": 'http://www.wikidata.org/entity/' + u }} for u in response['uri'] if u != 'NOTFOUND']
    else:
        answers = []
    
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

    # cache request and response
    # cache_question('qanswer_' + kb, request.url.path, query, query_data, final_response)
    ###
    return JSONResponse(content=final_response)
