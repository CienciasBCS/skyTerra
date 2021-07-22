# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 00:03:14 2020

@author: PC
"""

import pandas as pd
from . import irradiacion_hsp as irra


def main(lat, lon, year, kwh_an):
    #lat, lon, year = 24.139569, -110.316460, 2008
    a = irra.main(lat, lon, year)

    noct = 45
    ppot = -.0041
    pot = 500
    npan = 2000
    invef = .95
    dccab = .99
    accab = .99
    a["Cell_Temp"] = a["Temperature"]+(a["Irra"]/800)*(noct-20)
    a["Perd_Temp"] = pot + pot*ppot*(a["Cell_Temp"]-20)
    a["Generation_solar"] = npan*(pot + pot*ppot*(a["Cell_Temp"]-20))*a["HSP"]
    a["Generation"] = a["Generation_solar"]*invef*dccab*accab/1000
    a["Generation2"] = a["Generation_solar"]*invef*dccab*accab*.5/1000
    cap_clien = (kwh_an/a["Generation"].sum())*(pot*npan/1000)
    return a, cap_clien
