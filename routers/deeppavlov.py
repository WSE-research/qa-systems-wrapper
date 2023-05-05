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
    
    if type(response) != list:
        final_response = {'answer': ['NOTFOUND']}
    elif len(response) > 0 and len(response[0]) > 0 and 'Q' in response[0][1]:
        final_response = {'answer': ['http://www.wikidata.org/entity/' + response[0][1]]}
    elif len(response) > 0 and len(response[0]) > 0 and 'Q' not in response[0][1] and not response[0][0] == 'Not Found':
        final_response = {'answer': ['http://www.wikidata.org/entity/' + response[0][0]]}
    else:
        final_response = {'answer': ['NOTFOUND']}

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

    if type(response) != list:
        answers = []
    elif len(response) > 0 and len(response[0]) > 0 and 'Q' in response[0][1]:
        answer_value = 'http://www.wikidata.org/entity/' + response[0][1]
    elif len(response) > 0 and len(response[0]) > 0 and 'Q' not in response[0][1] and not response[0][0] == 'Not Found':
        answer_value = 'http://www.wikidata.org/entity/' + response[0][0]
    else:
        answer_value = 'NOTFOUND'

    if 'uri' in response.keys():
        answers = [{"x": {"type": "uri", "value": answer_value}}]
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
