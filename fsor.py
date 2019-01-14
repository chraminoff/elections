import random
import numpy as np
from collections import Counter

# this file contains quick random election simulations

def randvs(*args):
     return list("".join([a[0]*random.randrange(a[1],a[2]) for a in args]))

def concat(lst):
    return [elem for sublst in lst for elem in sublst]

def csum(itble):
     cs = Counter()
     for cntr in itble:
         cs += cntr
     return cs


def group(lst,num):
     gsz = len(lst)//num
     rem = num - gsz
     gl = [lst[i*gsz:(i+1)*gsz] for i in range(num)]
     gl[-1] += lst[-rem:]
     return gl

ncenter = random.random()
nspread= 0.1
norm = lambda: random.gauss(ncenter,nspread)%1

def rgroup(lst,num,ndist=False):
     slst = lst[:]
     if ndist:
          random.shuffle(slst,norm)
     else:
          random.shuffle(slst)
     return group(slst,num)

def pcts(dicti, rounding=2):
     return Counter({x[0]:round(x[1]*100./sum(dicti.values()),rounding) for x in dicti.items()})

def fpps(gs):
     return Counter([max(set(g),key=lambda l:g.count(l)) for g in gs])
     
def rch(g,sts=1):
    return Counter(np.random.choice(g,sts, replace=False))

def sorts(gs):
      return Counter([random.choice(g) for g in gs])

def pr(g,sts,prm=1,thresh=0,minpties=1,mmp=None,oh=False):
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
    best2 = sorted(Counter(g).items(), key=lambda l: -l[1])[:2]
    gap = best2[0][1]*1./best2[1][1]
    return pr(g,sts,factor*gap/sts,thresh,minpties,mmp,oh)

def prs(gs,sts,prm=1,thresh=0, minpties=1,mmp=None,oh=False):
     return csum([pr(g,sts,prm,thresh, minpties,mmp,oh) for g in gs])
     

def gapprs(gs,sts,factor=1,thresh=0, minpties=1,mmp=None,oh=False):
     return csum([gappr(g,sts,factor,thresh, minpties, mmp,oh) for g in gs])


def sortition(sts,*v):
     tvl = randvs(*v)
     tvlg = rgroup(tvl,sts)
     print(Counter(tvl))
     print(pcts(Counter(tvl)))
     srt = sorts(tvlg)
     print(srt)
     print(pcts(srt))
     return srt

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

def fpp(sts,*v):
     tvl = randvs(*v)
     tvlg = rgroup(tvl,sts)
     print(Counter(tvl))
     print(pcts(Counter(tvl)))
     ff = fpps(tvlg)
     print(ff)
     print(pcts(ff))
     return ff

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

def subfpps(gs,sts, *args):
     if "subr" in args:
          subr = [defpp(sts,g, *args) for g in gs]
          return (csum(subr),subr)
     return csum([defpp(sts,g, *args) for g in gs])

def nfpp(sts,*v):
     ncenter = random.random()
     tvl = randvs(*v)
     tvlg = rgroup(tvl,sts,True)
     print(Counter(tvl))
     print(pcts(Counter(tvl)))
     ff = fpps(tvlg)
     print(ff)
     print(pcts(ff))
     return ff

def cfpps(gs):
     return Counter([max(g.keys(),key=lambda l:g[l]) for g in gs])

def parallel(sts,gfuncparams,alfuncparams,*v):
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

def nparallel(sts,gfuncparams,alfuncparams,*v):
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


def fsor(fsts,ssts,*v):
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


def nfsor(fsts,ssts,*v):
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

def recel(finsts,div,func,sts,*v):
     result = func(sts,*v)
     while sum(result.values()) > finsts:
          result = func(max(finsts,sum(result.values())//div),*[(x[0],x[1],x[1]+1) for x in result.items()])
     return result

sen = [Counter(),Counter(),Counter()]
sencyc = 0
subr = []

def uscyclep(v,*args):
     global sen, sencyc, subr
     tvl = randvs(*v)
     tvlg = rgroup(tvl,50,"uniform" not in args)
     sgs = [tvlg[i-1] for i in range(1,len(tvlg)+1) if (i-sencyc)%3 != 0]
     forseti = prs(tvlg,11,0)
     down, subr = subfpps(tvlg,9,*(list(args)+["subr"]))
     up = fpps(sgs)
     sen[sencyc] = up
     sencyc = (sencyc+1)%3
     print(Counter(tvl))
     print(pcts(Counter(tvl)))
     print("P")
     print(forseti)
     print(pcts(forseti))
     print("S")
     print(Counter(concat(sgs)))
     print(pcts(Counter(concat(sgs))))
     print(csum(sen))
     print(pcts(csum(sen)))
     print("H")
     print(down)
     print(pcts(down))


def uscyclem(v,*args):
     global sen, sencyc, subr
     tvl = randvs(*v)
     tvlg = rgroup(tvl,50,"uniform" not in args)
     sgs = [tvlg[i-1] for i in range(1,len(tvlg)+1) if (i-sencyc)%3 != 0]
     down, subr = subfpps(tvlg,9,*(list(args)+["subr"]))
     up = fpps(sgs)
     sen[sencyc] = up
     sencyc = (sencyc+1)%3
     print(Counter(tvl))
     print(pcts(Counter(tvl)))
     print("S")
     print(Counter(concat(sgs)))
     print(pcts(Counter(concat(sgs))))
     print(csum(sen))
     print(pcts(csum(sen)))
     print("H")
     print(down)
     print(pcts(down))
     
     
def withcoal(el,spktr):
    for n in range(1,len(spktr)+1):
        combos = [c for c in itertools.combinations(spktr,n) if sum(map(lambda l:el[l],c))>sum(el.values())/2. and "".join(c) in "".join(spktr)]
        combos.sort(key=lambda l:-sum(map(lambda m:(spktr.index(m)-len(spktr)/2.)**2,l)))
        if combos:
            return (sorted(combos[0],key=lambda l: -el[l]),sum(map(lambda l:el[l],combos[0])))



# Party maximum and minimum votes
vlist = [("N",100,50000),("D",40000,100000),
         ("L",7000,32000),("C",3000,30000),("V",5000,34000),
         ("G",30000,110000),("K",1000,30000)]

uslist = [('D', 90000, 110000),('R', 80000, 120000),('L', 200, 10000),('G', 500, 6000)]


parallel(300,[[fpps]],[(pr,60,1,5)],*vlist)





