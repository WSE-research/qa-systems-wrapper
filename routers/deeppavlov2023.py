import requests
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question, example_lang, example_kb, cache_question, find_in_cache, parse_gerbil

api_url_dict = {
    "en": "http://141.57.8.18:40196/respond",
    "ru": "http://141.57.8.18:40195/respond"
}

router = APIRouter(
    prefix="/deeppavlov2023",
    tags=["DeepPavlov2023"],
    responses={404: {"description": "Not found"}},
)

@router.get("/answer", description="Returns list of answer URIs")
async def get_answer(request: Request, question: str = example_question, lang: str = example_lang):
    cache = find_in_cache("deeppavlov2023", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    try:
        response = requests.post(
            api_url_dict[lang],
            json={"questions": [question]}
        ).json()
        
        if type(response) != list:
            final_response = {'answer': ['NOTFOUND']}
        elif len(response) > 0 and len(response[0]["answer_ids"]) > 0 and 'Q' in response[0]["answer_ids"][0]:
            final_response = {'answer': ['http://www.wikidata.org/entity/' + r for r in response[0]["answer_ids"]]}
        elif len(response) > 0 and len(response[0]) > 0 and 'Q' not in response[0]["answer_ids"][0]:
            final_response = {'answer': [r for r in response[0]["answer_ids"]]}
        else:
            final_response = {'answer': ['NOTFOUND']}

        # cache request and response
        cache_question('deeppavlov2023', request.url.path, question, {'question': question, 'lang': lang}, final_response)
        ###
    except Exception as e:
        print(str(e))
        final_response = {'answer': ['NOTFOUND']}

    return JSONResponse(content=final_response)

@router.get("/answer_raw", description="Returns raw output from the system")
async def get_raw_answer(request: Request, question: str = example_question, lang: str = example_lang):
    cache = find_in_cache("deeppavlov2023", request.url.path, question)
    if cache:
        return JSONResponse(content=cache)

    response = requests.post(
        api_url_dict[lang],
        json={"questions": [question]}
    ).json()
    # cache request and response
    cache_question('deeppavlov2023', request.url.path, question, {'question': question, 'lang': lang}, response)
    ###
    return JSONResponse(content=response)