import requests
import json
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question, cache_question, find_in_cache, example_lang
import re

full_api_url = "https://tebaqa.demos.dice-research.org/qa"
simple_api_url = "https://tebaqa.demos.dice-research.org/qa-simple"

router = APIRouter(
    prefix="/tebaqa",
    tags=["TeBaQA"],
    responses={404: {"description": "Not found"}},
)

@router.get("/answer_raw", description="Returns raw answer form the system")
async def get_answer(request: Request, question: str = example_question, lang: str = example_lang):
    cache = find_in_cache("tebaqa", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    query_data = {'query': question, 'lang': lang}
    response = requests.post(full_api_url, query_data).json()
    final_response = response

    # cache request and response
    cache_question('tebaqa', request.url.path, question, {'question': question, 'lang': lang}, final_response)
    ###

    return JSONResponse(content=final_response)

@router.get("/answer", description="Returns list of answer URIs (not candidates, hence, non-ranked list)")
async def get_query_candidates(request: Request, question: str = example_question, lang: str = example_lang):
    cache = find_in_cache("tebaqa", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    try:
        query_data = {'query': question, 'lang': lang}
        response = requests.post(simple_api_url, query_data).json()
        final_response = {'answer': response['answers'], 'sparql': response['sparql']}

        # cache request and response
        cache_question('tebaqa', request.url.path, question, {'question': question, 'lang': lang}, final_response)
        ###
    except Exception as e:
        print(str(e))
        final_response = {'answer': ['NOTFOUND']}

    return JSONResponse(content=final_response)