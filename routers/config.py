from pymongo import MongoClient
import re
from datetime import datetime

mongo_client = MongoClient('webengineering.ins.hs-anhalt.de:41052',
    username='admin',
    password='admin',
    authSource='admin'
)

db = mongo_client.qa_systems_cache

print(db.command("serverStatus"))

example_question = "Where was Angela Merkel born?"
example_question_ru = "Где место рождения Ангелы Меркель?"
example_lang = "en"
example_kb = "wikidata"

def parse_gerbil(body):
    body = eval(body).decode('utf-8').split('&')
    query, lang = body[0][body[0].index('=')+1:], body[1][body[1].index('=')+1:-1]
    return query, lang

def preprocess(question):
    return re.sub('[^A-Za-zА-Яа-яÀ-žÄäÖöÜüß0-9]+', ' ', question).lower().strip()

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