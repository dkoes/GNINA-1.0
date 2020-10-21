#!/usr/bin/env python3

'''
This is a script that takes as an argument a directory name and docking job lines.

It then will use obrms to calculate the true rmsd to the correct ligand.

The --CNNscore flag will trigger the use of sdsorter to sort the molecule by CNNscore instead of minimizedAffinity
	before performing the obrms calculation.
'''


import argparse, re
from plumbum.cmd import obrms
from plumbum.cmd import grep
from plumbum.cmd import zgrep

def get_lig_out(instring):
	'''
	Use RE to pull the -l and the -o arguments from the string.
	'''

	lig=re.split(pattern=' -l ',string=instring)[1].split()[0]
	out=re.split(pattern=' --out ',string=instring)[1].split()[0]

	return (lig,out)

def splitter(intuple, pattern):
	'''
	Split pattern out of each item in intuple.

	This applies after get_lig_out
	'''

	return (intuple[0].split(pattern)[1], intuple[1].split(pattern)[1])

parser=argparse.ArgumentParser(description='Run OBRMS on docking outputs')
parser.add_argument('-i','--input',type=str, required=True, help='Name of docking jobs file.')
parser.add_argument('-d','--dirname',type=str,required=True, help='Name of directory the job will work on')
parser.add_argument('-s','--splitprefix',type=str,default=None, help='Text prefix to split off of filepaths in input. Defaults to None')
parser.add_argument('--getscores',action='store_true', help='Flag to output the CNNscore, CNNaffinity, and minimizedAffinity in the output file (in that order)')

args=parser.parse_args()


todo=open(args.input).readlines()
todo=[get_lig_out(x) for x in todo if args.dirname in x]

if args.splitprefix:
	todo=[splitter(x, args.splitprefix) for x in todo]


#we now have a list of (lig, dockedlig) tuples.
for lig, dockedlig in todo:

	outname=dockedlig.split('.sdf')[0]+'.rmsds'

	if args.getscores:
		if dockedlig.endswith('.gz'):
			cnnscores=re.findall("-?\d+\.\d+",(zgrep['-A1','CNNscore',dockedlig])())
			cnnaffs=re.findall("-?\d+\.\d+",(zgrep['-A1','CNNaffinity',dockedlig])())
			vinascores=re.findall("-?\d+\.\d+",(zgrep['-A1','minimizedAffinity',dockedlig])())
		else:
			cnnscores=re.findall("-?\d+\.\d+",(grep['-A1','CNNscore',dockedlig])())
			cnnaffs=re.findall("-?\d+\.\d+",(grep['-A1','CNNaffinity',dockedlig])())
			vinascores=re.findall("-?\d+\.\d+",(grep['-A1','minimizedAffinity',dockedlig])())
		items=(obrms[dockedlig,lig])().split('\n')
		with open(outname,'w') as outfile:
			for start,cnnscore,cnnaff,vina in zip(items,cnnscores,cnnaffs,vinascores):
				outfile.write(f'{start} {cnnscore} {cnnaff} {vina}\n')
	else:
		(obrms[dockedlig,lig] > outname)()
