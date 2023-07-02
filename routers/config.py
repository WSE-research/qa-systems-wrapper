import re
import json
from datetime import datetime
from pymongo import MongoClient


example_question = "Where was Angela Merkel born?"
example_question_ru = "Где место рождения Ангелы Меркель?"
example_lang = "en"
example_kb = "wikidata"

dummy_answers = {
    "head": {
        "link": [],
        "vars": [
            "dummy"
        ]
    },
    "results": {
        "bindings": []
    }
}

mongo_client = MongoClient('141.57.8.18:40200',
    username='admin',
    password='admin123',
    authSource='admin'
)

db = mongo_client.qa_systems_cache

def parse_gerbil(body):
    body = eval(body).decode('utf-8').split('&')
    query, lang = body[0][body[0].index('=')+1:], body[1][body[1].index('=')+1:]
    return query, lang

def preprocess(question):
    return re.sub('[^A-Za-zА-Яа-яÀ-žÄäÖöÜüß0-9]+', ' ', question).lower().strip()

def delete_cache(system_name: str, path: str):
    try:
        db[system_name].delete_many({'path': path})
    except Exception as e:
        print(str(e))

def find_in_cache(system_name: str, path: str, question: str):
    try:
        result = db[system_name].find_one({'question': preprocess(question), 'path': path})
        if result:
            return result['output']
        else:
            return None
    except Exception as e:
        print(str(e))
        return None

def cache_question(system_name: str, path: str, question: str, input_params, output):
    try:
        document = {
            'path': path,
            'question': preprocess(question),
            'raw_question': question,
            'input_params': input_params,
            'output': output,
            'date': datetime.now()
        }
        db[system_name].insert_one(document)
    except Exception as e:
        print(str(e))

def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)