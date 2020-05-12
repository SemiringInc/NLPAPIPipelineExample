#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
server.py

(C) 2020 by Semiring Inc., Damir Cavar <damir@semiring.com>

The NLP-Lab Team 2019 (http://nlp-lab.org/) contributed to older code versions.

NLP pipeline server as a RESTful API engine using:
- spaCy
- benepar
- neurocoref
"""


from __future__ import unicode_literals, print_function

__author__ = 'Damir Cavar <damir@semiring.com>'
__version__ = '1.0'

name = "japi"
package = "japi"


import sys
import os
import os.path
import configparser
import plac
import spacy
import functools
import re
from collections import OrderedDict, defaultdict, Counter
from typing import Dict, Tuple, List
import neuralcoref
from benepar.spacy_plugin import BeneparComponent
from spacy.language import Language
from spacy.tokens import Doc
from flask import Flask, request
from flask_cors import CORS
from flask import jsonify
import html
import json
from .japp import get_base, get_base_document, remove_empty_fields, find_head, build_coreference, build_constituents, surface_string, subtract_tokens
from datetime import datetime


# RESTful service settings
port: str = str(9002)
host: str = "localhost"

# check for config.ini
iniPath = os.path.join(os.path.split(os.path.realpath(__file__))[0], "config.ini")
if os.path.exists(iniPath):
    config = configparser.ConfigParser()
    config.read(iniPath)
    if "DEFAULT" in config:
        default = config['DEFAULT']
        if 'port' in default:
            port = default['port']
        if 'host' in default:
            host = default['host']

app = Flask(__name__)
CORS(app) # Flask extension for handling Cross Origin Resource Sharing (CORS)


__cache = defaultdict(dict)


def cache_it(func):
    """A decorator to cache function response based on params. Add it to top of function as @cache_it."""

    global __cache
    @functools.wraps(func)
    def cached(*args):
        f_name = func.__name__
        s = ''.join(map(str, args))
        if s not in __cache[f_name]:
            __cache[f_name][s] = func(*args)
        return __cache[f_name][s]
    return cached


@cache_it
def get_model(spacy_model: str, coref: bool, constparse: bool) -> Language:
    """Loads a model for a language."""

    if spacy_model == 'en':
        spacy_model = 'en_core_web_sm'
    nlp = spacy.load(spacy_model)
    if coref:
        neuralcoref.add_to_pipe(nlp)
    if constparse:
        nlp.add_pipe(BeneparComponent("benepar_en2"))
    return nlp


def load_models(spacy_model: str, coref:str='', constituents:str='' ) -> Language:
    try:
        nlp = get_model(spacy_model)
        print('loaded spacy model: ' + spacy_model)
    except OSError as e:
        print(e)
        print('Missing spacy model. Try running: python spacy download ' + spacy_model)
        print('Defaulting to en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')
    if coref:
        neuralcoref.add_to_pipe(nlp)
    if constituents:
        nlp.add_pipe(BeneparComponent(constituents))
    return nlp


def process(text: str = None, spacy_model='en_core_web_sm', coreferences=True, constituents=True, dependencies=True, expressions=True) -> OrderedDict:
    """Process provided text"""

    nlp = get_model(spacy_model, coreferences, constituents)
    j: OrderedDict = get_base()
    d: OrderedDict = get_base_document(1)
    j['documents'].append(d)
    d['meta']['DC.source'] = 'NLP1 {}'.format(spacy.__version__)
    d['text'] = text
    doc = None
    food_ner = None
    if text:
        doc = nlp(text)
    else:
        return remove_empty_fields(j)

    model_lang = spacy_model[0:2]
    sent_lookup: Dict[int, int] = {}
    token_lookup: Dict[Tuple[int, int], int] = {}

    token_id = 1
    sent_num = 1
    for sent in doc.sents:

        current_sent = {
            'id': sent_num,
            'tokenFrom': token_id,
            'tokenTo': token_id + len(sent),
            'tokens': []
        }
        if constituents:
            try:
                d['constituents'].append(build_constituents(sent_num, sent._.parse_string))
            except Exception:
                pass

        sent_lookup[sent.end_char] = sent_num
        d['sentences'][current_sent['id']] = current_sent
        last_char_index = 0
        for token in sent:
            t = {
                'id': token_id,
                'sentence_id': sent_num,
                'text': token.text,
                'lemma': token.lemma_,
                'xpos': token.tag_,
                'upos': token.pos_,
                'entity_iob': token.ent_iob_,
                'characterOffsetBegin': token.idx,
                'characterOffsetEnd': token.idx + len(token),
                'lang': token.lang_,
                'features': {
                    'Overt': True,
                    'Stop': True if token.is_stop else False,
                    'Alpha': True if token.is_alpha else False,
                },
                'misc': {
                    'SpaceAfter': False
                }
            }

            t['shape'] = token.shape_

            if token.idx != 0 and token.idx != last_char_index:
                d['tokenList'][token_id-2]['misc']['SpaceAfter'] = True
            last_char_index = t['characterOffsetEnd']

            for i, kv in enumerate(nlp.vocab.morphology.tag_map.get(token.tag_, {}).items()):
                if i > 0:
                    t['features'][kv[0]] = str(kv[1]).title()

            if token.ent_type_:
                t['entity'] = token.ent_type_

            token_lookup[(sent_num, token.i)] = token_id
            current_sent['tokens'].append(token_id)
            d['tokenList'].append(t)
            token_id += 1

        d['tokenList'][token_id-2]['misc']['SpaceAfter'] = True
        sent_num += 1

    d['tokenList'][token_id-2]['misc']['SpaceAfter'] = False

    if expressions:
        chunk_id = 1
        for chunk in doc.noun_chunks:
            if len(chunk) > 1:
                sent_id = sent_lookup[chunk.sent.sent.end_char]
                d['expressions'].append({
                    'id': chunk_id,
                    'type': 'NP',
                    'head': token_lookup[(sent_id, chunk.root.i)],
                    'dependency': chunk.root.dep_.lower(),
                    'tokens': [token_lookup[(sent_id, token.i)] for token in chunk]
                })
                chunk_id += 1

    if dependencies:
        d['dependencies']=[]
        for sent_num, sent in enumerate(doc.sents):
            deps = {
            'style': "universal",
            'trees':[]
            }
            for token in sent:
                dependent = token_lookup[(sent_num+1, token.i)]
                deps['trees'].append({
                    'lab': token.dep_ if token.dep_ != 'ROOT' else 'root',
                    'gov': token_lookup[(sent_num+1, token.head.i)] if token.dep_ != 'ROOT' else 0,
                    'dep': dependent
                })
            d['dependencies'].append(deps)

    if coreferences and doc._.coref_clusters is not None:
        for cluster in doc._.coref_clusters:
            r = build_coreference(cluster.i)
            r['representative']['tokens'] = [t.i+1 for t in cluster.main]
            r['representative']['head'] = find_head(d, r['representative']['tokens'], d['tokenList'][max(r['representative']['tokens'])]['sentence_id'], 'universal')
            for m in cluster.mentions:
                if m[0].i+1 in r['representative']['tokens']:
                    continue
                ref = {'tokens': [t.i+1 for t in m]}
                ref['head'] = find_head(d, ref['tokens'], sent_num+1, 'universal')
                r['referents'].append(ref)
            d['coreferences'].append(r)

    d['meta']['DC.language'] = "en"

    return remove_empty_fields(j)


@app.route('/', methods=['POST', 'GET'])
def serv():
    """The main server function for Flask or WSGI."""

    text = None
    try:
        if request.method == 'POST':
            j = request.get_json()
            if j and "text" in j:
                text = j['text']
        if request.method == 'GET':
            if 'text' in request.args:
                text = request.args.get('text')
    except RuntimeError:
        pass
    if text:
        return app.response_class(
            response=json.dumps(process(text=text)),
            status=200,
            mimetype='application/json'
        )
    else:
        return app.response_class(
            status=204,
            mimetype='application/json'
        )
