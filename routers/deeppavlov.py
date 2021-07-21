import requests
import json
import time
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question, example_lang, example_kb, cache_question, find_in_cache

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
