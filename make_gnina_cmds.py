#!/usr/bin/env python3

'''
This script aims to create a text file with a line per gnina command that needs to be run.

Input:
	infile         -- a space-delimited file containing: <recfile> <ligfile> <autobox_ligand file>
	cnn            -- defaults to gnina default. Must be in [crossdock_default2018, crossdock_default2018_<1-4>, 
																default2017, dense, dense_<1-4>, 
																general_default2018, general_default2018_<1-4>]. *if multiple args are given, it is an ensemble
	cnn_scoring    -- defaults to rescore. Must be in [none, rescore, refinement, all].
	exhaustiveness -- number(s)
	rmsd_filter    -- number(s)
	cnn_rotations  -- number(s)
	num_modes      -- number(s)
	autobox_add    -- number(s)
	num_mc_saved   -- number(s)

	--gpu : this will turn on gpu acceleration for the command.

The name of the output file for the gnina command will be the name of the receptor+ligand+"option"+.sdf

Output:
	a text file with a command per line.
'''

import argparse,os

def gen_docking_prefix(receptor,ligand):
	'''
	Helper function to generate the outfile prefix for a given receptor ligand pair
	'''
	r=receptor.split('.')[0]
	l=ligand.split('/')[-1].split()[0]
	outname=f'{r}_{l}_'
	return outname


parser=argparse.ArgumentParser(description='Create a text file containing all the gnina commands you specify to run.')
parser.add_argument('-i','--input',required=True,help='Space-delimited file containing the Receptor file, Ligand file, and autobox ligand file')
parser.add_argument('-o','--output',default='gnina_cmds.txt',help='Name of the output file containing the commands to run. Defaults to "gnina_cmds.txt"')
parser.add_argument('--cnn',default=None,nargs='+',help="Specify built-in CNN model for gnina. Default is to use gnina's default. If multiple models are specified, an ensemble will be evaluated.")
parser.add_argument('--cnn_scoring',default='rescore',help='Specify what method of CNN scoring. Must be [none, rescore,refinement,all]. Defaults to rescore')
parser.add_argument('--exhaustiveness',default=None,nargs='+',help='exhaustiveness arguments for gnina. Accepts any number of arguments.')
parser.add_argument('--min_rmsd_filter',default=None,nargs='+',help='Filters for min_rmsd_filter for gnina. Accepts any number of arguments.')
parser.add_argument('--cnn_rotation',default=None,nargs='+',help='Options for cnn_rotation for gnina. Accepts any number of arguments. All must be [0,24].')
parser.add_argument('--num_modes',default=None,nargs='+',help='Options for num_modes for gnina. Accepts any number of arguments.')
parser.add_argument('--autobox_add',default=None,nargs='+',help='Options for autobox_add for gnina. Accepts any number of arguments.')
parser.add_argument('--num_mc_saved',default=None,nargs='+',help='Options for num_mc_saved for gnina. Accepts any number of arguments.')
parser.add_argument('--gpu',action='store_true',help='Flag to turn on gpu acceleration for gnina.')
args=parser.parse_args()

#Checking that the input arguments make sense
if args.cnn_rotation:
	for rot in args.cnn_rotation:
		assert (0<=int(rot) and int(rot)<=24),"cnn_rotations need to be in [0,24]!"

assert (args.cnn_scoring in ['none','rescore','refinement','all']),"cnn_scoring must be one of none,rescore,refinement,all!"

if args.cnn:
	possible=[
	'crossdock_default2018','crossdock_default2018_1','crossdock_default2018_2',
	'crossdock_default2018_3','crossdock_default2018_4','default2017',
	'dense','dense_1','dense_2','dense_3','dense_4','general_default2018',
	'general_default2018_1','general_default2018_2','general_default2018_3',
	'general_default2018_4','general_default2018_5',
	]
	for cnn in args.cnn:
		assert(cnn in possible),"Specified cnn not built into gnina!"

#Specifying arguments to skip over
skip=set(['input','output','cnn','cnn_scoring','gpu'])

#Gathering the receptor, ligand, and autobox_ligand arguments from input
todock=[] #list of tuples (recfile,ligfile,autobox_ligand,outf_prefix)
with open(args.input) as infile:
	for line in infile:
		rec,lig,box=line.rstrip().split()
		todock.append((rec,lig,box,gen_docking_prefix(rec,lig)))

#main part of the program
with open(args.output,'w') as outfile:
	for arg in vars(args):
		print(arg)
		if arg not in skip:
			if getattr(args,arg):
				for val in getattr(args,arg):
					print(val)
					for r, l, box, out_prefix in todock:
						sent=f'gnina -r {r} -l {l} --autobox_ligand {l} --cnn_scoring {args.cnn_scoring} --cpu 1 --seed 420'
						if args.cnn:
							dock_out=out_prefix+'_'.join[args.cnn]+'_'+args.cnn_scoring+'_'+arg+val+'.sdf'
							sent+=f' --cnn {" ".join(args.cnn)} --out {dock_out}'
						else:
							dock_out=out_prefix+'_crossdock_default2018_'+args.cnn_scoring+'_'+arg+val+'.sdf'
							sent+=f' --out {dock_out}'

						#adding in the stuff for the specified argument
						sent+=f' --{arg} {val}'
						if args.gpu:
							sent+=' --gpu'

						outfile.write(sent+'\n')