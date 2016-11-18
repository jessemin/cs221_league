'''
500 requests every 10 minutes
100 requests every 10 seconds
key: f239b7ff-7cdb-464a-abf0-cfb2c1c7e287 / donotgoroaming
'''
import requests
import time
import Queue
import pickle
import json


class DataCollector:
    def __init__(self):
        self.API_KEY = "f239b7ff-7cdb-464a-abf0-cfb2c1c7e287"
        #self.seed = "4460427"
        self.seed = "4460427"
        self.seedPlayers = None
        self.visited = set()
        self.data = dict()

    def run(self):
        self.seedPlayers, self.visited = self.initializeBFS()
        copyVisited = set(self.visited)
        #for p in copyVisited:
        #    self.addMatchlist(p)

    def seedMatchlistRequest(self):
        MATCHLIST_API = "https://kr.api.pvp.net/api/lol/kr/v2.2/matchlist/by-summoner/{}?rankedQueues=RANKED_SOLO_5x5&seasons=SEASON2016&api_key={}".format(self.seed, self.API_KEY)
        return requests.get(MATCHLIST_API).json()

    def matchRequest(self,matchId):
        MATCH_API = "https://kr.api.pvp.net/api/lol/kr/v2.2/match/{}?api_key={}".format(matchId, self.API_KEY)
        return requests.get(MATCH_API).json()

    def getSummonerId(self, summonerName):
        SUMMONERID_API = "https://na.api.pvp.net/api/lol/na/v1.4/summoner/by-name/donotgoroaming?api_key=f239b7ff-7cdb-464a-abf0-cfb2c1c7e287"
        return requests.get(SUMMONERID_API).json()

    def getStats(self, summonerId):
        STATS_API = "https://na.api.pvp.net/api/lol/na/v1.3/stats/by-summoner/71149441/ranked?season=SEASON2016&api_key=f239b7ff-7cdb-464a-abf0-cfb2c1c7e287"
        return requests.get(STATS_API).json()

    def initializeBFS(self):
        matchIds = []
        players = Queue.Queue()
        visited = set()
        matches = None
        trialNum = 0
        while not matches and trialNum < 10:
            try:
                trialNum += 1
                matches = self.seedMatchlistRequest()["matches"]
            except:
                print "Error occurred during parsing seed matches"
                continue
        time.sleep(1)
        self.data[self.seed] = matches
        matchCnt = 0
        for match in matches:
            matchCnt += 1
            matchInfo = self.matchRequest(match["matchId"])
            try:
                participants = matchInfo["participantIdentities"]
            except KeyError:
                print "KeyError occurred during parsing match {} of seed".format(match["matchId"])
                print matchInfo
                print "============================================"
                continue
            for participant in participants:
                summonerId = participant["player"]["summonerId"]
                if summonerId in visited:
                    continue
                players.put(summonerId)
                visited.add(summonerId)
            time.sleep(1)
        return players, visited

    def addMatchlist(self, p):
        MATCHLIST_API = "https://kr.api.pvp.net/api/lol/kr/v2.2/matchlist/by-summoner/{}?rankedQueues=RANKED_SOLO_5x5&seasons=SEASON2016&api_key={}".format(p, self.API_KEY)
        matchIds = []
        matches = None
        trialNum = 0
        while not matches and trialNum < 10:
            try:
                trialNum += 1
                matches = requests.get(MATCHLIST_API).json()["matches"]
            except:
                print "Error occurred during parsing {}'s matches".format(str(p))
                continue
        time.sleep(1)
        self.data[p] = matches
        matchCnt = 0
        for match in matches:
            matchCnt += 1
            matchInfo = self.matchRequest(match["matchId"])
            try:
                participants = matchInfo["participantIdentities"]
            except KeyError:
                print "KeyError occurred during parsing match {}".format(match["matchId"])
                print matchInfo
                print "============================================"
                continue
            for participant in participants:
                summonerId = participant["player"]["summonerId"]
                if summonerId in self.visited:
                    continue
                self.seedPlayers.put(summonerId)
                self.visited.add(summonerId)
            time.sleep(0.2)
            break

a = DataCollector()
a.run()
with open('data.json', 'w') as outfile:
    json.dump(a.data, outfile)
with open('data.json') as data_file:
    data = json.load(data_file)
    print len(data)
#pickle.dump(a.data, open("test", "wb"))
