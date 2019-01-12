import matplotlib
import matplotlib.pyplot as plt
from SuperElection import *

def plotparl(el, colordict, small=False, inctext=True):
    matplotlib.rcParams['figure.facecolor'] = '1'
    labels = sorted(el.seattotals.keys(),key=lambda l: -el.positions[l][0])
    seats = [el.seattotals[l] for l in labels]
    percents = percentages(el.seattotals)
    percents = [percents[l] for l in labels]
    seats.append(sum(seats))
    explode = (0, 0, 0, 0, 0)
    colors = [colordict[l] for l in labels]
    labels += ['']
    colors += ['1']
    patches, texts, autotexts = plt.pie(seats, labels=labels, autopct='', shadow=False, colors=colors, wedgeprops = {'linewidth': 0}, radius=1-0.75*small)
    for i, t in enumerate(autotexts[:-1]):
        t.set_text(""+ (str(seats[i])+ "\n(%.2f %%)" % percents[i])*inctext)
    autotexts[-1] = ""
    plt.show()

def plotres(res, colordict, order, small=True, inctext=False):
    resel = Election()
    resel.seattotals = res
    resel.positions = {p: (i,0) for i, p in enumerate(order)}
    plotparl(resel, colordict, small, inctext)



def randreposition(lst,repmean=0,repstd=0.1, frommean=True, shunpower=True):
    avgpos = (random.gauss(repmean+meanpos(lst)[0]*int(frommean),repstd), random.gauss(repmean+meanpos(lst)[1]*int(frommean),0.25*repstd))
    for v in lst:
        vpos = [random.gauss(v.position[0]+0.1*avgpos[0]-repstd*shunpower*np.mean([el.positions[el.plurality()[0]][0] for el in v.regs]),repstd),random.gauss(v.position[1]+0.1*avgpos[1]-repstd*shunpower*np.mean([el.positions[el.plurality()[0]][1] for el in v.regs]),repstd)]
        v.pos(*vpos)


def ecyc(rr=True):
    for sub in [e]+e.subelections:
        sub.clearVotes()
    for v in vs:
        v.vote()
    meanpos = (np.mean([v.position[0] for v in vs]),np.mean([v.position[1] for v in vs]))
    for p in e.positions:
        e.positions[p] = tuple([e.positions[p][i]+(meanpos[i]-e.positions[p][i])*flexes[p][i]*random.gauss(1,0.1) for i in [0,1]])
    if rr:
        randreposition(vs)
    for sub in e.subelections:
        sub.positions = e.positions

def group(lst,num):
     gsz = len(lst)//num
     rem = num - gsz
     gl = [lst[i*gsz:(i+1)*gsz] for i in range(num)]
     gl[-1] += lst[-rem:]
     return gl

def vargroup(lst,gs,meansize=1, sizestd=0.3):
    tot = len(lst)
    sizes = [random.gauss(meansize, sizestd) for g in range(gs)]
    sizes = listPR(dict(zip(range(gs),sizes)), tot,"lr").values()
    finlst = []
    totadded = 0
    for s in sizes:
        finlst.append(lst[totadded:totadded+s])
        totadded += s
    return finlst


def varreg(lst, el, *args):
    vg = vargroup(lst,len(el.subelections), *args)
    for i,g in enumerate(vg):
        for v in g:
            v.newreg(el,el.sub(i))
            


def eqreg(lst, el):
    gs = group(lst, len(el.subelections))
    for i,g in enumerate(gs):
        for v in g:
            v.newreg(el,el.sub(i))
            

def newsubs(nsubs,el,vtrs,eq=False):
    el.numSubs(nsubs)
    if eq:
        varreg(vtrs,el, 1, 0)
    else:
        varreg(vtrs,el)
    spreadpos(el)







