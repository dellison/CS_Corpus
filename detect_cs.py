#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Implements CS voting model
"""
########################################################################
import sys, time
from is_language import *
########################################################################
start = time.time()
L = Lmodel(sys.argv[1])
print L.test('baraka')
print time.time() - start,"seconds"
