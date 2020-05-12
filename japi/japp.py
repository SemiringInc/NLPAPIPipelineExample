#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
japp.py

(C) 2020 by Semiring Inc., Damir Cavar <damir@semiring.com>

The NLP-Lab Team 2019 (http://nlp-lab.org/) contributed to older code versions.

NLP pipeline server as a RESTful API engine using:
- spaCy
- benepar
- neurocoref
"""


from __future__ import unicode_literals, print_function
from collections import OrderedDict, defaultdict, Counter
from typing import Dict, Tuple, List
import datetime


__author__ = 'Damir Cavar <damir@semiring.com>'
__version__ = '1.0'
name = "japi"


def get_base() -> OrderedDict:
    """
    Return a base framework for JSON-NLP.

    :returns Base frame for a JSON-NLP object
    :rtype OrderedDict
    """

    return OrderedDict({
        "meta": {
            "DC.conformsTo": __version__,
            "DC.source": "",
            "DC.created": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "DC.date": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "DC.creator": "",
            'DC.publisher': "",
            "DC.title": "",
            "DC.description": "",
            "DC.identifier": "",
            "DC.language": "",
            "DC.subject": "",
            "DC.contributors": "",
            "DC.type": "",
            "DC.format": "",
            "DC.relation": "",
            "DC.coverage": "",
            "DC.rights": "",
            "counts": {},
        },
        "conll": {},
        "documents": []
    })


def get_base_document(doc_id: int) -> OrderedDict:
    """Returns a JSON base document."""

    return OrderedDict({
        "meta": {
            "DC.conformsTo": __version__,
            "DC.source": "",
            "DC.created": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "DC.date": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "DC.creator": "",
            'DC.publisher': "",
            "DC.title": "",
            "DC.description": "",
            "DC.identifier": "",
            "DC.language": "",
            "DC.subject": "",
            "DC.contributors": "",
            "DC.type": "",
            "DC.format": "",
            "DC.relation": "",
            "DC.coverage": "",
            "DC.rights": "",
            "counts": {},
        },
        "id": doc_id,
        "conllId": "",
        "text": "",
        "tokenList": [],
        "sentences": {},
        "paragraphs": {},
        "dependencies": [],
        "coreferences": [],
        "constituents": [],
        "expressions": [],
    })


def remove_empty_fields(json_nlp: OrderedDict) -> OrderedDict:
    """Remove all empty fields from root, meta, and documents."""

    cleaned = OrderedDict()
    for k, v in json_nlp.items():
        if v != '' and v != [] and v != {}:
            cleaned[k] = v
    if 'meta' in cleaned:
        cleaned['meta'] = remove_empty_fields(cleaned['meta'])
    if 'documents' in cleaned:
        for i in range(len(cleaned['documents'])):
            cleaned['documents'][i] = remove_empty_fields(cleaned['documents'][i])
    return cleaned


def find_head(doc: OrderedDict, token_ids: List[int], sentence_id: int, style='universal') -> int:
    """
    Given phrase, clause, or other group of token ids, use a dependency parse to find the head token.
    We create two sets, governors and dependents of the tokens in token_ids. The elements in gov that do not occur
    in dependents are the heads. There should be just one.
    """
    if len(token_ids) == 0:
        return None
    arcs = doc['dependencies'][sentence_id-1]['trees']
    govs = set(token_ids)
    for x in arcs:
        if x["dep"] in govs and x["gov"] in govs:
            govs.remove(x["dep"])
    govs = list(govs)
    if len(govs) == 0:
        return None
    return govs[0]


def build_coreference(reference_id: int) -> dict:
    """Build a frame for a coreference JSON object."""

    return {
        'id': reference_id,
        'representative': {
            'tokens': []
        },
        'referents': []
    }


def build_constituents(sent_id: int, s: str) -> dict:
    """Generates a frame for a constituent tree JSON object."""

    s = s.rstrip().lstrip()
    open_bracket = s[0]
    close_bracket = s[-1]
    return {
        'sentenceId': sent_id,
        'labeledBracketing': f'{open_bracket}ROOT {s}{close_bracket}' if s[1:5] != 'ROOT' else s
    }


def surface_string(tokens: List[OrderedDict], trim=False) -> str:
    """Generates a surface string from a list of tokens/strings."""

    s = ''.join([t['text'] + (' ' if t.get('misc', {}).get('SpaceAfter', 'No') == 'Yes' else '')
                for t in tokens])
    return s.rstrip() if trim else s


def subtract_tokens(a: List[OrderedDict], b: List[OrderedDict]) -> List[OrderedDict]:
    b_set = set(map(lambda t: t['id'], b))
    return [t for t in a if t['id'] not in b_set]

