import json
from uuid import uuid4
from datetime import datetime
import os


with open("./utils/data.json") as json_file:
    config = json.load(json_file)


def load_config():
    return config

def load_data(config):
    keywords_class = list(config['keywords_class'].values())
    text_class = list(config['text_class'].values())
    liste_regex = list(config['liste_regex'].items())
    nbr_mot_chunk = config['nbr_mot_chunk']
    return keywords_class, text_class, liste_regex, nbr_mot_chunk

def download(data):
    uuid = uuid4()
    date = datetime.now().strftime('%d-%m-%Y')
    file_txt = f"Import {uuid}-{date}.txt"
    file_json = f"Import {uuid}-{date}.json"
    with open(os.path.join('./static/txt/', file_txt), 'w') as outfile:
        json.dump(data, outfile)
    with open(os.path.join('./static/json/', file_json), 'w') as outfile:
        json.dump(data, outfile)
    
    return file_json, file_txt


def validte_form(form):
    form.data = {}
    form.errors = {}
    
    if not form.get('input_class'):
        form.errors["input_class"] = "Class not selected"
    else:
        form.data["input_class"] = form.get('input_class')
        
    if not form.get('input_text_class'):
        form.errors["input_text_class"] = "Class text not selected"
    else:
        form.data["input_text_class"] = form.get('input_text_class')
    
    if not form.getlist('input_liste_regex'):
        form.errors["input_liste_regex"] = "Regex not selected"
    else:
        form.data["input_liste_regex"] = form.getlist('input_liste_regex')
    
    if not form.get('input_nbr_mot_chunk'):
        form.errors["input_nbr_mot_chunk"] = "Chunk not selected"
    else:
        form.data["input_nbr_mot_chunk"] = form.get('input_nbr_mot_chunk')
    
    return len(form.errors) == 0