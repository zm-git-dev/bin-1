#!/usr/bin/env python3
desc="""Plot the density of alignment identities.
"""
epilog="""Author: l.p.pryszcz+git@gmail.com
Barcelona, 25/4/2022
"""

import os
import sys
import pysam
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime


import os
import pysam
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

def qc_fail(a, mapq=15):
    """Return True if alignment fails quality checks"""
    if a.mapq<mapq or a.is_secondary or a.is_qcfail or a.is_supplementary:
        return True
    return False

def get_identities(bam, mapq=15):
    """Get alignment identities from BAM"""
    sam = pysam.AlignmentFile(bam)
    references, identities = [], []
    for a in sam: 
        if qc_fail(a, mapq): 
            continue
        # NM: Total number of mismatches and gaps in the alignment
        k2v = {k: v for k, v in a.tags}
        identity = 1-k2v['NM']/a.alen
        identities.append(identity)
        references.append(a.reference_name)
    return references, identities 

def identity_density(outfn, bams, names=[], mapq=15, title=""):
    """Plot density of alignment identities"""
    # get names
    if not names:
        names = [os.path.sep.join(bam[:-4].split(os.path.sep)[-2:]) for bam in bams]
    # start figure
    fig, ax = plt.subplots(figsize=(12, 4))
    legend = []
    for bam, name in zip(bams, names):
        references, identities = get_identities(bam)
        label = "%s: %.3f, %.3f"%(name, np.mean(identities), np.median(identities))
        sns.kdeplot(x=identities, ax=ax, label=label)
    ax.set_xlabel("Identity to reference")
    ax.legend()
    if title: ax.set_title(title)
    fig.savefig(outfn)
    #ax.set_xlim(0.6, )

def main():
    import argparse
    usage   = "%(prog)s -v" #usage=usage, 
    parser  = argparse.ArgumentParser(description=desc, epilog=epilog, \
                                      formatter_class=argparse.RawTextHelpFormatter)
  
    parser.add_argument('--version', action='version', version='1.0b') 
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose")
    parser.add_argument("-o", "--out", default="identity.pdf",
                        help="output name [%(default)s]")
    parser.add_argument("-i", "--bam", nargs="+", help="input BAM files")
    parser.add_argument("-n", "--name", default=[], nargs="*", 
                        help="sample names [use file names]")
    parser.add_argument("-m", "--mapq", default=15, type=int, 
                        help="min. mapping quality [%(default)s]")
    parser.add_argument("-t", "--title", default=15, type=int, 
                        help="min. mapping quality [%(default)s]")
    
    o = parser.parse_args()
    if o.verbose: 
        sys.stderr.write("Options: %s\n"%str(o))

    identity_density(o.out, o.bam, o.name, o.mapq, o.title)
    
if __name__=='__main__': 
    t0 = datetime.now()
    try:
        main()
    except KeyboardInterrupt:
        sys.stderr.write("\nCtrl-C pressed!      \n")
    #except IOError as e:
    #    sys.stderr.write("I/O error({0}): {1}\n".format(e.errno, e.strerror))
    dt = datetime.now()-t0
    sys.stderr.write("#Time elapsed: %s\n"%dt)
