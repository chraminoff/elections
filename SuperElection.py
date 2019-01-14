import random
from collections import Counter
from Election import *

class SuperElection(Election) :
    '''This is a type of Election that can contain sub-elections ('subs'/districts),
    where any given electoral system can be applied simultaneously to all sub-elections.
    The seat results of sub-elections can then be aggregated.
    This allows one to simulate real-life elections based on electoral districts.'''

    def __init__(self,name="") :
        Election.__init__(self,name)
        self.subelections = []

    def addSub(self,elec,*args) :
        if "super" in args:
            self.subelections.append(SuperElection(elec))
        else:
            self.subelections.append(Election(elec))
        self.subelections[-1].positions = self.positions
    
    # adds n sub-elections
    def addNumSubs(self,n,*args) :
        for i in range(len(self.subelections),n+len(self.subelections)) :
            if "super" in args:
                self.subelections.append(SuperElection(str(i+1)))
            else:
                self.subelections.append(Election(str(i+1)))
            self.subelections[-1].positions = self.positions

    # replaces the existing sub-elections with n new sub-elections
    def numSubs(self,n,*args):
        self.clearSubs()
        self.addNumSubs(n,*args)

    # distributes a /seats/ number of sub-elections among sub-elections themselves according to parameters given in /args/.
    # This creates "sub-sub-elections" and is useful e.g. for simulating the seat allocation between states 
    # in the U.S. House of Representatives (sub-elections are states, sub-sub-elections are congressional districts).
    def subNumSubs(self,seats,*args):
        '''By default, the sub-subs are distributed according to the Largest Remainder method (with a Hare quota) based on votes in each sub.
        Possible arg options:
        "eq" : Equal (as far as possible) distribution of sub-subs among subs
        "hhdist" : Huntington-Hill distribution (used for the U.S. House of Representatives)'''
        if "eq" in args :
            spsub = {x:seats/len(self.subelections) for x in range(len(self.subelections))}
            for s in range(len(self.subelections)) :
                self.sub(s).numSubs(*([spsub[s]]+list(args)));
        else :
            spsub = {}
            if "hhdist" in args :
                spsub = self.seatsPerSub(seats,"hh")
            else :
                spsub = self.seatsPerSub(seats,"lr")
            for s in range(len(self.subelections)) :
                self.sub(s).numSubs(*([spsub[s]]+list(args)));
        

    def clearSubs(self):
        del self.subelections[:]

    def clearEverything(self):
        super(SuperElection, self).clearEverything()
        clearSubs()

    def sub(self,i):
        return self.subelections[i];

    def randsub(self):
        return random.choice(self.subelections)

    # the combined votes in all sub-elections 
    def getSubVotes(self) :
        subvotetotals = Counter()
        subfirstprefs = Counter()
        for sub in self.subelections :
            subvotetotals += Counter(sub.votetotals)
            subfirstprefs += Counter(sub.firstprefs)
        return (dict(subvotetotals),dict(subfirstprefs))

    # the combined seat results in all sub-elections
    def getSubSeats(self) :
        subseattotals = Counter()
        for sub in self.subelections :
            subseattotals += Counter(sub.seattotals)
        return dict(subseattotals)

    # assigned the combined votes in all sub-elections as the votes for the SuperElection as a whole
    def importSubVotes(self) :
        self.votetotals.clear()
        self.firstprefs.clear()
        subvfp = self.getSubVotes()
        self.votetotals = subvfp[0]
        self.firstprefs = subvfp[1]

    # same as above, but for seats
    def importSubSeats(self) :
        self.seattotals.clear()
        self.seattotals = self.getSubSeats()

    # calculates the seat distribution between sub-elections based on the numbers of votes in them, using the listPR parameters given
    def seatsPerSub(self,seats="t",*args):
        if seats == "t" :
            seats = self.totSeats()
        poppersub = {x: self.sub(x).totVote() for x in range(len(self.subelections))}
        if "names" in args :
            poppersub = {x.name: x.totVote() for x in self.subelections}
        return listPR(poppersub,seats,*args)

    # spreads the votes of the SuperElection among the subelections randomly (in chunks, to speed up the process)
    def randomSpreadVotes(self,minchunk,maxchunk,minsize=-1,maxsize=-1,absorpct="abs") :
        '''Parameters:
        minchunk/maxchunk : minimum/maximum chunks in which votes are assigned to subelections
        minsize/maxsize: minimum/maximum size of subelections, by absolute number of votes if absorpct is set to "abs",
                         or by percentage of all votes if it is set to "pct"
        '''
        for sub in self.subelections :
            sub.clearEverything()
        vpersub = {x: self.totVote()/len(self.subelections) for x in range(len(self.subelections))}
        if not (minsize<0 or maxsize<0 or maxsize<minsize) :
            if absorpct == "pct" :
                vpersub = {x: int(self.totVote()*random.uniform(minsize,maxsize)/100.) for x in range(len(self.subelections))}
            else :
                vpersub = {x: random.randint(minsize,maxsize) for x in range(len(self.subelections))}
            if sum(vpersub.values()) > self.totVote():
                    vpersub = {x: int(self.totVote()*1./sum(vpersub.values())*vpersub[x]) for x in vpersub.keys()}
        nonfullsubs = list(range(len(self.subelections)))
        for v in self.votetotals.keys() :
            remvs = self.votetotals[v];
            while remvs > 0 :
                pick = 0;
                if len(nonfullsubs) > 0 :
                    pick = random.choice(nonfullsubs)
                else :
                    pick = random.randrange(len(self.subelections))
                psub = self.subelections[pick]
                give = 0;
                if len(nonfullsubs) > 0:
                    give = random.randint(min(remvs,minchunk,vpersub[pick]-psub.totVote()),\
                        min(maxchunk,remvs,vpersub[pick]-psub.totVote()))
                else :
                    give = 1
                psub.addVotes(give,*v);
                remvs -= give;
                if  psub.totVote() == vpersub[pick] and len(nonfullsubs)>0:
                    nonfullsubs.remove(pick);

    # repeats the process above for each subelection (that has subelections of its own)
    def subRandomSpreadVotes(self,*args) :
        for s in self.subelections :
            s.randomSpreadVotes(*args)

    # runs runElection in all sub-elections according to the electoral system and parameters specified in args 
    def runSubElections(self,*args) :
        '''Args:
        first argument : electoral system, i.e. the name of the function implementing it, i.e. "FPTP" for first past the post, "IRV" for instant runoff voting etc.
        subsequent arguments: parameters of the electoral system (mainly used for listPR/IRVlistPR), which are passed on to the function implementing the electoral system,
                              as well as the following parameters for seat distribution among subelections:  
                              "eq" : Equal (as far as possible) distribution of sub-subs among subs
                              "hhdist" : Huntington-Hill distribution
        '''
        if "pop" in args :
            spsub = {}
            if "hhdist" in args :
                spsub = self.seatsPerSub([x for x in args if type(x) is int][0],"hh")
            else :
                spsub = self.seatsPerSub([x for x in args if type(x) is int][0],"lr")
            for s in range(len(self.subelections)) :
                self.sub(s).runElection(*(list(args)+[spsub[s]]));
        elif "eq" in args :
            seats = [x for x in args if type(x) is int][0]
            spsub = {x:seats/len(self.subelections) for x in range(len(self.subelections))}
            for s in range(len(self.subelections)) :
                self.sub(s).runElection(*(list(args)+[spsub[s]]));
        else:
            for sub in self.subelections :
                sub.runElection(*args);

    # Simulates a multi-district general election (given that the votes have been added), takes the same arguments as runSubElections, plus "fins" and "stot" as options
    def runGenElection(self,*args) :
        '''Function-specific args:
        "fins": print a string of the combined results of the SuperElection
        "stot": return a per-party seat count dictionary'''
        self.runSubElections(*args)
        self.importSubSeats()
        if "fins" in args :
            print(valsorted(self.firstprefs))
            print(valsorted({x[0]: round(x[1],2) for x in self.percentages().items()}))
            print("")
            print(valsorted(self.seattotals))
            print(valsorted({x[0]: round(x[1],2) for x in percentages(self.seattotals).items()}))
        if "stot" in args :
            return self.seattotals
