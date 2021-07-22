# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 16:35:37 2020

@author: PC
"""


import pandas as pd
import numpy as np


def main(a,df, cap):
    df2 = a[["Month", "Generation"]].groupby("Month").sum()*cap/1000
    df2  = df2.reset_index().rename(columns = {"Month": "Mes"})
    print('MEEEEEEEEEEEEEEEESSS')
    print(df2['Mes'])
    df = df2.merge(df, on = "Mes")
    
    banco = []
    banco_acum = []
    red = []
    bancoi = 0
    precio = []
    for i in df[["Generation", "kWh", "PreciokWh"]].iterrows():
        gen = i[1]["Generation"]
        con = i[1]["kWh"]
        pre = i[1]["PreciokWh"]
        net = gen - con
        if gen >= con:
            banco.append(net)
            bancoi += net
            banco_acum.append(bancoi)
            red.append(0)
            precio.append(64)
        else:
            if abs(net) < bancoi:
                banco.append(net)
                bancoi += net
                banco_acum.append(bancoi)
                red.append(0)
                precio.append(64)
            else:
                banco.append(-bancoi)
                banco_acum.append(0)
                red.append(abs(net+bancoi))
                bancoi += 0
                precio.append(abs(net+bancoi)*pre) # No se tiene que calcular el precio ocn las tarifas? 
    df["Banco-mes"] = banco
    df["Banco-neto"] =  banco_acum
    df["Consumo-red"] = red
    df["Nueva-Facturación"] = precio
    df["Ahorro"] = df["Facturacion"] - df["Nueva-Facturación"]
    
    ahorro = []
    ahorroinf = []
    anio = []
    ahor = df["Ahorro"].sum()
    ahor2 = df["Ahorro"].sum()
    for i in range(25):
        if i == 0:
            ahorro.append(0)
            ahorroinf.append(0)
            ahorf = 0
            ahorf2 = 0
        else:
            ahorf += ahor
            ahor2 = ahor2*1.046
            ahorf2 += ahor2
            ahorro.append(ahorf)
            ahorroinf.append(ahorf2)
        anio.append(i)
    df2 = pd.DataFrame()
    df2["Año"] = anio
    df2["Ahorro sin incremento"] = ahorro
    df2["Ahorro con inflación"] = ahorroinf 
    return df, df2