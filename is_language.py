#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This code implements a basic language identifier by predicting the Maximum
Liklihood Estimate that some word is the same language as some input text.
Identification is acheived by predicting the probability of character 5grams
in a word.

1)  Call the object by initializing it with some training file:
    L = Lmodel(file)
2)Test by feeding a string into the model:
    mle = L.test('tanzania')
"""

__author__ = "Nick Kloehn"
__copyright__ = "Copyright 2015, Nick Kloehn"
__credits__ = []
__version__ = "1.0"
__maintainer__ = "Nick Kloehn"
__email__ = "See the author's website"

######################################################################
import math,re
from nltk.probability import FreqDist
######################################################################
######################################################################
#   Helper Functions
######################################################################
def clean_up(old_list):
    """Messy way to clean up the specific file and turn a line of text
    into some cleaned format."""
    new_list=[]
    junk=re.compile(r"""(?:(^\\\S*)|(\([a-z]\))|(\d+\:\S+)|[\.\,\-\[\]\"]+)""")
    for token in old_list:
        token=token.decode('utf-8')
        if junk.match(token):
            continue
        else: new_token = ''
        for char in token:
            if re.compile(r"""(?:(\W|\d|\_))""").match(char):
                continue
            else: new_token+=char
        token = new_token
        new_list.append(token.lower())
    return new_list

def extract_ngrams(line):
    """Messy extraction of 4,5-grams from a line. Should be done functionally"""
    # put each type of ngram in list of lists
    ngrams=[[],[]]
    for word in line:
        # add anchoring symbols and extract fourgrams
        word= '^^^^'+word+'$$$$'
        ngrams[0].append([word[char]
                         +word[char+1]
                         +word[char+2]
                         +word[char+3]
                         for char in range(len(word)-3)])
        # extract fivegrams
        ngrams[1].append([word[char]
                         +word[char+1]
                         +word[char+2]
                         +word[char+3]
                         +word[char+4]
                         for char in range(len(word)-4)])
    # flatten the list of each type of ngrams
    return [flatten_list(ngrams[tlist]) for tlist in range(len(ngrams))]

def flatten_list(list_of_lists):
    """Takes a lits of lists and return a single (flattened) list"""
    return [item for sublist in list_of_lists for item in sublist]

def get_prob_dist(ngram_list):
    """Takes a list of list of ngrams per line and calculates counts"""
    ngram_list= flatten_list(ngram_list)
    ngram_dist = FreqDist()
    for ngram in ngram_list:
        ngram_dist[ngram] += 1
    return ngram_dist

def merge_dicts(*dict_args):
    """Merges N dictionaries into a single one"""
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def log_prob(list):
    """Get the sum of the log of each number in a list"""
    p=0
    for i in list:
        p += math.log10(i)
    return math.exp(p)

def calculate_mle(list_of_ngrams,model):
    """Calculates the MLE of a word given our model using char fivegrams, e.g.
        1. For the word 'baraka', the MLE can be calculated for 5grams:
                P(^^^^baraka$$$$) =
                P(b|^^^^) * P(a|^^^b) * P(k|^^ba) * P(a|^bar) * P(k|bara) *
                P(a|arak) * P($|raka) * P($|aka$) * P($|ka$$) * P($|a$$$)
        2. To calculate the probability we divide the count the fivegram by the
           count of the fourgram preceding it:
                P(b|^^^^) = Count of ^^^^b / Count of ^^^^ and,
                P(a|^^^b) = Count of ^^^ba / Count of ^^^b, and ...
                P($|a$$$) = Count of a$$$$ / Count of a$$$
        3. To prevent underflow, we calculate the log10 of the probabilities
           and sum them, then use exp() of the sum:
                exp(log10(P(b|^^^^))+log10(P(ba|^^^))...+log10(P($|a$$$)))"""
    # declare lists
    fourgrams,fivegrams=list_of_ngrams
    # create dictionary for P (to be calculated) of each fivegram
    prob={}
    # smoothed count for unseen n-grams
    k = .01
    # go through each fivegram, and if it's been seen in training, calculate
    # its probability and make that the value of the 5gram key in the prob dict
    # if either the fourgram or fivegram hasn't been seen in training, smooth
    for i in range(len(fivegrams)):
        if fivegrams[i] in model:
            fivegram_count= model[fivegrams[i]]
        else:
            fivegram_count=k
        if fourgrams[i] in model:
            fourgram_count=model[fourgrams[i]]
        else:
            fourgram_count=k
        prob[fivegrams[i]]=float(fivegram_count)/fourgram_count
    return log_prob(prob.values())
######################################################################
# Object Methods
######################################################################
class Lmodel:
    def __init__(self,file):
        """Initialize model by reading in file and
        inputting probability distributions for
        1-5grams in a dictionary."""
        # declare lists for ngrams for whole document
        fourgrams,fivegrams = [],[]
        # read in file and clean
        f=re.split(r'\n', open(file).read())
        for line in f:
            line=re.split(r'\s',line)
            if len(line)>2:
                # get rid of unwanted characters
                line=clean_up(line)
                # split each line into 4,5grams
                ngrams_per_line=extract_ngrams(line)
                # add those lists of ngrams to document ngram list
                fourgrams.append(ngrams_per_line[0])
                fivegrams.append(ngrams_per_line[1])
        # Create probabilty distributtion for each type
        # of ngram, and merge them into one dictionary
        self.ngram_model = merge_dicts(get_prob_dist(fourgrams),
                                       get_prob_dist(fivegrams))

    def test(self,string):
        """Reads in some new input string and determines
        the probability that a given piece of text
        matches the trained language."""
        # put string into a list, and sep if multiple words
        # (shouldn't be the case)
        string=re.split(r'\s',string)
        # put in unicode
        string=[token.decode('utf-8') for token in string]
        # get rid of uninteresting symbols
        string=clean_up(string)
        # get fourgrams, and fivegrams
        list_of_ngrams=extract_ngrams(string)
        return calculate_mle(list_of_ngrams,self.ngram_model)
