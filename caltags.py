#caltags.py

import re
import string

from flask import current_app
from gensim import corpora, models, similarities
from collections import defaultdict
from pprint import pprint

from cal import app
from cal.schema import db, Event, Tag, EventTag

stoplist = set('for a of the and to in or by in as this he she them him her which at is'.split())
punc_regex = re.compile('[%s]' % re.escape(string.punctuation))
alpha_regex = re.compile('[a-z]+')

def tokenize(content):
    content_no_punc = punc_regex.sub('', content)
    documents = [content_no_punc]
    texts = [[word for word in alpha_regex.findall(document.lower()) if word not in stoplist]
        for document in documents]
    
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    
    texts = [token for token in frequency if frequency[token] > 1]
    #pprint(texts)
    return texts

'''
class EventDescriptionCorpus(object):
    def __iter__(self):
        for event in Event.query:
            yield dictionary.doc2bow(event.description.lower().split())
            
with app.app_context():
    ed_corpus = EventDescriptionCorpus()
    for vector in ed_corpus:
        print(vector)
'''

with app.app_context():

    EventTag.query.delete()
    Tag.query.delete()
    db.session.commit()

    def tagsplit(str):
        this_list = [word for word in str.lower().split() if word not in stoplist]
        return this_list

    events = Event.query
    tags = []
    documents = []
    for event in events:
        tags += [tokenize(event.description)]
        '''
        documents = [event.description]
        texts = [[word for word in document.lower().split() if word not in stoplist]
            for document in documents]
        
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1
        
        texts = [token for token in frequency if frequency[token] > 1]
        #pprint(texts)
        tags += [texts]
        '''
    
    #pprint(tags)
    dictionary = corpora.Dictionary(tags)
    
    #dictionary.save('event_descriptions.dict')
    for token, tid in dictionary.token2id.items():
        #print(token + ":" + str(tid) + "\n")
        new_tag = Tag(id=tid, tag=token)
        db.session.add(new_tag)
    
    db.session.commit()
    #print(dictionary.token2id)
    
    corpus = [dictionary.doc2bow(tag) for tag in tags]
    #print(corpus)
    tfidf = models.TfidfModel(corpus)
    
    events_to_tag = Event.query
    event_count = events_to_tag.count()
    event_num = 0
    for event in Event.query:
        event_num += 1
        ed_tags = [tokenize(event.description)]
        ed_dict = corpora.Dictionary(ed_tags)
        ed_corp = [ed_dict.doc2bow(ed_tag) for ed_tag in ed_tags]
        ed_tfidf = tfidf[ed_corp]
        #print('//////////////')
        for doc in ed_tfidf:
            '''
            print('==================')
            pprint(doc)
            print('==================')
            '''
            tag_count = len(doc)
            tag_num = 0
            for id,weight in doc:
                tag_num += 1
                print("Processing tag %d of %d in event %d of %d"
                    % (tag_num, tag_count, event_num, event_count))
                tagname = ed_dict[id]
                orig_tagid = Tag.query.filter_by(tag=tagname).first().id
                '''
                print(orig_tagid)
                '''
                new_eventtag = EventTag(tag_id=orig_tagid, event_id=event.id, ed_weight=weight)
                db.session.add(new_eventtag)
                #print("Added tag %s for event %d" % (tagname, event.id))
                '''
                print(tagname + ":" + str(weight))
                '''
            
        '''
        for doc in corpus_tfidf:
            print(doc)
        '''
        db.session.commit()