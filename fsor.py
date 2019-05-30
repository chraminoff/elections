import random
import numpy as np
from collections import Counter
import itertools

# this file contains quick random election simulations

def randvs(*args):
    """
    Generates a string containing a number of copies (representing votes) of a single character,
    where the number follows a uniform distribution within a given range.
    1st arg: a character, denoting a party
    2nd arg: minimum nuber of votes
    3rd arg: maximum number of votes
    """
    return list("".join([a[0]*random.randrange(a[1],a[2]) for a in args]))

# concatenate a list of lists into one list
def concat(lst):
    return [elem for sublst in lst for elem in sublst]

# sum of multiple Counters in an iterable
def csum(itble):
    cs = Counter()
    for cntr in itble:
        cs += cntr
    return cs

def group(lst,num):
    """
    Group an iterable (lst) into a certain number (num) of groups.
    The groups are used to represent constituencies.
    """
    gsz = len(lst)//num
    rem = num - gsz
    gl = [lst[i*gsz:(i+1)*gsz] for i in range(num)]
    gl[-1] += lst[-rem:]
    return gl

# default settings for vote order arrangement based on normal distribution
ncenter = random.random()
nspread= 0.1
norm = lambda: random.gauss(ncenter,nspread)%1

def rgroup(lst,num,ndist=False):
    """
    Group the votes in a list (lst) into a number (num) of groups randomly,
    i.e. after shuffling the list. The shuffling follows a normal distribution
    if (ndist) is set to True.
    """
    slst = lst[:]
    if ndist:
         random.shuffle(slst,norm)
    else:
         random.shuffle(slst)
    return group(slst,num)

# represents a dictionary statistic (e.g. vote or seat totals) as percentages 
def pcts(dicti, rounding=2):
    return Counter({x[0]:round(x[1]*100./sum(dicti.values()),rounding) for x in dicti.items()})

#### The following functions compute seat distribution statistics (Counters) based on ####
#### generated, and if necessary, grouped, votes using different electoral systems    ####

# first-past-the-post in each constituency in gs
def fpps(gs):
    return Counter([max(set(g),key=lambda l:g.count(l)) for g in gs])

# random choice of (sts) voters in a constituency (g)
def rch(g,sts=1):
    return Counter(np.random.choice(g,sts, replace=False))

# one voter elected at random in each constituency
def sorts(gs):
    return Counter([random.choice(g) for g in gs])

def pr(g,sts,prm=1,thresh=0,minpties=1,mmp=None,oh=False):
    """
    Proportional representation in a single constituency using a highest averages method.

    g: votes as characters
    sts: number of seats to be distributed
    prm: interval between divisors for consecutive seats for a party in seat distribution (e.g. 1 for d'Hondt, 2 for Sainte-Lague)
    thresh: percentage threshold for a party to be allocated any seats at all (passing it doesn't guarantee seats)
    minpties: minimum number of parties that are allocated seats regardless of the threshold
    mmp: an initial seat distribution statistic (dictionary or Counter) (e.g. FPP results) to which seats are added
         so that the overall result is as proportional as possible (given the divisor interval)
    oh: if True, as many overhang seats beyond (sts) are added as are necessary in order to give each party
        at least as many seats as they would have been allocated if all (sts) seats were allocated proportionally
    """
    tally = Counter(g)
    totv = sum(tally.values())
    nonex = [x[0] for x in sorted(tally.items(),key=lambda l:l[1],reverse=True)[:minpties]]
    for t in tally.keys():
        if tally[t]*100./totv < thresh and t not in nonex:
            tally[t] = 0
    result = Counter()
    if mmp:
        if callable(mmp[0]):
            try:
                result = mmp[0](mmp[1],g,*mmp[2:])
            except TypeError:
                result = mmp[0](g,*mmp[1:])
        else:
            result = mmp
        for r in list(result.keys())*(not oh):
            tally[r] /= (1.+prm*result[r])
        mmpresult = result
    if oh:
        result = Counter({x:0 for x in tally.keys()})
    else:
        result += Counter({x:0 for x in tally.keys()})
    if type(prm) is not str:
        while sum(result.values()) < sts:
            seatee = max(tally.keys(),key=lambda l:tally[l])
            result[seatee] += 1
            tally[seatee] *= (1.+prm*(result[seatee]-1))/(1.+prm*result[seatee])
    if mmp and oh:
        for r in result.keys():
            result[r] = max(mmpresult[r],result[r])
    return result
     
     

def gappr(g,sts,factor=1,thresh=0,minpties=1,mmp=None,oh=False):
    """
    "Gap-proportional representation" (not actually proportional).
    An experimental seat distribution system that is intended to give the largest
    party a comfortable majority while maintaining a sizable opposition.
    The interval between seat distribution divisors is based on the winner's margin of victory.
    
    factor: multiplier for the divisor interval (higher values lead to higher proportionality)
    other parameters: same as for the pr function
    """
    best2 = sorted(Counter(g).items(), key=lambda l: -l[1])[:2]
    gap = best2[0][1]*1./best2[1][1]
    return pr(g,sts,factor*gap/sts,thresh,minpties,mmp,oh)

# proportional representation in each constituency in (gs)
def prs(gs,sts,prm=1,thresh=0, minpties=1,mmp=None,oh=False):
    return csum([pr(g,sts,prm,thresh, minpties,mmp,oh) for g in gs])
     
# gap-proportional representation
def gapprs(gs,sts,factor=1,thresh=0, minpties=1,mmp=None,oh=False):
    return csum([gappr(g,sts,factor,thresh, minpties, mmp,oh) for g in gs])

# first-past-the-post elections for (sts) sub-constituencies held in each constituency in (gs) 
def subfpps(gs,sts, *args):
    if "subr" in args: # sub-results included
        subr = [defpp(sts,g, *args) for g in gs]
        return (csum(subr),subr)
    return csum([defpp(sts,g, *args) for g in gs])


#### The following functions simulate elections based on generated but ungrouped votes ####
#### These can be used as helper functions when simulating MMP systems                 ####

def defsortition(sts, g, *args):
    tvlg = rgroup(g,sts,"uniform" not in args)
    if "s" in args:
        print(Counter(g))
        print(pcts(Counter(g)))
    sr = sorts(tvlg)
    if "s" in args or "st" in args:
        print(sr)
        print(pcts(sr))
    return sr

def defpp(sts, g, *args):
    tvlg = rgroup(g,sts,"uniform" not in args)
    if "s" in args:
        print(Counter(g))
        print(pcts(Counter(g)))
    ff = fpps(tvlg)
    if "s" in args or "st" in args:
        print(ff)
        print(pcts(ff))
    return ff

#### The following functions generate votes and simulate elections based on               ####
#### a list of (party, minimum, maximum) details given in the (v) parameter.              ####
#### Votes are then generated based on these details and then randomly grouped            ####
#### into (sts) groups (using normal distribution if the function name begins with n).    #### 

def sortition(sts,v):
    tvl = randvs(*v)
    tvlg = rgroup(tvl,sts)
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    srt = sorts(tvlg)
    print(srt)
    print(pcts(srt))
    return srt

def fpp(sts,v):
    tvl = randvs(*v)
    tvlg = rgroup(tvl,sts)
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    ff = fpps(tvlg)
    print(ff)
    print(pcts(ff))
    return ff


def nfpp(sts,v):
    ncenter = random.random()
    tvl = randvs(*v)
    tvlg = rgroup(tvl,sts,True)
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    ff = fpps(tvlg)
    print(ff)
    print(pcts(ff))
    return ff

def parallel(sts,gfuncparams,alfuncparams,v):
    """
    Parallel electoral system, where different members are chosen simultaneously
    according to different electoral systems. This (and nparallel) are the most
    versatile functions in this file, allowing for the simulation of a multitude
    of different electoral systems.

    sts: number of constituencies (districts)
    gfuncparams: list of electoral systems applied to each constituency, 
                 where function names have to end with s.
    alfuncparams: list of electoral systems applied to the electorate at large
    v: list of (party, minimum votes, maximum votes) details (tuples)

    Arguments to gfuncparams are given in the following format:
    [[function 1, argument 1 of function 1, argument 2 of function 1,..],
    [function 2, argument 1 of function 2, argument 2 of function 2,..],..]

    Example uses, *approximations* of real-life electoral systems:
    Chamber of Deputies of Mexico:
    5 regions, with 60 FPP and 40 PR (Sainte-Lague & 3% threshold) seats in each
    
    parallel(5,[[subfpps,60],[prs,40,2,3]],[],partyvotelist)

    National Assembly of South Korea:
    253 FPP seats and 47 at-large PR (Sainte-Lague and 3% threshold) seats 
    
    parallel(253,[[fpps]],[[pr,47,2,3]],partyvotelist)

    """
    tvl = randvs(*v)
    tvlg = rgroup(tvl,sts)
    print("")
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    para = csum([f[0](list(tvlg),*(list(f[1:]))) for f in gfuncparams])
    para += csum([f[0](list(tvl),*(list(f[1:]))) for f in alfuncparams])
    print(para)
    print(pcts(para))
    print("")
    return para

def nparallel(sts,gfuncparams,alfuncparams,v):
    """
    Normal-distribution version of parallel, which tends
    to result in more realistic simulations. 
    Same parameters used as in the parallel function.
    """
    tvl = randvs(*v)
    tvlg = rgroup(tvl,sts,True)
    print("")
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    para = Counter()
    for f in gfuncparams:
        fres = f[0](list(tvlg),*(list(f[1:])))
        print(f[0].__name__+":\n"+str(fres)+"\n"+str(pcts(fres)))
        para += fres
    for f in alfuncparams:
        fres = f[0](list(tvl),*(list(f[1:])))
        print(f[0].__name__+":\n"+str(fres)+"\n"+str(pcts(fres)))
        para += fres
    print(para)
    print(pcts(para))
    print("")
    return para


def fsor(fsts,ssts,v):
    """First-past-the-post and sortition in parallel
    
    Arguments:
        fsts {int} -- FPP seats
        ssts {int} -- sortition seats
        v {list((str,int,int))} -- list of (party, minimum votes, maximum votes) details (tuples)
    """
    ftresh, stresh = False, False
    try:
        1 > v[0]
        ftresh = True
        try:
            1 > v[1]
            stresh = True
        except TypeError:
            pass
    except TypeError:
        pass
    vs = list(v)
    vs = [x for x in vs[0:1] if not ftresh]+[x for x in vs[1:2] if not stresh]+vs[2:]
    tvl = randvs(*vs)
    ftvlg = rgroup(tvl,fsts)
    stvlg = rgroup(tvl,ssts)
    if ftresh:
        fexcl = [x[0] for x in pcts(Counter(tvl)).items() if x[1]<v[0]]
        if set(fexcl) == set(tvl):
            fexcl.remove(max(set(tvl),key=lambda l:tvl.count(l)))
        ftvlg = [[f for f in g if f not in fexcl] for g in ftvlg]
        if stresh:
            soexcl = [x[0] for x in pcts(Counter(tvl)).items() if x[1]<v[1]]
            if set(soexcl) == set(tvl):
                soexcl = []
            stvlg = [[f for f in g if f not in soexcl] for g in stvlg]
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    srt = sorts(stvlg)
    ff = fpps(ftvlg)
    print(srt+ff)
    print(pcts(srt+ff))


def nfsor(fsts,ssts,v):
    """
    Normal-distribution version of fsor using the same parameters
    """
    ncenter = random.random()
    ftresh, stresh = False, False
    try:
        1 > v[0]
        ftresh = True
        try:
            1 > v[1]
            stresh = True
        except TypeError:
            pass
    except TypeError:
        pass
    vs = list(v)
    vs = [x for x in vs[0:1] if not ftresh]+[x for x in vs[1:2] if not stresh]+vs[2:]
    tvl = randvs(*vs)
    ftvlg = rgroup(tvl,fsts,True)
    stvlg = rgroup(tvl,ssts,True)
    if ftresh:
        fexcl = [x[0] for x in pcts(Counter(tvl)).items() if x[1]<v[0]]
        if set(fexcl) == set(tvl):
            fexcl.remove(max(set(tvl),key=lambda l:tvl.count(l)))
        ftvlg = [[f for f in g if f not in fexcl] for g in ftvlg]
        if stresh:
            soexcl = [x[0] for x in pcts(Counter(tvl)).items() if x[1]<v[1]]
            if set(soexcl) == set(tvl):
                soexcl = []
            stvlg = [[f for f in g if f not in soexcl] for g in stvlg]
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    srt = sorts(stvlg)
    ff = fpps(ftvlg)
    print(srt+ff)
    print(pcts(srt+ff))

def recel(finsts,div,func,sts,*opt,**kwa):
    sps = kwa['sps'] if 'sps' in kwa else 1
    result = func(sts,*opt)
    while sum(result.values()) > finsts:
        result = func(max(finsts//sps,sum(result.values())//div),*(list(opt[:-1])+[[(x[0],x[1],x[1]+1) for x in result.items()]]))
    return result

########################################################
### FUNCTIONS SIMULATING A US-STYLE ELECTORAL SYSTEM ###
########################################################


sen = [Counter(),Counter(),Counter()] # senate classes
sencyc = 0
subr = [] # used for state-by-state House results

def uscyclep(v,*args):
    """Presidential and congressional election
    
    Arguments:
        v {list((str,int,int))} -- list of (party, minimum votes, maximum votes) details (tuples)
    """
    global sen, sencyc, subr
    tvl = randvs(*v)
    tvlg = rgroup(tvl,50,"uniform" not in args)
    sgs = [tvlg[i-1] for i in range(1,len(tvlg)+1) if (i-sencyc)%3 != 0]
    pres = prs(tvlg,11,0)
    house, subr = subfpps(tvlg,9,*(list(args)+["subr"]))
    up = fpps(sgs)
    sen[sencyc] = up
    sencyc = (sencyc+1)%3
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    print("President")
    print(pres)
    print(pcts(pres))
    print("Senate")
    print(Counter(concat(sgs)))
    print(pcts(Counter(concat(sgs))))
    print(csum(sen))
    print(pcts(csum(sen)))
    print("House")
    print(house)
    print(pcts(house))


def uscyclem(v,*args):
    """Midterm congressional election"""
    global sen, sencyc, subr
    tvl = randvs(*v)
    tvlg = rgroup(tvl,50,"uniform" not in args)
    sgs = [tvlg[i-1] for i in range(1,len(tvlg)+1) if (i-sencyc)%3 != 0]
    house, subr = subfpps(tvlg,9,*(list(args)+["subr"]))
    up = fpps(sgs)
    sen[sencyc] = up
    sencyc = (sencyc+1)%3
    print(Counter(tvl))
    print(pcts(Counter(tvl)))
    print("Senate")
    print(Counter(concat(sgs)))
    print(pcts(Counter(concat(sgs))))
    print(csum(sen))
    print(pcts(csum(sen)))
    print("House")
    print(house)
    print(pcts(house))

def uscyc(v):
    """Whichever election follows the previous one"""
    global ucpm
    func = uscyclem if ucpm else uscyclep
    func(v)
    ucpm = (ucpm+1)%2
    
     
def withcoal(el,spktr):    
        """ Description
        Most likely majority coalition and its combined seats

        :type el: dict
        :param el: election result (seats)
    
        :type spktr: list
        :param spktr: political spectrum
    
        :rtype: (list, int)
        """
    for n in range(1,len(spktr)+1):
        combos = [c for c in itertools.combinations(spktr,n) if sum(map(lambda l:el[l],c))>sum(el.values())/2. and "".join(c) in "".join(spktr)]
        combos.sort(key=lambda l:-sum(map(lambda m:(spktr.index(m)-len(spktr)/2.)**2,l)))
        if combos:
            return (sorted(combos[0],key=lambda l: -el[l]),sum(map(lambda l:el[l],combos[0])))



# Party maximum and minimum votes

# Generic (European) multi-party system
vlist = [("N",100,50000),("R",40000,100000),
         ("L",7000,32000),("C",3000,30000),("V",5000,34000),
         ("G",30000,110000),("K",1000,30000)]

# Something resembling the US party system
uslist = [('D', 90000, 110000),('R', 80000, 120000),('L', 200, 10000),('G', 500, 6000)]


# parallel(300,[[fpps]],[(pr,60,1,5)],*vlist)

# Calculates the minimum percentage of seats that needs to be given as a majority bonus
# to the largest party to ensure it wins at least half of all seats, given that it has won at least 
# majpct percent of the rest of the seats (usually through PR)
def majbonpct(majpct):
    return 100*(1+50./(majpct-100))

# number of majority bonus seats in an assembly of size allsts that gives a majority to 
# the plurality party, provided that it has won at least majpct percent of the other seats
def majbonseats(majpct, allsts):
    return int(allsts * majbonpct(majpct)/100.) + 1

# Example: In the current Greek electoral system, 250 of 300 seats are distributed proportionally.
# The 50 remaining seats, 16.7% of all seats, are allocated to the largest party. If it has won 
# 100 out of 250 proportional seats, i.e. 40% (achievable with slightly less than 40% of the votes), 
# it wins 150 out of 300 seats. Any further proportional seats give the party a majoity.
# Accordingly, majbonpct(40) = 16.666..


