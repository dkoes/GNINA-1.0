#!/usr/bin/env python
# coding: utf-8

# For the new pipeline using the python scripts in Paul's Repo
# Takes in one of the csv's output by the coalescer.py script (or something that looks like that)
import argparse
from datetime import datetime
# from glob import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib

matplotlib.use('Agg')


def makeOffset(number_labels, width=1):  # number_labels=number of bars that will be plotted on the multiple bargraph, width is the spread of the bars for a given tick
    # Generates the offset values for the bars to make a multiple bargraph
    max_numerator = number_labels // 2
    offset = np.arange(-max_numerator/number_labels, (max_numerator+1)/number_labels, width/number_labels).tolist()
    if not (number_labels % 2):  # special case when even
        spacing = width/number_labels  # spacing between the bars
        start = -(width/2 - spacing/2)
        offset = np.arange(start, start+spacing*(number_labels), spacing).tolist()
    return offset

def autolabel(rects, size, imp_ax):  # size is font-size of the annotation, imp_ax is the axis of the plotting
    # Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        imp_ax.annotate('{:.1f}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 6),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', size=size)

def getPlottingDataFrame(path, names, col_names, header, delim, usecols, key, unique):  # unique is the number of unique receptor-ligand systems that should exist
    # Generates a dataframe used for the graph making functions
    # Each row of dataframe is a cumulation of statistics of all poses before and the current pose
    # Each row has the percentage of Receptor-Ligand Systems with less than 1, 2, and 3 RMSD for 'good1', 'good2', and 'good3' respectively
    initial_df = pd.read_csv(path, header=header, sep=delim, usecols=usecols)
    initial_df.columns = col_names
    initial_df['good2'] = (initial_df['rmsd'] < 2)
    initial_df['good1'] = (initial_df['rmsd'] < 1)
    initial_df['good3'] = (initial_df['rmsd'] < 3)
    tags = initial_df[key[1]].unique()
    tags.sort()
    new_datafs = []
    new_ranges = []
    for tag, name in zip(tags, names):
        df_tagonly = initial_df[initial_df[key[1]] == tag]
        grouped_tagonly = df_tagonly.groupby(key[0])
        print(f"{name}: {tag}") 
        assert len(df_tagonly[key[0]].unique()) == unique, f"Doesn't have the right number of systems, should have {unique}, but has {len(initial_df[key[0]].unique())}"
        idx = grouped_tagonly.nth(0).index
        maxrange = grouped_tagonly.size().max()
        rang = list(range(1, maxrange+1))
        base = pd.DataFrame(None, index = idx, columns=['good1', 'good2', 'good3'])
        combin_top_df = pd.DataFrame(None, index = rang, columns=['good1', 'good2', 'good3']) #non_def_top -> combin_top_df
        top_bools = grouped_tagonly.nth(0)[['good1', 'good2', 'good3']] #non_def_last -> top_bools
        combin_top_df.loc[1] = [top_bools['good1'].mean()*100, top_bools['good2'].mean()*100, top_bools['good3'].mean()*100]
        for r in range(1, maxrange):
            cur_row = base.combine_first(grouped_tagonly.nth(r)[['good1', 'good2', 'good3']]).fillna(False)
            top_bools = cur_row | top_bools
            combin_top_df.loc[r+1] = [top_bools['good1'].mean()*100, top_bools['good2'].mean()*100, top_bools['good3'].mean()*100]
        new_datafs.append(combin_top_df)
        new_ranges.append(rang)

    return new_datafs, new_ranges


# Need to integrate the benchmark data here
# def getBenchmarkInfo(args):
#    performance_files = glob('{}*.{}'.format(args.benchmark_root, args.benchmark_ext)
#    performance_files.sort()
#    master_file = pd.DataFrame(columns = ['mean', 'stddev', 'median', 'min', 'max', 'parameter', 'prot'])
#    for sys in performance_files:
#        perf_stats = pd.read_csv(sys, delimiter=', ')
#        perf_stats['prot'] = perf_stats['command'].apply(lambda x: re.findall(r'(....)_PROT.pdb', x)[0])
#        del perf_stats['command'], perf_stats['user'], perf_stats['system']
#        master_file = master_file.append(perf_stats, ignore_index = True)
#    master_file['var'] = master_file['stddev'].apply(lambda x: x**2)
#    final_agg = master_grouped.agg({'mean':'mean', 'var': np.sum}).reset_index()
#    final_agg['std'] = final_agg['var'].apply(lambda x: np.sqrt(x))
#    return final_agg

def makeLineGraph(config, dfs, ranges):  # dfs are all of the computed dataframes, ranges are the ranges (i.e. number of poses) for the dataframes
    # Generates a line graph of the number of "good" dockings cumulatively for all of the poses
    ax = plt.figure().gca()
    for j, plot_df in enumerate(dfs):
        rang = ranges[j]
        p = plt.plot(rang, plot_df['good2'], label=config.compare_names[j])
        if config.use_bound:  # this adds shading to show the systems with dockings that are very "good" and less "good" (1 and 3 RMSD)
            plt.fill_between(rang, plot_df['good2'].astype('float64').values, plot_df['good1'].astype('float64').values, alpha = 0.1, color=p[-1].get_color())
            plt.fill_between(rang, plot_df['good2'].astype('float64').values, plot_df['good3'].astype('float64').values, alpha = 0.1, color=p[-1].get_color())
    prettifyGraph(ax, 'Top Number of Poses', '% of Systems with "good" docking', config.figname+'_line', xlim = 1, ylim=config.y_lim)

def makeBarGraph(config, dfs):
    # Generates a multiple bar graph for the specified poses that shows the percentage of good systems at those poses (this is cumulative still)
    ax = plt.figure().gca()
    offset = makeOffset(len(config.compare_names), config.width)
    for j, plot_df in enumerate(dfs):
        bar_info = [plot_df['good2'].iat[p-1] for p in config.use_pose]
        yerr = np.zeros(shape=(2, len(config.use_pose)), dtype=float)
        if config.use_bound:  # for showing error bars on the bars to denote the systems below 1 and 3 rmsd for - and + error respectively
            for p_idx, pose in enumerate(config.use_pose):
                yerr_pos = float(plot_df.iloc[pose-1]['good3'])-float(plot_df.iloc[pose-1]['good2']) 
                yerr_neg = float(plot_df.iloc[pose-1]['good2'])-float(plot_df.iloc[pose-1]['good1']) 
                yerr[p_idx,:] = [yerr_neg, yerr_pos]
        else:
            yerr = None
        rects = ax.bar(np.array(config.use_pose)+offset[j], bar_info, config.width/len(config.compare_names), align='center', label=config.compare_names[j], yerr=yerr, capsize=4)
        if config.annotate_size:  # adding annotations to the bars to tell their exact values
            autolabel(rects, config.annotate_size, ax)
    prettifyGraph(ax, 'Pose #', 'Percent Good Poses (<2 RMSD)', config.figname+'_bar', bargraph=config.use_pose, ylim=config.y_lim)

# Not Very sure how to integrate the benchmark info into this yet, will definitely update it later
# def makeBenchmarkGraph(config, dfs):
#    ax = plt.figure().gca()
#    for j, plot_df in enumerate(dfs):
#        bar_info = [plot_df['good2'].iat[p] for p in config.use_pose]
        
    

def prettifyGraph(imp_ax, xlabel, ylabel, figname, xlim=0, bargraph=False, ylim=None):  # bargraph should be the pose numbers that you are plotting bars for, to show the ticks for only those poses
    # Finalizes the graphs to make them goodlooking
    imp_ax.set_xlim(left=xlim)
    imp_ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    if bargraph:
        imp_ax.set_autoscalex_on(True)
        imp_ax.set_xticks(bargraph)
        imp_ax.set_autoscaley_on(True)
    if ylim is not None and not bargraph:
        imp_ax.set_ylim(top=ylim[1], bottom=ylim[0])
    imp_ax.set_xlabel(xlabel)
    imp_ax.set_ylabel(ylabel)
    box = imp_ax.get_position()
    imp_ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    lgd = imp_ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.savefig('{}.png'.format(figname), dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight')

parser = argparse.ArgumentParser()
parser.add_argument('--compare_paths', '-C', required=True, nargs='+', help="paths to all gnina runs' master rmsd files to compare")
parser.add_argument('--compare_names', '-N', required=True, nargs='+', help='Ordered names of gnina runs to use in Legend, order should be same as compare_paths')
parser.add_argument('--figname', '-F', default=str(datetime.now().time()), help='name to give to the figure, automatically appends "_line" and "_bar" to line and bar graphs, respectively')
parser.add_argument('--line_graph', default=False, action='store_true', help='Plot a line graph of the information')
parser.add_argument('--bar_graph', default=False, action='store_true', help='Plot a bar graph of the information')
parser.add_argument('--key', '-k', default=['rec', 'tag'], nargs='+', help='Column names to group the csv by.(default: %(default)s')
parser.add_argument('--delimiter', '-d', default=',', help='Delimiter that the files use (default=%(default)s)')
parser.add_argument('--usecols', default=[0, 2, 7], nargs='+', type=int, help='Columns of the data files that should be used')
parser.add_argument('--col_names', default=['tag', 'rmsd', 'rec'], nargs='+', help='Names of the columns in the dataframe')
parser.add_argument('--header', default=True, action='store_false', help='Use if the data does not have a header')
parser.add_argument('--num_unique', '-U', default=4260, type=int, help='number of unique rec-ligand pairs that should be in each file')
parser.add_argument('--use_bound', action='store_true', default=False, help='Plot upper and lower bounds on "good" fit, (<1 and <3 RMSD)')
parser.add_argument('--use_pose', default=[1, 3], type=int, nargs='+', help='which pose numbers to plot on the bar graph')
parser.add_argument('--annotate_size', default=12, type=int, help='size of the annotation to use, if 0 then no annotation')
parser.add_argument('--width', '-w', default=1.0, type=float, help='width of the spread of the bar graphs around the center')
parser.add_argument('--y_lim', '-y', nargs=2, type=float, help='lower and upper bounds of y limit for graphs, defaults to whatever matplotlib wants')
# parser.add_argument('--benchmark_graph', default = False, action='store_true', help='creates a graph that has benchmark timings vs performance')
args = parser.parse_args()

# assert len(args.compare_paths) == len(args.compare_names), "The number of paths is not the same as the number of names"
assert args.line_graph or args.bar_graph, "If you don't wanna make a graph, then why are you using this?"
if args.y_lim is not None:
    assert args.y_lim[1] <= 100 and args.y_lim[0] >= 0, "The y limit must be between 0 and 100 (its a percent)"

# make sure headers of pandas dataframes are handled correctly
if args.header:
    args.header = 'infer'
else:
    args.header = None

list_of_dataframes = []
list_of_ranges = []
names = args.compare_names
for i, path in enumerate(args.compare_paths):  # Calculate all of the dataframes to use for the graphs
    assert len(names), "The number of names is not the same as the amount of tags in all of the csvs provided"
    plot_df, rang = getPlottingDataFrame(path, names, args.col_names, args.header, args.delimiter, args.usecols, args.key, args.num_unique)
    names = names[len(plot_df):]
    list_of_dataframes += plot_df
    list_of_ranges += rang

if args.line_graph:
    makeLineGraph(args, list_of_dataframes, list_of_ranges)
    plt.clf()
if args.bar_graph:
    makeBarGraph(args, list_of_dataframes)
    plt.clf()
# if args.banchmark_graph:
#     benchmark_info = getBenchmarkInfo()
#     makeBenchmarkGraph(args, list_of_dataframes, benchmark_info)
