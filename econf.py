import parliament
import westminster

from SuperElection import *

# AN EXPERIMENTAL MULTI-ELECTION SIMULATOR

# The aim is to simulate a multi-party system over multiple elections
# Key assumptions: 
# - voters vote for the party closest to them politically (on a left-right/authoritarian-libertarian map)
# - governing parties and coalitions tend to lose support
# - parties seek to maximise their vote share, and change their positions if necessary


# Example usage:
# elcyc(100, "borda", "fins") 
# elcyc(650, "FPTP", "wm", "fins") # UK general elections
# elcyc(225, "FPTP", "fins", al=("listPR",225,"lr"), pres=(1,"TRS","s")) # Russian duma (w/o 5% threshold) and presidential elections
# elcyc(577, "TRS", "fins", pres=(1,"TRS", "s")) # French legislative and presidential elections
# elcyc(19, "IRVlistPR", 19, 2, "fins") # Proportional representation with the Sainte-Lague method in 19 19-seat districts

# Initialisation
e = SuperElection("Election")
vs = [Voter([e]) for i in range(int(700000*random.gauss(1,0.2)))] # randomly sized list of voters
ncenter = random.random()
nspread = 0.5
n = lambda: random.gauss(ncenter,nspread)

# voters distributed according to their position on the right-left axis, 
# enabling somewhat realistic modeling of electoral districts
vs.sort(key=lambda l: l.position[0]*n()*random.gauss(1,nspread))

# some plausible parties and political positions in a multi-party democracy
e.addPositions((u"Cyan",0.5,0.1),(u"Pink",-0.6,-0.2),(u"Orange",0.2,-1),(u"Yellow",1.2,-0.4),(u"Black",0,0),(u"Navy",0.1,1.3),(u"Green",-0.7,-1.6),(u"Crimson",-2,-0.1),(u"Maroon",-1.8,1),(u"Brown",-0.2,2.5))

# Configure and run an election,
# parameters: number of districts (subelections), followed by runGenElection parameters for the electoral system
def econf(nsub=50, *args, **kwargs):
    
    global vs
    global e
    for s in e.subelections+[e]:
        s.clearVotes()

    e.numSubs(nsub)
    for i in range(len(vs)):
        vs[i].newreg(e,e.sub(int(i*1.*nsub/len(vs))))

    for v in vs:
        v.vote()
    
    if args:
        e.runGenElection(*args, **kwargs)
    else:
        e.runGenElection("IRVlistPR",13,"fins")
    
    return e
    
# reposition the voters politically, given the most likely government formed    
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
    
        
# reposition parties in a vote-seeking manner
def partyrepos(el,vtrlist):
    for p, ppos in el.positions.items():
        el.positions[p] = (random.gauss(ppos[0],0.05),random.gauss(ppos[1],0.05))
        if poll(vtrlist,el.positions,1000)[p] < Counter(percentages(el.firstprefs))[p]:
            el.positions[p] = ppos
            
# most likely coalition given the existing election result
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

# reposition parties and voters, configure and hold a new election and display the result as a diagram
def necdis(etype="parl",*args,**kwargs):            
    global vs, e, prevresult
    if e.seattotals :
        partyrepos(e,vs)
        newpos(vs,e)
    e = econf(*args,**kwargs)
    print(str(sorted({p:Counter(e.seattotals)[p]-prevresult[etype][p] for p in set(e.seattotals)|set(prevresult[etype])}.items(), key= lambda l: -Counter(e.seattotals)[l[0]])).replace("', ","', +").replace("+-","-"))
    if sum(e.seattotals.values()) == 1 and sum(prevresult[etype].values()) in (0,1):
        if prevresult[etype] == e.seattotals:
            print(list(e.seattotals.keys())[0] + " hold")
        elif not prevresult[etype]:
            print(list(e.seattotals.keys())[0] + " win")
        else:
            print(list(e.seattotals.keys())[0] + " gain from " + list(prevresult[etype].keys())[0])
    prevresult[etype] = Counter(e.seattotals)
    if "wm" in args: # westminster-style parliament diagram
        gov = mlcoal(e)[0]
        plist = [",".join([gov[0],"1",'head',plegend[gov[0]]])] # speaker from largest gov party
        for p, sts in valsorted(e.seattotals):
            if p in gov:
                plist.append(",".join([p,str(sts-(p==gov[0])),'right',plegend[p]]))
            else:
                plist.append(",".join([p,str(sts),'left',plegend[p]]))
        westminster.wmdiagram(";".join(plist))
    else: # hemicycle parliament diagram, default
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
        necdis("parl",*args,**kwargs)
        return mlcoal(e)

      
plegend = {'Black':'black','Navy':'navy','Orange':'orange','Pink':'pink','Green':'green','Cyan':'cyan','Yellow':'yellow','Brown':'brown','Maroon':'maroon','Crimson':'crimson', 'Blue':'blue','Purple':'purple','Red':'red'}

# Political positions designed to create a two-party system
twoppos = {"Cyan":(1,0.2),"Pink":(-1,-0.2),"Orange":(0.1,-3),"Yellow":(10,-2),"Navy":(0.1,6),"Green":(-3,-9),"Crimson":(-10,-1),"Maroon":(-9,3),"Brown":(-0.3,11)}

# Political positions based on the 4 squares of the political compass
polcpos = {"Red":(-2,2),"Green":(-2,-2),"Purple":(2,-2),"Blue":(2,2)}

# Simulates the governing party/parties trying to choose an electoral system that maximises their electoral fortunes.
# Also assumes that economically left-leaning and right-leaning parties will tend to try increase and decrease the number
# of seats, respectively. Only single-member districts are allowed. Since this is likely to produce large majorities, any 
# changes to the electoral system require a 5/6 majority. 
def govdecision(election, system):
    mc, govseats = mlcoal(election)
    avgeconpos = sum([e.positions[p][0]*e.firstprefs[p] for p in e.positions])*1./sum(e.firstprefs.values())
    goveconpos = sum([e.positions[p][0] for p in mc])*1./len(mc)
    newseats = sum(election.seattotals.values())
    newsystem = system
    currsysres = election.seattotals
    if govseats >= 5*(sum(currsysres.values())-govseats):
        if goveconpos > avgeconpos+5:
            newseats=19
        elif goveconpos > avgeconpos+.5:
            newseats=61
        elif goveconpos < avgeconpos-5:
            newseats=659
        elif goveconpos < avgeconpos-.5:
            newseats=361
        sysoptions = [sys for sys in ["FPTP","TRS","IRV","borda","RP"] if not sys == system]

        for elsys in sysoptions:
            sysres = Counter([getattr(s,elsys)()[0] for s in election.subelections])
            if all([sysres[gp] > currsysres[gp] for gp in mc]):
                newsystem = elsys
                currsysres = sysres
    return newseats, newsystem

# Runs elcycs forever, given a starting single-member electoral system (string)
# Governments try to change the system to favor themselves if they can.
def elcyc8(system):
    sys = system
    while 1:
        seats, sys = govdecision(e, sys)
        print("Seats: %d, Electoral system: %s"%(seats,sys))
        print(elcyc(seats,sys,"fins"))
