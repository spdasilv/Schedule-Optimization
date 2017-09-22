import random
import pandas as pd
from string import ascii_uppercase
from math import radians, cos, sin, asin, sqrt
import time

# Let W be the normalized weight of the interest point.
# Let T represent the average time spent visiting the interest point.
# Let ID be an unique identifier for a location.
# Let NAME be the name of a location.
# Let T_OPEN be the opening time of a location.
# Let T_CLOSE be the closing time of a location.
class InterestPoint:
    def __init__(self, w, t, id, name=None, t_open=None, t_close=None):
        self.w = w
        self.t = t
        self.id = id
        self.name = None
        self.t_open = None
        self.t_close = None
        if t_open is not None:
            self.t_open = t_open
        else:
            self.t_open = 540
        if t_close is not None:
            self.t_close = t_close
        else:
            self.t_close = 1080
        if name is not None:
            self.name = name
        else:
            self.name = ''.join(random.choice(ascii_uppercase) for i in range(8))

    def getW(self):
        return self.w

    def getT(self):
        return self.t

    def getId(self):
        return self.id

    def __repr__(self):
        return str(self.getId()) + ", " + str(self.getT()) + ", " + str(self.getW())

# Let each bucket represent each day. This class stores the overall detail of the points visited for a given day.
class Bucket:
    timeUsed = 0
    start_time = None
    end_time = None
    totalWeight = 0
    plan = None

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.plan = []

    def getTime(self, index):
        return self.destinationPoints[index]

    def incrementTime(self, time):
        self.timeUsed += time

    def getWeight(self, index):
        return self.destinationPoints[index]

    def incrementWeight(self, weight):
        self.totalWeight += weight

    def addToPlan(self, identification, time):
        self.plan.append((identification, time))

# The TourManager is responsible for generating the tours by running our custom heuristic.
class TourManager():

    base = None
    timeCosts = None
    destinationPoints = []

    def __init__(self, origin, timeCosts):
        self.base = origin
        self.timeCosts = timeCosts

    def addPoint(self, point):
        self.destinationPoints.append(point)

    def getPoint(self, index):
        return self.destinationPoints[index]

    def numberOfPoints(self):
        return len(self.destinationPoints)

    def allocateHeuristic(self):
        tourScore = 0
        buckets = []
		# We manually set the number of bucket here. In the future this will be a variable.
        for i in range(0, 2):
            buckets.append(Bucket(540, 1080))
        removed = set()
        for bucket in buckets:
            if len(removed) >= len(self.destinationPoints):
                break
            previousPoint = self.base
            search = True
            while True:
                expectedReturns = self.calculateExpectedReturns(removed, previousPoint)
                if len(expectedReturns) == 0:
                    break
                for pointIndex in range(0, len(expectedReturns)):
                    currentPoint = expectedReturns[pointIndex][0]
                    if bucket.start_time + bucket.timeUsed + self.timeCosts[(previousPoint.id, currentPoint.id)] + currentPoint.t + self.timeCosts[(currentPoint.id, self.base.id)] <= bucket.end_time and bucket.start_time <= currentPoint.t_open <= bucket.end_time and currentPoint.t_close <= bucket.end_time:
                        bucket.incrementWeight(currentPoint.w)
                        bucket.addToPlan(currentPoint.id, bucket.start_time + bucket.timeUsed + self.timeCosts[(previousPoint.id, currentPoint.id)])
                        bucket.incrementTime(currentPoint.t + self.timeCosts[(previousPoint.id, currentPoint.id)])
                        removed.add(currentPoint.id)
                        previousPoint = currentPoint
                        break
                    if pointIndex == len(expectedReturns) - 1:
                        search = False
                if not search:
                    break
            tourScore += bucket.totalWeight
        return tourScore, buckets

    def expectedReturn(self, travelTime, activityTime, weight):
        return (activityTime/(travelTime + activityTime))*weight

    def calculateExpectedReturns(self, removed, previousPoint):
        returns = []
        for city in self.destinationPoints:
            if city.id in removed:
                continue
            else:
                travelTime = self.timeCosts[(previousPoint.id, city.id)]
                returns.append((city, self.expectedReturn(travelTime, city.t, city.w)))
        return sorted(returns, key=lambda x: x[1], reverse=True)

# Calculate the great circle distance between two points on the earth (specified in decimal degrees)
def Haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

# Calculate the cost of time to travel between two points given an arbitrary moving speed.
def calculateCost(coordinates):
    time_cost = {}
    for key1, value1 in coordinates.items():
        for key2, value2 in coordinates.items():
            if value1['id'] == value2['id']:
                time_cost[(value1['id'], value2['id'])] = 0
            else:
                time_cost[(value1['id'], value2['id'])] = round(Haversine(value1['lon'], value1['lat'], value2['lon'], value2['lat'])*(60/20))
    return time_cost


if __name__ == '__main__':
    input = pd.read_csv("input.csv").T.to_dict()
    cost_matrix = calculateCost(input)
    tourmanager = TourManager(InterestPoint(0, 0, 0), cost_matrix)
    for key in input:
        if input[key]['id'] == 0:
            continue
        point = InterestPoint(input[key]['w'], input[key]['t'], input[key]['id'])
        tourmanager.addPoint(point)
    start = time.time()
    schedule = tourmanager.allocateHeuristic()
    end = time.time()
    print("Heuristic Run Time: " + str(end - start))
    print("Heuristic Score: " + str(schedule[0]))
    day = 0
    for bucket in schedule[1]:
        day += 1
        print("Day " + str(day))
        for activity in bucket.plan:
            print(activity)
