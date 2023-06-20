from fastapi import APIRouter, Request, Body
from fastapi.responses import JSONResponse
from qanary_helpers import qanary_queries

import json
import requests
import logging
import ast

from routers.config import example_question, parse_gerbil, dummy_answers, find_in_cache, cache_question, example_lang


logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

router = APIRouter(
    prefix="/qanary",
    tags=["Qanary"],
    responses={404: {"description": "Not found"}},
)

api_url = "http://pie.qanary.net:8000/startquestionansweringwithtextquestion"

@router.get("/query_candidates", description="Get query candidates")
async def get_query_candidates(self, question: str = example_question, lang: str = example_lang) -> str:
    final_response = {}
    
    return JSONResponse(content=final_response)

@router.post("/answers", description="Get answers")
async def get_answers(request: Request, question: str = example_question, lang: str = example_lang, components_list: list = []) -> str:
    cache = find_in_cache(system_name='_'.join(c for c in components_list), path=request.url.path, question=question)
    if cache:
        return JSONResponse(content=cache)

    try:
        response = requests.post(
            url=api_url,
            params={
                "question": question,
                "componentlist[]": components_list,
            },
            timeout=20
        ).json()

        sparql = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
            PREFIX qa: <http://www.wdaqua.eu/qa#>
            SELECT DISTINCT ?jsonValue
            FROM <{graphId}> 
            WHERE {{
                ?s a qa:AnnotationOfAnswerJson ;
                    oa:hasBody ?body .
                ?body rdf:value ?jsonValue .
            }}
        """

        response = qanary_queries.select_from_triplestore(response["endpoint"], sparql.format(graphId=response["inGraph"]))
        answer = json.loads(response["results"]["bindings"][0]["jsonValue"]["value"]) # load the answer from the response

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
                "answers": [answer]
            }]
        }
        
        cache_question(system_name='_'.join(c for c in components_list), path=request.url.path, question=question, input_params=components_list, output=final_response)
    except Exception as e:
        logger.error("Error in Qanary.gerbil_response: {0}".format(str(e)))
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
                "answers": [dummy_answers]   
            }]
        }
    logger.info('Qanary response: {0}'.format(str(final_response)))
    
    return JSONResponse(content=final_response)

@router.get("/answers_raw", description="Get answers raw")
async def get_answers_raw(self, question: str = example_question) -> str:
    response = requests.post(
        url=self.api_url,
        params={
            "question": question,
            "componentlist[]": self.components_list,
        }
    ).json()
    return JSONResponse(content=response)

@router.post("/gerbil", description="Get gerbil response")
async def gerbil_response(self, request: Request) -> str:
    try:
        request_body = str(await request.body())
        question, lang = parse_gerbil(request_body) # get question and language from the gerbil request
        
        logger.info('GERBIL input: {0}, {1}'.format(question, lang))
        
        cache = find_in_cache(system_name='_'.join(c for c in self.components_list), path=request.url.path, question=question)
        if cache:
            return JSONResponse(content=cache)

        
        response = requests.post(
            url=self.api_url,
            params={
                "question": question,
                "componentlist[]": self.components_list,
            },
            timeout=20
        ).json()

        sparql = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
            PREFIX qa: <http://www.wdaqua.eu/qa#>
            SELECT DISTINCT ?jsonValue
            FROM <{graphId}> 
            WHERE {{
                ?s a qa:AnnotationOfAnswerJson ;
                    oa:hasBody ?body .
                ?body rdf:value ?jsonValue .
            }}
        """

        response = qanary_queries.select_from_triplestore(response["endpoint"], sparql.format(graphId=response["inGraph"]))
        answer = json.loads(response["results"]["bindings"][0]["jsonValue"]["value"]) # load the answer from the response

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
                "answers": [answer]
            }]
        }
        
        cache_question(system_name='_'.join(c for c in self.components_list), path=request.url.path, question=question, input_params=self.components_list, output=final_response)
    except Exception as e:
        logger.error("Error in Qanary.gerbil_response: {0}".format(str(e)))
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
                "answers": [dummy_answers]   
            }]
        }
    logger.info('Qanary response: {0}'.format(str(final_response)))
    
    
    
    return JSONResponse(content=final_response)
