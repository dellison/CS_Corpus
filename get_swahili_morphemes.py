#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,re,nltk
#get rid of extralinguistic lines
def clean_up(old_list):
    new_list=[]
    junk=re.compile(r"""(?:(^\\\S*)|(\([a-z]\))|(\d+\:\S+)|[\.\,\-\[\]\"]+)""")
    for token in old_list:
        token=token.decode('utf-8')
        if junk.match(token):
            continue
        new_list.append(token.lower())
    return new_list

class Parse:
    def __init__(self):
        pass
    def split_morphs(self,file):
        cleaned_doc=[]
        f=re.split(r'\n', open(file).read())
        for line in f:
            line=re.split(r'\s',line)
            print line,'\n'

Parse().split_morphs(sys.argv[1])
