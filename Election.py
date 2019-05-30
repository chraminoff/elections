import random
from collections import Counter
import numbers
import math
import itertools

class Election():
    """Simulates a single-district election, with a number of possible different electoral systems.
    Votes cast are treated as party votes.
    
    Attributes:
        name : Name string of the election
        votetotals: number of votes cast with each preference sequence
        firstprefs: number of votes cast by first preference only
        seattotals: number of seats by party/alternative
        positions: political compass (economic, social) positions of parties (used for multi-election simulations)
    """
    def __init__(self, name=""):
        self.name = name
        self.votetotals = Counter()
        self.firstprefs = Counter()
        self.seattotals = Counter()
        self.positions = {}

    def addVote(self,*vote) :
        if vote:
            self.votetotals[vote] += 1
            self.firstprefs[vote[0]] += 1

    def addVotes(self,n,*vote) :
        if vote:
            self.votetotals[vote] += n
            self.firstprefs[vote[0]] += n

    def addPos(self,cand,econ=random.gauss(0,0.5),soc=random.gauss(0,1)):
        self.positions[cand] = (econ,soc)

    def addPositions(self,*args):
        for p in args:
            self.addPos(*p)

    def clearVotes(self):
        self.votetotals.clear()
        self.firstprefs.clear()

    def clearSeats(self):
        self.seattotals.clear()

    def clearEverything(self) :
        self.votetotals.clear()
        self.firstprefs.clear()
        self.seattotals.clear()
        self.positions.clear()

    # tot = total
    def totVote(self):
        return sum(self.votetotals.values())

    def totSeats(self):
        return sum(self.seattotals.values())

    # returns the candidate with the most votes in the /stat/ count (first preference votes by default). ties are resolved randomly.
    # return format: winner's (name, votes, margin of victory, number of winners)
    def plurality(self,stat="firstprefs") :
        if stat == "firstprefs" :
            stat = self.firstprefs
        sortedvotes = sorted(stat.items(), key=lambda r: r[1],reverse=True)
        nofwinners = 0
        for v in sortedvotes:
            if v[1] >= sortedvotes[0][1] :
                nofwinners += 1
            else:
                break
        if nofwinners > 1 :
            print("Because of a tie, the winner has been chosen randomly.")
            winner = random.choice(sortedvotes[0:nofwinners])[0]
        else:
            winner = sortedvotes[0][0]
        nextbestvote = 0
        if len(sortedvotes) > 1:
            nextbestvote = sortedvotes[1][1]
        return (winner,sortedvotes[0][1],sortedvotes[0][1]-nextbestvote,nofwinners==1)

    def percentages(self,stat="firstprefs",rounding=-1) :
        if stat == "firstprefs" :
            stat = self.firstprefs
        totvotes = sum(stat.values())
        if not rounding==-1 :
            return {n: round(stat[n]*100./totvotes,rounding) for n in stat.keys()}
        else:
            return {n: stat[n]*100./totvotes for n in stat.keys()}

    # result of a one-to-one match between candidate/parties a and b
    def preference(self,a,b,*args):
        tot = {a:0,b:0}
        for vt in self.votetotals.keys():
            i = 0
            while vt[i] not in [a,b]:
                i += 1
                if i >= len(vt):
                    break
            if i < len(vt):
                tot[vt[i]] += self.votetotals[vt]
        if "s" in args :
            tots = [x[0] for x in valsorted(tot)]
            pcts = percentages(tot)
            print("")
            print("%s :\t%d\t(%.2f pct)" % (tots[0],tot[tots[0]],pcts[tots[0]]))
            print("%s :\t%d\t(%.2f pct)" % (tots[1], tot[tots[1]], pcts[tots[1]]))
        return self.plurality(tot)

    # set of all candidates (aka alternatives or parties) for which any vote has been given at any preference
    def allCands(self):
        allcands = set()
        for vt in self.votetotals.keys() :
            for v in vt :
                allcands.add(v)
        return list(allcands)

    # [BEGIN] Single-winner electoral systems
    
    # All functions (electoral systems) in this section have the following return format:
    # winner's (name, votes, margin of victory, number of winners)

    # At least the following arg options apply to each function:
    #   "s": print details of the result
    #   "stot": return the winner's name string only

    # First Past the Post
    def FPTP(self,*args) :
        if "s" in args:
            print("An election in the %s constituency\nhas been conducted under First Past The Post."%self.name)
        sortedvotes = sorted(self.firstprefs.items(), key=lambda r: r[1],reverse=True)
        pcts = self.percentages()
        winner = self.plurality()
        if "s" in args:
            print("The votes were cast as follows:")
            for v in sortedvotes :
                print("\n%s :\t%d\t(%.2f pct)" % (v[0],v[1],pcts[v[0]]))
            print("\n")
            print("\n%s is elected by a margin of %d votes." % (winner[0],winner[2]))
        if "stot" in args :
            return {winner[0]:1}
        return winner

    # Two-Round System (more precisely the contingency vote)
    def TRS(self,*args) :
        finnum = 2
        if len(args) > 0 :
            if type(args[0]) is int :
                finnum = args[0]
        sortedvotes = sorted(self.firstprefs.items(), key=lambda r: r[1],reverse=True)
        pcts = self.percentages()
        if "s" in args :
            print("An election in the %s constituency\nhas been conducted under the Two-Round System."%self.name)
            print("The first round results are as follows:")
            for v in sortedvotes :
                print("\n%s :\t%d\t(%.2f pct)" % (v[0],v[1],pcts[v[0]]))
            print("\n")

        if pcts[sortedvotes[0][0]] > 50 :
            fstrndwinner = self.plurality()
            if "s" in args :
                print("%s has obtained a majority in the first round,\
                \nand is thus elected outright, with a margin of %d votes."\
                 % (fstrndwinner[0],fstrndwinner[2]))
            if "stot" in args:
                return {fstrndwinner[0]: 1}
            return fstrndwinner

        finalists = []
        nofpotwinners = 0
        for v in sortedvotes:
            if v[1] == sortedvotes[finnum-1][1] :
                nofpotwinners += 1
            elif v[1] > sortedvotes[finnum-1][1] :
                finalists.append(v[0])
            else:
                break
        fincands = nofpotwinners + len(finalists)

        if fincands > finnum :
            findices = random.sample(range(len(finalists),fincands),nofpotwinners)
            for n in range(finnum-len(finalists)) :
                finalists.append(sortedvotes[0:fincands][findices[n]][0])
        else :
            finalists = [x[0] for x in sortedvotes[0:finnum]]

        if "s" in args :
            print(finalists[0]),
            for f in finalists[1:-1] :
                print(", %s"%f),
            print("and"),
            print(finalists[-1]),
            print("advance to the second round.")
        finvotes = {f: 0 for f in finalists}
        for vt in self.votetotals.keys() :
            i=0
            while vt[i] not in finalists :
                i += 1
                if i >= len(vt) :
                    break
            if i < len(vt) :
                finvotes[vt[i]] += self.votetotals[vt]
        finalwinner = self.plurality(finvotes)
        if "s" in args :
            finpcts = self.percentages(finvotes)
            sortedfinvotes = sorted(finvotes.items(), key=lambda r: r[1],reverse=True)
            print("\nThe second round results are as follows:")
            for v in sortedfinvotes :
                print("\n%s :\t%d\t(%.2f pct)" % (v[0],v[1],finpcts[v[0]]))
            print("\n%s is elected by a margin of %d votes." % (finalwinner[0],finalwinner[2]))

        if "stot" in args :
            return {finalwinner[0]:1}
        return finalwinner

    # Instant Runoff Voting
    def IRV(self,*args) :
        cands = self.firstprefs.keys()
        eliminated = []
        count = 1
        sortedvotes = sorted(self.firstprefs.items(), key=lambda r: r[1],reverse=True)
        pcts = self.percentages()
        if "s" in args :
            print("An election is conducted in the %s constituency under Instant Runoff Voting."%self.name)
            print("The first preferences are as follows:")
            for v in sortedvotes :
                print("\n%s :\t%d\t(%.2f pct)" % (v[0],v[1],pcts[v[0]]))
            print("\n")

        while len(sortedvotes) > 0 :
            if pcts[sortedvotes[0][0]] > 50 :
                if "s" in args :
                    print("%s has been elected at count %d."%(sortedvotes[0][0],count))
                irvplur = self.plurality(dict(sortedvotes))
                if "stot" in args:
                    return {irvplur[0]: 1}
                return irvplur
            if not sortedvotes[-1][1]==sortedvotes[-2][1]:
                eliminated.append(sortedvotes[-1][0])
                del sortedvotes[-1]
            else :
                eliminable = len([x for x in sortedvotes if x[1]==sortedvotes[-1][1]])
                eliminee = random.randint(1,eliminable)
                eliminated.append(sortedvotes[-eliminee][0])
                del sortedvotes[-eliminee]
            if "s" in args :
                print("%s is eliminated at count %d."%(eliminated[-1],count))
            count += 1
            stagevotes = {v[0]: 0 for v in sortedvotes}
            for vt in self.votetotals.keys() :
                i=0
                while vt[i] in eliminated or vt[i] not in cands:
                    i += 1
                    if i >= len(vt) :
                        break
                if i < len(vt) :
                    stagevotes[vt[i]] += self.votetotals[vt]
            del sortedvotes
            del pcts
            sortedvotes = sorted(stagevotes.items(), key=lambda r: r[1],reverse=True)
            pcts = self.percentages(stagevotes)

            if "s" in args :
                print("The vote totals at count %d are as follows:"%count)
                for v in sortedvotes :
                    print("\n%s :\t%d\t(%.2f pct)" % (v[0],v[1],pcts[v[0]]))
                print("\n")

    # The borda count
    def borda(self,*args):
        '''Function-specific arg options:
        "frac": use the Dowdall borda count, which is used in Nauru. The original formula is used by default.
        "stat": return a Counter of the borda point counts of all parties/candidates/alternatives, which can be used e.g. for seat allocation.
        '''
        if "s" in args:
            print("An election in the %s constituency\nhas been conducted under the Borda Count." % self.name)
        maxi = len(max(self.votetotals.keys(),key=lambda l:len(l)))-1
        bcount = Counter()
        if "frac" in args :
            for vt in self.votetotals.keys():
                i = 0
                while i < len(vt):
                    bcount[vt[i]] += self.votetotals[vt]/(i+1.)
                    i += 1
        else :
            for vt in self.votetotals.keys():
                i = 0
                while i < len(vt):
                    bcount[vt[i]] += self.votetotals[vt] * (maxi - i)
                    i += 1
        bordaplur = self.plurality(bcount)
        if "s" in args:
            sortedborda = valsorted(bcount)
            pcts = percentages(bcount)
            print("Based on the votes, the Borda points are as follows:")
            for v in sortedborda :
                print("\n%s :\t%.4f\t(%.2f pct)" % (v[0],v[1],pcts[v[0]]))
            print("\n")
            print("\n%s is elected by a margin of %.4f points." % (bordaplur[0],bordaplur[2]))
        if "stot" in args :
            return {bordaplur[0]:1}
        elif "stat" in args :
            return bcount
        return bordaplur

    # Ranked Pairs (a Condorcet method)
    def RP(self,*args):
        '''Function-specific arg options:
        "paths": print the preference path (graph) formed at each one-to-one match
        "rank": return a list of alternatives in the order of their final RP ranking 
        '''
        if "s" in args:
            print("An election in the %s constituency\nhas been conducted under the Ranked Pairs system." % self.name)
            print("The pair preferences, sorted by the votes of the winner, are as follows:")
        pairs = itertools.combinations(self.allCands(),2)
        rpairs = {}
        for p in pairs:
            ppref = self.preference(*p)
            rpairs[(ppref[0],p[p.index(ppref[0])-1])] = ppref[1]
        rpairskeys = [x[0] for x in valsorted(rpairs)]
        paths = []
        finranking = []
        for rp in rpairskeys:
            if "s" in args:
                self.preference(rp[0],rp[1],"s")
            tpaths = paths[:]
            cycle = False
            for tp in tpaths :
                if tp[0] == rp[1] and tp[-1] == rp[0] :
                    cycle = True
                    break
                if tp[0] == rp[1] :
                    tpaths.append([rp[0]]+tp)
                if tp[-1] == rp[0] :
                    tpaths.append(tp+[rp[1]])
            if not cycle :
                tpaths.append(list(rp))
                paths = tpaths[:]
                if rp[0] in finranking and rp[1] in finranking:
                    wrank = finranking.index(rp[0])
                    lrank = finranking.index(rp[1])
                    if wrank > lrank :
                        finranking.remove(rp[0])
                        finranking.insert(lrank,rp[0])
                elif rp[0] in finranking:
                    finranking.insert(finranking.index(rp[0])+1,rp[1])
                elif rp[1] in finranking:
                    finranking.insert(finranking.index(rp[1]),rp[0])
                else :
                    finranking += rp[:]
                if "paths" in args :
                    print(paths)
                if "s" in args :
                    print(finranking[0]),
                    for r in finranking[1:]:
                        print("> %s" % r),
                    print("")
            elif "s" in args:
                print("The pair is not locked in due to the cycle that would be created.")
        
        if "s" in args:
            print("\nThe final ranking is %s"%finranking[0]),
            for r in finranking[1:] :
                print("> %s"%r),
            print("")
        if "stot" in args:
            return {finranking[0]:1}
        elif "rank" in args:
            return finranking
        else :
            return self.preference(finranking[0],finranking[1])


    # [END] Single-winner electoral systems
    
    # Multi-winner seat distribution between alternatives (parties) under Party-list Proportional representation
    def listPR(self,seats,*args):
        '''Arg options:
        Seat allocation method to be used:
        
            "lr": largest remainder method with a Hare quota
            "lrd": largest remainder method with a Droop quota
            "hh": Huntington-Hill method
        
        If none of the above is used, a highest averages method is used,
        and the first numeric argument is used as the interval between divisors for consecutive numbers of seats:
            1 for the D'Hondt method (default, also used if no numeric argument is given in args)
            2 for the Sante-Lague method
            0.5 for Imperiali
            0 for Plurality Block Voting (winner takes all)

        The smaller this interval is, the less proportional the result.

        '''
        prseats = {x: 0 for x in self.firstprefs.keys()}
        filledseats = 0
        if "lr" in args or "lrd" in args:
            quota = self.totVote()*1./seats
            if "lrd" in args:
                quota = self.totVote()/(seats+1.)
            seatcredit = {x[0]:x[1]/quota for x in self.firstprefs.items()}
            prseats = {x[0]:int(x[1]) for x in seatcredit.items()}
            seatcredit = dict(Counter(seatcredit)-Counter(prseats))
            remseats = sorted(seatcredit.items(), key=lambda l:l[1], reverse=True)[0:seats-sum(prseats.values())]
            for x in remseats :
                prseats[x[0]] += 1
        elif "hh" in args:
            prseats = {x: 1 for x in self.firstprefs.keys()}
            filledseats = len(self.firstprefs)
            runningvotes = dict(self.firstprefs.items())
            while filledseats < seats :
                pick = max(runningvotes.items(),key=lambda l:l[1])[0]
                runningvotes[pick] = runningvotes[pick]*math.sqrt(prseats[pick]*(prseats[pick]+1))/\
                                     math.sqrt((prseats[pick]+1)*(prseats[pick]+2))
                prseats[pick] += 1
                filledseats += 1
        else:
            divinterval = 1
            if len(args) > 0:
                numargs = [x for x in list(args) if isinstance(x, numbers.Number)]
                if len(numargs)>0:
                    divinterval = numargs[0]
            runningvotes = dict(self.firstprefs.items())
            while filledseats < seats :
                pick = max(runningvotes.items(),key=lambda l:l[1])[0]
                runningvotes[pick] = runningvotes[pick]*(1.+divinterval*prseats[pick])/(1.+divinterval*(prseats[pick]+1))
                prseats[pick] += 1
                filledseats += 1
        if "s" in args :
            vpcts = percentages(self.firstprefs)
            spcts = percentages(prseats)
            print("A list PR election is conducted for %d seats in the %s constituency."%(seats,self.name))
            print("The votes and the corresponding seats are as follows:")
            print("List  \tVotes\t(pct)\tSeats\t(pct)")
            sortvs = sorted(prseats.keys(),key=lambda l:self.firstprefs[l],reverse=True)
            for v in sortvs :
                print("\n%s :\t%d\t(%.2f)\t%d\t(%.2f)" % (v,self.firstprefs[v],vpcts[v],prseats[v],spcts[v]))
            print("\n")
        return prseats

    # An Instant-Runoff Variant of the listPR function above. 
    
    # Here, if any party gets 0 seats, it is eliminated from the count, its votes are
    # redistributed to next-preference choices, and the seats are reallocated according to the new vote totals.
    # This process is repeated until all remaining parties are represented.

    # This system is not currently used anywhere in the world (as far as the author is aware), 
    # the Single Transferable Vote being the closest real-life approximation. 
    def IRVlistPR(self,seats,*args):
        runningvotes = dict(self.firstprefs.items())
        irvprseats = listPR(runningvotes,seats,*[x for x in args if not x=="s"])
        stage = 1
        if "s" in args :
            vpcts = percentages(runningvotes)
            spcts = percentages(irvprseats)
            print("An IRV list PR election is conducted for %d seats in the %s constituency."%(seats,self.name))
            print("The votes and the corresponding seats at stage %d are as follows:"%stage)
            print("List  \tVotes\t(pct)\tSeats\t(pct)")
            sortvs = sorted(runningvotes.keys(),key=lambda l:runningvotes[l],reverse=True)
            for v in sortvs :
                print("\n%s :\t%d\t(%.2f)\t%d\t(%.2f)" % (v,runningvotes[v],vpcts[v],irvprseats[v],spcts[v]))
            print("\n")
            if 0 not in irvprseats.values() :
                    print("\nAll voters are represented at the final stage (%d)"%stage)
        while 0 in irvprseats.values():
            sv = valsorted(runningvotes)
            eliminee = 1
            if not sv[-1][1]==sv[-2][1]:
                irvprseats.pop(sv[-1][0])
            else :
                eliminable = len([x for x in sv if x[1]==sv[-1][1]])
                eliminee = random.randint(1,eliminable)
                irvprseats.pop(sv[-eliminee][0])
            if "s" in args :
                print("%s is eliminated at stage %d."%(sv[-eliminee][0],stage))
            stage += 1
            cands = irvprseats.keys()
            runningvotes = {x:0 for x in cands}
            for vt in self.votetotals.keys() :
                i=0
                while vt[i] not in cands:
                    i += 1
                    if i >= len(vt) :
                        break
                if i < len(vt) :
                    runningvotes[vt[i]] += self.votetotals[vt]
            irvprseats = listPR(runningvotes,seats,*[x for x in args if not x=="s"])
            if "s" in args:
                vpcts = percentages(runningvotes)
                spcts = percentages(irvprseats)
                print("\nThe votes and the corresponding seats at stage %d are as follows:"%stage)
                print("List  \tVotes\t(pct)\tSeats\t(pct)")
                sortvs = sorted(runningvotes.keys(),key=lambda l:runningvotes[l],reverse=True)
                for v in sortvs :
                    print("\n%s :\t%d\t(%.2f)\t%d\t(%.2f)" % (v,runningvotes[v],vpcts[v],irvprseats[v],spcts[v]))
                print("\n")
                if 0 not in irvprseats.values() :
                    print("\nAll voters are represented at the final stage (%d)"%stage)
        return irvprseats

    # Assigns the seat results under a specified electoral system as the seat total of the election
    def runElection(self,*args,**kwargs) :
        '''args:
        first argument : electoral system, i.e. the name of the function implementing it, i.e. "FPTP" for first past the post, "IRV" for instant runoff voting etc.
        subsequent arguments: parameters of the electoral system (mainly used for listPR/IRVlistPR), which are passed on to the function implementing the electoral system
        '''
        if "supp" not in kwargs:
            self.seattotals.clear()
        
        if "mstr" in args :
            print(valsorted(self.firstprefs))
            print(valsorted({x[0]: round(x[1],2) for x in self.percentages().items()}))
            print("")
            print(valsorted(self.seattotals))
            print(valsorted({x[0]: round(x[1],2) for x in percentages(self.seattotals).items()}))
            print("")

        if args[0] == "listPR" :
            if "pop" in args or "eq" in args:
                self.seattotals += self.listPR(*([args[-1]]+list(args)[2:-1])) # when arguments are passed down from a SuperElection
            else:
                self.seattotals += self.listPR(*list(args)[1:])
        elif args[0] == "IRVlistPR":
            if "pop" in args or "eq" in args:
                self.seattotals += self.IRVlistPR(*([args[-1]]+list(args)[2:-1]))
            else:
                self.seattotals += self.IRVlistPR(*list(args)[1:])
        else:
            self.seattotals += getattr(self,args[0])(*(list(args)[1:]+["stot"]))
        

# List of dictionary items (key-value pairs) sorted in a decreasing order of value
def valsorted(stat):
    return sorted(stat.items(),key=lambda l:l[1],reverse=True)

def percentages(stat,rounding=-1) :
    totvotes = sum(stat.values())
    if not rounding==-1 :
        return {n: round(stat[n]*100./totvotes,rounding) for n in stat.keys()}
    else:
        return {n: stat[n]*100./totvotes for n in stat.keys()}

# A generic version of the SuperElection listPR function that can be used for any party-vote dictionary.
def listPR(stat,seats,*args):
    prseats = {x: 0 for x in stat.keys()}
    filledseats = 0
    if "lr" in args or "lrd" in args:
        quota = sum(stat.values())*1./seats
        if "lrd" in args:
            quota = 1 + sum(stat.values())/(seats+1.)
        seatcredit = {x[0]:x[1]/quota for x in stat.items()}
        prseats = {x[0]:int(x[1]) for x in seatcredit.items()}
        seatcredit = dict(Counter(seatcredit)-Counter(prseats))
        remseats = sorted(seatcredit.items(), key=lambda l:l[1], reverse=True)[0:seats-sum(prseats.values())]
        for x in remseats :
            prseats[x[0]] += 1
    elif "hh" in args:
        prseats = {x: 1 for x in stat.keys()}
        filledseats = len(stat)
        runningvotes = dict(stat.items())
        while filledseats < seats :
            pick = max(runningvotes.items(),key=lambda l:l[1])[0]
            runningvotes[pick] = runningvotes[pick]*math.sqrt(prseats[pick]*(prseats[pick]+1))/\
                                    math.sqrt((prseats[pick]+1)*(prseats[pick]+2))
            prseats[pick] += 1
            filledseats += 1
    else:
        divinterval = 1
        if len(args) > 0:
            numargs = [x for x in list(args) if isinstance(x, numbers.Number)]
            if len(numargs)>0:
                divinterval = numargs[0]
        runningvotes = dict(stat.items())
        while filledseats < seats :
            pick = max(runningvotes.items(),key=lambda l:l[1])[0]
            runningvotes[pick] = runningvotes[pick]*(1.+divinterval*prseats[pick])/(1.+divinterval*(prseats[pick]+1))
            prseats[pick] += 1
            filledseats += 1
    if "s" in args :
        vpcts = percentages(stat)
        spcts = percentages(prseats)
        print("An election is conducted for %d seats."%seats)
        print("The votes and the corresponding seats are as follows:")
        print("List  \tVotes\t(pct)\tSeats\t(pct)")
        sortvs = sorted(prseats.keys(),key=lambda l:stat[l],reverse=True)
        for v in sortvs :
            print("\n%s :\t%d\t(%.2f)\t%d\t(%.2f)" % (v,stat[v],vpcts[v],prseats[v],spcts[v]))
        print("\n")
    return prseats

        
class Voter() :
    """Simulates a voter with potentially changing political opinions registered to vote in one or more elections.
    
    Attributes:
        name : name string of the voter
        position: the political compass (economic, social) position of the voter (default: random following a normal distribution)
        regs: elections in which the voter is registered to vote
    """
    def __init__(self,regs=[],econpos="rand",socpos="rand",name=""):
        self.name = name
        self.position = (econpos,socpos)
        if econpos =="rand":
            self.position = (random.gauss(0,0.5),self.position[1])
        if socpos == "rand":
            self.position = (self.position[0],random.gauss(0,1))
        self.regs = list(regs)

    # repositions the voter politically
    def pos(self,econpos="rand",socpos="rand"):
        self.position = (econpos, socpos)
        if econpos == "rand":
            self.position = (random.gauss(0, 0.5), self.position[1])
        if socpos == "rand":
            self.position = (self.position[0], random.gauss(0, 1))

    # registers the voter in each election given as an argument
    def reg(self,*regs):
        self.regs += list(regs)

    # de-registers the voter in each election given as an argument
    def dereg(self,*regs):
        for r in regs:
            self.regs.remove(r)

    # replaces the registration of the voter with a new set of elections
    def newreg(self,*regs):
        self.regs = list(regs)

    # adds the voter's vote to a specific election (/election/ parameter), or to every election the voter is registered for (default)
    def vote(self,election="all",*args):
        votedelecs = []
        if election=="all":
            votedelecs = self.regs
        else:
            votedelecs = [self.regs[election]]
        for elec in votedelecs:
            posdists = {x: (self.position[0] - elec.positions[x][0]) ** 2 \
                        + (self.position[1] - elec.positions[x][1]) ** 2 \
                        for x in elec.positions.keys()}
            vote = [x[0] for x in sorted(posdists.items(), key=lambda l: l[1])]
            if "s" in args:
                print(vote)
            elec.addVote(*vote)

