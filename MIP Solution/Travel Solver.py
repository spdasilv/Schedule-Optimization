#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyomo.core.base import ConcreteModel
from pyomo.environ import *
import math
import random
import pandas as pd
from string import ascii_uppercase
from math import radians, cos, sin, asin, sqrt


def Haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


def prepareInput(coordinates):
    C = {}
    I = []
    T = {}
    W = {}
    for key1, value1 in coordinates.items():
        I.append(int(value1['id']))
        T[int(value1['id'])] = int(value1['t'])
        W[int(value1['id'])] = int(value1['w'])
        for key2, value2 in coordinates.items():
            if value1['id'] == value2['id']:
                C[(int(value1['id']), int(value2['id']))] = 0
            else:
                C[(int(value1['id']), int(value2['id']))] = int(math.ceil(Haversine(value1['lon'], value1['lat'], value2['lon'], value2['lat'])*(4/20)))
    return I, T, W, C


# Creation of a Concrete Model
model = ConcreteModel()


# Read Inputs

input = pd.read_csv("input.csv").T.to_dict()
model_input = prepareInput(input)

## Define sets ##

model.t = Set(initialize=range(0, 96), doc='Times')
model.d = Set(initialize=range(0, 2), doc='Days')
model.i = Set(initialize=model_input[0], doc='Activities')
model.j = SetOf(model.i)

## Define parameters ##

model.Ti = Param(model.i, initialize=model_input[1], doc='Average Times')
model.Wi = Param(model.i, initialize=model_input[2], doc='Weight Scores')
model.Cij = Param(model.i, model.j, initialize=model_input[3], doc='Cost of Trip')

Adt = {}
for d in range(0, 2):
    for t in range(0, 96):
        if 36 <= t < 36 + 36:
            Adt[(d, t)] = 1
        else:
            Adt[(d, t)] = 0
model.Adt = Param(model.d, model.t, initialize=Adt, doc='Availability')

Oidt = {}
for i in range(0, len(model_input[0])):
    for d in range(0, 2):
        for t in range(0, 96):
            if i == 0:
                Oidt[(i, d, t)] = 1
                continue
            if 36 <= t <= 72:
                Oidt[(i, d, t)] = 1
            else:
                Oidt[(i, d, t)] = 0

model.Oidt = Param(model.i, model.d, model.t, initialize=Oidt, doc='Business Hours')

## Define variables ##
model.Yijdt = Var(model.i, model.j, model.d, model.t, within=Binary, doc='Going to Activity')
model.Sijdt = Var(model.i, model.j, model.d, model.t, within=Binary, doc='Followed by Activity')


## Define constraints ##
def Availability(model, i, j, d, t):
    tmax = 95 if t + model.Cij[i, j] + model.Ti[i] >= 95 else t + model.Cij[i, j] + model.Ti[i]
    return model.Sijdt[i, j, d, t] <= model.Adt[d, tmax]
model.Availability = Constraint(model.i, model.j, model.d, model.t, rule=Availability, doc='Availability')


def GroupAvailability(model, i, j, d, t):
    return model.Sijdt[i, j, d, t] <= model.Adt[d, t]
model.GroupAvailability = Constraint(model.i, model.j, model.d, model.t, rule=GroupAvailability, doc='Group Availability')


def IsOpen(model,i, j, d, t):
    tmax = 95 if t + model.Cij[i, j] + model.Ti[i] >= 95 else t + model.Cij[i, j] + model.Ti[i]
    return model.Sijdt[i, j, d, t] <= model.Oidt[j, d, tmax]
model.IsOpen = Constraint(model.i, model.j, model.d, model.t, rule=IsOpen, doc='Is Open')


def BusinessAvailability(model, i, j, d, t):
    return model.Sijdt[i, j, d, t] <= model.Oidt[i, d, t]
model.BusinessAvailability = Constraint(model.i, model.j, model.d, model.t, rule=BusinessAvailability, doc='Business Availability')


def startOnce(model, i):
    if i == 0:
        return Constraint.Skip
    else:
        return sum(model.Sijdt[i, j, d, t] for j in model.j for d in model.d for t in model.t) <= 1
model.startOnce = Constraint(model.i, rule=startOnce, doc='Start Activity Once')

def endtOnce(model, j):
    if j == 0:
        return Constraint.Skip
    else:
        return sum(model.Sijdt[i, j, d, t] for i in model.i for d in model.d for t in model.t) <= 1
model.endtOnce = Constraint(model.j, rule=endtOnce, doc='End Activity Once')


def startAtHotel(model, d):
    return sum(model.Sijdt[0, j, d, t] for j in model.j for t in model.t) == 1
model.startAtHotel = Constraint(model.d, rule=startAtHotel, doc='Start at Hotel')


def endAtHotel(model, d):
    return sum(model.Sijdt[i, 0, d, t] for i in model.i for t in model.t) == 1
model.endAtHotel = Constraint(model.d, rule=endAtHotel, doc='End at Hotel')


def circularRule(model, d, t):
    return sum(model.Sijdt[i, i, d, t] for i in model.i) == 0
model.circularRule = Constraint(model.d, model.t, rule=circularRule, doc='No Circles')


def CompAct(model, i, j, d, t):
    if t + model.Cij[i, j] + model.Ti[i] + 1 >= 96:
        tmax = 96
        return sum(model.Yijdt[i, j, d, g] for g in range(t, tmax)) >= model.Sijdt[i, j, d, t]*(model.Cij[i, j] + model.Ti[i])
    if t + model.Cij[i, j] + model.Ti[i] == t:
        return Constraint.Skip
    else:
        tmax = t + model.Cij[i, j] + model.Ti[i]
        return sum(model.Yijdt[i, j, d, g] for g in range(t, tmax)) >= model.Sijdt[i, j, d, t]*(model.Cij[i, j] + model.Ti[i])
model.CompAct = Constraint(model.i, model.j, model.d, model.t, rule=CompAct, doc='Complete Activity')


def NoIntersect(model, d, t):
    return sum(model.Yijdt[i, j, d, t] for i in model.i for j in model.j) <= 1
model.NoIntersect = Constraint(model.d, model.t, rule=NoIntersect, doc='No Intersect')


def limitActivities(model, d, t):
    return sum(model.Sijdt[i, j, d, t] for i in model.i for j in model.j) <= 1
model.limitActivities = Constraint(model.d, model.t, rule=limitActivities, doc='Schedule Activities')


def Continuity(model, i ,j, d, t):
    if j == 0:
        return Constraint.Skip
    else:
        return sum(model.Sijdt[j, h, d, g] for g in range(t + 1, 96) for h in model.j) >= model.Sijdt[i, j, d, t]
model.Continuity = Constraint(model.i, model.j, model.d, model.t, rule=Continuity, doc='Continuity')

## Define Objective and solve ##
def objectiveRule(model):
    return sum(model.Wi[i]*sum(model.Sijdt[i, j, d, t] for j in model.j for d in model.d for t in model.t) for i in model.i)
model.objectiveRule = Objective(rule=objectiveRule, sense=maximize, doc='Define Objective Function')


## Display of the output ##
# Display x.l, x.m ;
def pyomo_postprocess(options=None, instance=None, results=None):
    with open('results.txt', 'w') as f:
        for key, value in instance.Sijdt._data.items():
            if value._value > 0.5:
                f.write('% s: % s\n' % (key, int(round(value._value))))


if __name__ == '__main__':
    # This emulates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ

    opt = SolverFactory("gurobi")
    results = opt.solve(model)
    # sends results to stdout
    results.write()
    print("\nWriting Solution\n" + '-' * 60)
    pyomo_postprocess(None, model, results)
    print("Complete")
