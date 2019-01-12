import random
from collections import Counter
from Election import *

class SuperElection(Election) :
    def __init__(self,name="") :
        Election.__init__(self,name)
        self.subelections = []
    def addSub(self,elec,*args) :
        if "super" in args:
            self.subelections.append(SuperElection(elec))
        else:
            self.subelections.append(Election(elec))
        self.subelections[-1].positions = self.positions
        
    def addNumSubs(self,n,*args) :
        for i in range(len(self.subelections),n+len(self.subelections)) :
            if "super" in args:
                self.subelections.append(SuperElection(str(i+1)))
            else:
                self.subelections.append(Election(str(i+1)))
            self.subelections[-1].positions = self.positions

    def numSubs(self,n,*args):
        self.clearSubs()
        self.addNumSubs(n,*args)

    def subNumSubs(self,seats,*args):
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

    def getSubVotes(self) :
        subvotetotals = Counter()
        subfirstprefs = Counter()
        for sub in self.subelections :
            subvotetotals += Counter(sub.votetotals)
            subfirstprefs += Counter(sub.firstprefs)
        return (dict(subvotetotals),dict(subfirstprefs))
    def getSubSeats(self) :
        subseattotals = Counter()
        for sub in self.subelections :
            subseattotals += Counter(sub.seattotals)
        return dict(subseattotals)
    def importSubVotes(self) :
        self.votetotals.clear()
        self.firstprefs.clear()
        subvfp = self.getSubVotes()
        self.votetotals = subvfp[0]
        self.firstprefs = subvfp[1]
    def importSubSeats(self) :
        self.seattotals.clear()
        self.seattotals = self.getSubSeats()
    def seatsPerSub(self,seats="t",*args):
        if seats == "t" :
            seats = self.totSeats()
        poppersub = {x: self.sub(x).totVote() for x in range(len(self.subelections))}
        if "names" in args :
            poppersub = {x.name: x.totVote() for x in self.subelections}
        return listPR(poppersub,seats,*args)
    def randomSpreadVotes(self,minchunk,maxchunk,minsize=-1,maxsize=-1,absorpct="abs") :
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

    def subRandomSpreadVotes(self,*args) :
        for s in self.subelections :
            s.randomSpreadVotes(*args)

    def runSubElections(self,*args) :
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

    def runGenElection(self,*args) :
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
