import numpy as np
import pandas as pd
import prody
from openbabel import openbabel, pybel
import multiprocessing, subprocess
import os
from functools import partial


def calc_pocket_rmsd(rec, lig, root):
    """
    Calculate difference between the ligand reference receptor and
    the receptor it is being docked into.

    From original script by David Koes
    """
    ligrec = lig.replace("LIG_aligned.sdf", "PRO.pdb")
    rec = prody.parsePDB(os.path.join(root, rec))
    ligrec = prody.parsePDB(os.path.join(root, ligrec))
    lig = next(pybel.readfile("sdf", os.path.join(root, lig)))
    c = np.array([a.coords for a in lig.atoms])
    nearby = rec.select("protein and same residue as within 3.5 of point", point=c)
    matches = []
    for cutoff in range(90, 0, -10):
        # can't just set a low cutoff since we'll end up with bad alignments
        # try a whole bunch of alignments to maximize the likelihood we get the right one
        m = prody.matchChains(
            rec, ligrec, subset="all", overlap=cutoff, seqid=cutoff, pwalign=True
        )
        if m:
            matches += m
    minrmsd = np.inf
    minbackrmsd = np.inf
    for rmap, lrmap, _, _ in matches:
        try:
            closeatoms = set(nearby.getIndices())
            lratoms = []
            ratoms = []
            for i, idx in enumerate(rmap.getIndices()):
                if idx in closeatoms:
                    lratoms.append(lrmap.getIndices()[i])
                    ratoms.append(idx)
            if len(lratoms) == 0:
                continue
            rmsd = prody.calcRMSD(rec[ratoms], ligrec[lratoms])
            backrmsd = prody.calcRMSD(rec[ratoms] & rec.ca, ligrec[lratoms] & ligrec.ca)
            if rmsd < minrmsd:
                minrmsd = rmsd
                minbackrmsd = backrmsd
        except:
            pass
    return minrmsd, minbackrmsd


def process_line(line, root):
    rec, lig, _, _ = line.replace("/scr/paul/", "").split()
    try:
        return (rec, lig, *calc_pocket_rmsd(rec, lig, root))
    except:
        return (rec, lig, np.inf, np.inf)


if __name__ == "__main__":
    root = "/net/pulsar/home/koes/paf46/Research/gnina1.0"
    ifile = os.path.join(root, "ds_cd_input_pairs.txt")

    rec, lig, _, _ = open(ifile).readline().replace("/scr/paul/", "").split()
    print(rec, lig)
    print(calc_pocket_rmsd(rec, lig, root))

    pool = multiprocessing.Pool(6)

    pocket_rmsds = pool.map(partial(process_line, root=root), list(open(ifile)))

    rmsds = np.array([r for (_, _, r, br) in pocket_rmsds])
    validrmsds = rmsds[~np.isinf(rmsds)]

    targetdiff = pd.DataFrame(
        [
            (
                r.replace("_PRO.pdb", "")[-4:],
                l.replace("_LIG_aligned.sdf", "")[-4:],
                rmsd,
                br,
            )
            for r, l, rmsd, br in pocket_rmsds
        ],
        columns=("rec", "lig", "pocket_change", "backbone_change"),
    )

    print(targetdiff)
    targetdiff.to_csv("pocketdiff.csv")
