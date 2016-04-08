#caltags.py

from gensim import corpora, models, similarities
from collections import defaultdict
from pprint import pprint

from cal.schema import db, Event, Tag

stoplist = set('for a of the and to in'.split())

def tagsplit(str):
    return [word for word in str.lower.split() if word not in stoplist]

events = Event.query
for event in events:
    text = tagsplit(event.description)
    
    frequency = defaultdict(int)
    for token in text:
        frequency[token] += 1
        
    text = [token for token in text if frequency[token] > 1]
    pprint(text)
    