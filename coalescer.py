#!/usr/bin/env python3

'''
Script to merge all of the *.rmsds files from obrms_calc.py into 1 master csv.
'''

import argparse, glob, re

parser=argparse.ArgumentParser(description='Merge OBRMS output files into 1 file')
parser.add_argument('-s','--suffix',type=str, required=True, help='Suffix of files to stick together.')
parser.add_argument('-r','--dataroot',type=str,required=True, help='Root of directories to search')
parser.add_argument('-o','--outfilename',type=str,required=True, help='Name of output file')
parser.add_argument('-d','--dirlist',type=str,required=True, help='File containing directory names to work on.')

args=parser.parse_args()

if args.dataroot[-1]!='/':
	root=args.dataroot+'/'
else:
	root=args.dataroot

dirs=[x.rstrip() for x in open(args.dirlist).readlines()]

with open(args.outfilename, 'w') as outfile:
	outfile.write('tag,molids,rmsd,pocket,rec,lig\n')
	for pocket in dirs:
		print(pocket)
		todo=glob.glob(root+pocket+'*'+args.suffix)

		for item in todo:
			lines2write=[x.rstrip() for x in open(item).readlines()]

			for line in lines2write:

				if line:
					m=re.search(r'(\S+)_PRO_(\S+)_LIG',item)

					rec=m.group(1)
					lig=m.group(2)
					
					newline=line.replace(' ',',').rstrip()+','+','.join([pocket,rec,lig])+'\n'

					outfile.write(newline)
