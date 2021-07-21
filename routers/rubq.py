import requests
import json
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question_ru, cache_question, find_in_cache
import re

api_url = "http://localhost:9998/answer?question={question}"

router = APIRouter(
    prefix="/rubq",
    tags=["RuBQ"],
    responses={404: {"description": "Not found"}},
)

@router.get("/answer", description="Returns list of answer URIs")
async def get_answer(request: Request, question: str = example_question_ru):
    cache = find_in_cache("rubq", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.get(
        api_url.format(question=question)
    ).json()
    response['responses'] = [[a['value']for a in r] for r in response['responses']]
    final_response = {'answer': response['responses'][0]}
    # cache request and response
    cache_question('rubq', request.url.path, question, {'question': question}, final_response)
    ###
    return JSONResponse(content=final_response)

@router.get("/query_candidates", description="Returns list of answer URIs")
async def get_query_candidates(request: Request, question: str = example_question_ru):
    cache = find_in_cache("rubq", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)
        
    response = requests.get(
        api_url.format(question=question)
    ).json()
    prefixes = """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>

    """
    response['queries'] = [re.sub(' +', ' ', (prefixes + q).replace("\n", " ")).strip() for q in response['queries']]
    final_response = {'queries': response['queries']}
    # cache request and response
    cache_question('rubq', request.url.path, question, {'question': question}, final_response)
    ###
    return JSONResponse(content=final_response)