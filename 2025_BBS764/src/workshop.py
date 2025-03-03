#!/usr/bin/env python3

import argparse
import json
from copy import deepcopy


# Parse command line arguments
parser = argparse.ArgumentParser(description='Process workshop notebook file.')
parser.add_argument('path_in', type=str, help='Input raw file path')
parser.add_argument('path_out_student', type=str, help='Output processed file path')
parser.add_argument('path_out_presentation', type=str, help='Output processed file path')
args = parser.parse_args()
path_in = args.path_in
path_out_student = args.path_out_student
path_out_presentation = args.path_out_presentation

key='# Your code:'
key2=['#### Your code starts here ####', '##### Your code ends here #####']
key_pref='###'

with open(path_in,'r') as f:
	d=json.load(f)

cells_student=[]
cells_presentation=[]

for xi0,xi in enumerate(d['cells']):
	if 'outputs' not in xi or 'source' not in xi:
		cells_student.append(xi)
		cells_presentation.append(xi)
		continue
	s1=[]
	s2=[]
	haskey=False
	xj0=0
	while xj0<len(xi['source']):
		xj=xi['source'][xj0]
		if xj.strip()==key2[0]:
			xk0=xj0+1
			while xk0<len(xi['source']):
				xk=xi['source'][xk0]
				if xk.strip()==key2[1]:
					break
				if key in xk:
					raise NotImplementedError('Only one fragment is allowed to contain the key in each subslide.')
				xk0+=1
			if xk0>=len(xi['source']):
				raise NotImplementedError('The code block is not closed.')
			haskey=True
			s1+=[xj,xj[:len(xj)-len(xj.lstrip())]+'???\n',xi['source'][xk0]]
			s2+=xi['source'][xj0+1:xk0]
			xj0=xk0+1
			continue
		if key not in xj:
			s1.append(xj)
			s2.append(xj)
			xj0+=1
			continue
		haskey=True
		t1=xj.split(key)
		assert len(t1)==2
		s1.append(t1[0][:len(t1[0])-len(t1[0].lstrip())]+key_pref+key+t1[1])
		s2.append(t1[0]+'\n')
		xj0+=1
	if not haskey:
		cells_student.append(xi)
		cells_presentation.append(xi)
		continue
	t1=deepcopy(xi)
	t1['source']=s1
	cells_student.append(t1)
	current_slide=len(cells_presentation)
	cells_presentation.append(t1)

	# Additional considerations for fragment slides to replicate context slides
	# For presentation, needs to find the last subslide and next fragment
	last_subslide=len(cells_presentation)-2
	fragment_slides=[]
	while last_subslide>=0:
		if 'metadata' in cells_presentation[last_subslide] and 'slideshow' in cells_presentation[last_subslide]['metadata'] and 'slide_type' in cells_presentation[last_subslide]['metadata']['slideshow']:
			if cells_presentation[last_subslide]['metadata']['slideshow']['slide_type'] in {'subslide','slide'}:
				break
			if cells_presentation[last_subslide]['metadata']['slideshow']['slide_type']=='fragment':
				fragment_slides.append(last_subslide)
		last_subslide-=1
	if last_subslide<0:
		last_subslide=0
	if any(any(key in y for y in x['source']) for x in cells_presentation[last_subslide:-1]):
		raise NotImplementedError('Only one fragment is allowed to contain the key in each subslide.')
	next_fragment=xi0+1
	while next_fragment<len(d['cells']):
		if 'metadata' in d['cells'][next_fragment] and 'slideshow' in d['cells'][next_fragment]['metadata'] and 'slide_type' in d['cells'][next_fragment]['metadata']['slideshow']:
			break
		next_fragment+=1
	for idx, cell in enumerate(d['cells'][xi0+1:next_fragment], start=xi0+1):
		for line in cell['source']:
			if key in line:
				raise NotImplementedError(f'Only one fragment is allowed to contain the key in each subslide. Found in cell {idx}, line: {line}.')
	
	# Insert slides till next fragment
	cells_presentation+=d['cells'][xi0+1:next_fragment]
	# Insert slides from the last subslide but remove fragment tags
	t1=deepcopy(cells_presentation[last_subslide:current_slide])
	# Treat the first slide as subslide
	t1[0]['metadata']['slideshow']['slide_type']='subslide'
	# Remove fragment tags from the rest of the slides
	for xj in t1[1:]:
		if 'metadata' in xj and 'slideshow' in xj['metadata'] and 'slide_type' in xj['metadata']['slideshow']:
			del xj['metadata']['slideshow']['slide_type']
	cells_presentation+=t1
	# Insert current fragment without fragment tags
	t1=deepcopy(xi)
	t1['source']=s2
	if 'metadata' in t1 and 'slideshow' in t1['metadata'] and 'slide_type' in t1['metadata']['slideshow']:
		del t1['metadata']['slideshow']['slide_type']
	cells_presentation.append(t1)

d1=deepcopy(d)
d1['cells']=cells_student
d2=deepcopy(d)
d2['cells']=cells_presentation

with open(path_out_student,'w') as f:
	json.dump(d1,f,indent=1)
with open(path_out_presentation,'w') as f:
	json.dump(d2,f,indent=1)


#    "metadata": {
#     "slideshow": {
#      "slide_type": "subslide"
#     }