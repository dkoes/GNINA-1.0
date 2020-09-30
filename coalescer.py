#!/usr/bin/env python3

'''
Script to merge all of the *.rmsds files from obrms_calc.py into 1 master csv.
'''

import argparse, glob, re

parser=argparse.ArgumentParser(description='Merge OBRMS output files into 1 file')
parser.add_argument('-s','--suffix',type=str, required=True, help='Suffix of files to stick together. Assumes filenames are *<SUFFIX><VALUE>.rmsds')
parser.add_argument('-v','--values',type=str, default="",nargs='+',help='Values to be searched combined with suffix. Defaults to empty string. Accepts any number of arguments.')
parser.add_argument('-r','--dataroot',type=str,required=True, help='Root of directories to search')
parser.add_argument('-o','--outfilename',type=str,required=True, help='Name of output file')
parser.add_argument('-d','--dirlist',type=str,required=True, help='File containing directory names to work on.')
parser.add_argument('--getscores',action='store_true',help='Flag to expect CNNscore, CNNaffinity, and minimizedAffinity data fields in the .rmsds file.')

args=parser.parse_args()

if args.dataroot[-1]!='/':
	root=args.dataroot+'/'
else:
	root=args.dataroot

dirs=[x.rstrip() for x in open(args.dirlist).readlines()]

with open(args.outfilename, 'w') as outfile:
	if args.getscores:
		outfile.write('tag,molids,rmsd,cnnscore,cnnaffinity,minimizedAffinity,pocket,rec,lig\n')
	else:
		outfile.write('tag,molids,rmsd,pocket,rec,lig\n')
	for pocket in dirs:
		print(pocket)
		for val in args.values:
			todo=glob.glob(root+pocket+'*'+args.suffix+val+'.rmsds')

			for item in todo:
				lines2write=[x.rstrip() for x in open(item).readlines()]

				for line in lines2write:

					if line:
						if args.getscores:
							tag,molids,rmsd,cnnscore,cnnaff,vina=line.rstrip().split()
						else:
							tag,molids,rmsd=line.rstrip().split()
						if val!="":
							tag=val
						m=re.search(r'(\S+)_PRO_(\S+)_LIG',item)

						rec=m.group(1)
						lig=m.group(2)

						if args.getscores:
							newline=f"{tag},{molids},{rmsd},{cnnscore},{cnnaff},{vina},{pocket},{rec},{lig}\n"#line.replace(' ',',').rstrip()+','+','.join([pocket,rec,lig])+'\n'
						else:
							newline=f"{tag},{molids},{rmsd},{pocket},{rec},{lig}\n"#line.replace(' ',',').rstrip()+','+','.join([pocket,rec,lig])+'\n'

						outfile.write(newline)
