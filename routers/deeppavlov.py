import requests
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from routers.config import example_question, example_lang, example_kb, cache_question, find_in_cache, parse_gerbil

api_url = "http://141.57.8.18:40198/query?question={question}&lang={lang}"

router = APIRouter(
    prefix="/deeppavlov",
    tags=["DeepPavlov"],
    responses={404: {"description": "Not found"}},
)

@router.get("/answer", description="Returns list of answer URIs")
async def get_answer(request: Request, question: str = example_question, lang: str = example_lang):
    # cache = find_in_cache("deeppavlov", request.url.path, question)
    # if cache:
        # return JSONResponse(content=cache)

    response = requests.get(
        api_url.format(question=question, lang=lang)
    ).json()
    final_response = {'answer': ['http://www.wikidata.org/entity/' + u for u in response['uri'] if u != 'NOTFOUND']}

    # cache request and response
    # cache_question('deeppavlov', request.url.path, question, {'question': question, 'lang': lang}, final_response)
    ###
    return JSONResponse(content=final_response)

@router.get("/answer_raw", description="Returns raw output from the system")
async def get_raw_answer(request: Request, question: str = example_question, lang: str = example_lang):
    # cache = find_in_cache("deeppavlov", request.url.path, question)
    # if cache:
        # return JSONResponse(content=cache)

    response = requests.get(
        api_url.format(question=question, lang=lang)
    ).json()
    # cache request and response
    # cache_question('deeppavlov', request.url.path, question, {'question': question, 'lang': lang}, response)
    ###
    return JSONResponse(content=response)

@router.post("/gerbil_wikidata", description="Get response for GERBIL platform")
async def get_response_for_gerbil_over_wikidata(request: Request):
    query, lang = parse_gerbil(str(await request.body()))
    print('GERBIL input:', query, lang)

    # cache = find_in_cache('deeppavlov_wikidata', request.url.path, query)
    # if cache:
        # return JSONResponse(content=cache)
    
    response = requests.get(
        api_url.format(question=query, lang=lang), timeout=90
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
    # cache_question('deeppavlov_wikidata', request.url.path, query, api_url.format(question=query, lang=lang), final_response)
    ###
    return JSONResponse(content=final_response)
