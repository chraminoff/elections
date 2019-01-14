import parliament

from SuperElection import *

# THIS FILE CONTAINS AN EXPERIMENTAL MULTI-ELECTION SIMULATOR

# Example usage:
# elcyc(100, "borda", "fins") 
# elcyc(650, "FPTP", "fins") # UK general elections
# elcyc(577, "TRS", "fins", pres=(1,"TRS", "s")) # French legislative and presidential elections
# elcyc(19, "IRVlistPR", 19, 2, "fins") # Proportional representation with the Sainte-Lague method in 19 19-seat districts


e = SuperElection("Parliamentary election")
vs = [Voter([e]) for i in range(int(700000*random.gauss(1,0.2)))]
ncenter = random.random()
nspread = 0.5
n = lambda: random.gauss(ncenter,nspread)

vs.sort(key=lambda l: l.position[0]*n()*random.gauss(1,nspread))

# parties and political positions commonly seen in multi-party democracies
e.addPositions((u"Conservative",0.5,0.1),(u"Labour",-0.6,-0.2),(u"Liberal",0.2,-1),(u"Libertarian",1.2,-0.4),(u"Centrist",0,0),(u"Nationalist",0.1,1.3),(u"Green",-0.7,-1.6),(u"Communist",-2,-0.1),(u"Revolutionary Socialist",-1.8,1),(u"National Socialist",-0.2,2.5))

# Configure and run an election,
# parameters: number of districts (subelections), followed by runGenElection parameters for the electoral system
def econf(nsub=50, *args):
    global vs
    global e
    for s in e.subelections+[e]:
        s.clearVotes()

    if nsub != len(e.subelections):
        e.numSubs(nsub)
        for i in range(len(vs)):
            vs[i].newreg(e,e.sub(int(i*1.*nsub/len(vs))))

    
    for v in vs:
        v.vote()
    
    if args:
        e.runGenElection(*args)
    else:
        e.runGenElection("IRVlistPR",13,"fins")
    
    return e
    
    
def newpos(vtrlist, el=None):
    if el:
        rulingpos = [el.positions[p] for p in mlcoal(el)[0]]
        rulingpos = tuple(map(lambda l: sum(l)*1./len(rulingpos),zip(*rulingpos)))
        allpos = list(zip(*[vtr.position for vtr in vtrlist]))
        meanpos = (sum(allpos[0])*1./len(vtrlist), sum(allpos[1])*1./len(vtrlist))
    else:
        rulingpos = None
    meanshift = (random.gauss(0,0.1),random.gauss(0,0.05))
    for vtr in vtrlist:
        if rulingpos:
            vtr.pos(random.gauss(vtr.position[0]+meanshift[0]
                    -0.1*(rulingpos[0]-vtr.position[0])
                    +0.05*(meanpos[0]+meanshift[0]-vtr.position[0])
                    +0.05*(0.0-vtr.position[0]),0.1),
                    random.gauss(vtr.position[1]+meanshift[1]
                    -0.1*(rulingpos[1]-vtr.position[1])
                    +0.05*(meanpos[1]+meanshift[1]-vtr.position[1])
                    +0.05*(0.0-vtr.position[1]), 0.05))
        else:
            vtr.pos(random.gauss(vtr.position[0]+meanshift[0],0.1), random.gauss(vtr.position[1]+meanshift[1], 0.05))

def poll(vtrlist,poses,samplesize=500,*args):
    testel = Election()
    testel.positions = {x : y for x,y in poses.items()}
    sample = random.sample(vtrlist,samplesize)
    for vtr in sample:
        vtr.reg(testel)
        vtr.vote(-1)
        vtr.dereg(testel)
    if "s" in args:
        print(valsorted(percentages(testel.firstprefs,2)))
    if "el" in args:
        return testel
    else:
        return Counter(percentages(testel.firstprefs))
    
        

def partyrepos(el,vtrlist):
    for p, ppos in el.positions.items():
        el.positions[p] = (random.gauss(ppos[0],0.05),random.gauss(ppos[1],0.05))
        if poll(vtrlist,el.positions,1000)[p] < Counter(percentages(el.firstprefs))[p]:
            el.positions[p] = ppos
            
# most likely coalition in existing parliament
def mlcoal(el):
    plur = max(el.seattotals.keys(),key=lambda l: el.seattotals[l])
    if el.seattotals[plur] > sum(el.seattotals.values())/2.:
        return [plur], el.seattotals[plur]
    currbest = []
    for nparties in range(len(el.seattotals.keys())+1):
        options = list(filter(lambda l: sum(map(lambda m: el.seattotals[m],l)) > sum(el.seattotals.values())/2.,list(itertools.combinations(el.seattotals.keys(),nparties))))    
        if options:
            currbest = [min(currbest+options,key=lambda coal: max(map(lambda p: ((el.positions[p[0]][0]-el.positions[p[1]][0])**2+(el.positions[p[0]][1]-el.positions[p[1]][1])**2)**.5,list(itertools.combinations(coal,2)))))]
    return sorted(currbest[0], key=lambda l: -el.seattotals[l]), sum(map(lambda l: el.seattotals[l],currbest[0]))

prevresult = {"parl":Counter(),"sen":Counter(),"pres":Counter()}

def necdis(etype="parl",*args):            
    global vs, e, prevresult
    if e.seattotals :
        partyrepos(e,vs)
        newpos(vs,e)
    e = econf(*args)
    print(str(sorted({p:Counter(e.seattotals)[p]-prevresult[etype][p] for p in set(e.seattotals)|set(prevresult[etype])}.items(), key= lambda l: -Counter(e.seattotals)[l[0]])).replace("', ","', +").replace("+-","-"))
    if etype == "pres" and sum(e.seattotals.values()) == 1:
        if prevresult[etype] == e.seattotals:
            print(list(e.seattotals.keys())[0] + " hold")
        elif not prevresult[etype]:
            print(list(e.seattotals.keys())[0] + " win")
        else:
            print(list(e.seattotals.keys())[0] + " gain from " + list(prevresult[etype].keys())[0])
    prevresult[etype] = Counter(e.seattotals)
    parliament.display(parliament.render_svg(parliament.to_partyspec(e.seattotals,plegend,sorted(e.seattotals.keys(),key=lambda l:e.positions[l][0]))))
    
nelcyc = 0    

# run an entire electoral cycle, with possible separate presidential and upper house (senate) elections 
def elcyc(*args,**kwargs):             
    global nelcyc
    nelcyc += 1 
    if nelcyc % 3 == 0 and "pres" in kwargs:
         necdis("pres",*kwargs["pres"])
    elif nelcyc % 3 == 2 and "sen" in kwargs:
        necdis("sen",*kwargs["sen"])
        return mlcoal(e)
    else:
        necdis("parl",*args)
        return mlcoal(e)

      
plegend = {'Centrist':'black','Nationalist':'darkblue','Liberal':'orange','Labour':'red','Green':'green',u'Conservative':'blue','Libertarian':'yellow','National Socialist':'brown',u'Revolutionary Socialist':'purple','Communist':'darkred'}

twoppos = {u"Conservative":(1,0.2),u"Labour":(-1,-0.2),u"Liberal":(0.1,-3),u"Libertarian":(10,-2),u"Nationalist":(0.1,6),u"Green":(-3,-9),u"Communist":(-10,-1),u"Revolutionary Socialist":(-9,3),u"National Socialist":(-0.3,11)}

