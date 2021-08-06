# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 16:35:37 2020

@author: PC
"""


import pandas as pd
from . import tarifas

def calc_costo_instalacion(kwp):
    costo = 0
    if kwp < 2.5:
        costo = 1400 * kwp
    elif kwp < 15:
        costo = 1300 * kwp
    elif kwp < 100:
        costo = 1200 * kwp
    elif kwp < 250:
        costo = 1100 * kwp
    else:
        costo = 1000 * kwp

    return costo * 20

def calc_costo_mto(kwp, año):
    costo = 0
    if kwp < 5:
        costo = 35 * kwp
    elif kwp < 15:
        costo = 36 * kwp
    elif kwp < 30:
        costo = 33 * kwp
    elif kwp < 50:
        costo = 27 * kwp
    elif kwp < 100:
        costo = 37 * kwp
    elif kwp < 250:
        costo = 35 * kwp
    else:
        costo = 28 * kwp

    return costo * año * 20

def obtener_nuevos_consumos(nuevo_consumo, consumo_base, consumo_inter, consumo_punta):
    consumos = []
    for tipo_consumo in [consumo_base, consumo_inter, consumo_punta]:
        if nuevo_consumo >= tipo_consumo:
            consumos.append(tipo_consumo)
            nuevo_consumo -= tipo_consumo
        else:
            consumos.append(nuevo_consumo)
            nuevo_consumo = 0
    return consumos

def main(a,df, cap, estado, municipio, tipo):
    df2 = a[["Month", "generation"]].groupby("Month").sum()*cap/1000
    df2  = df2.reset_index().rename(columns = {"Month": "mes"})
    
    df = df2.merge(df, on = "mes")
    df['precio_kwh'] = df.apply(lambda x: tarifas.calc_tarifa_gdmth(x['fecha'], estado, municipio, tipo,
                                  [x['kwh-base'], x['kwh-inter'], x['kwh-punta']], 
                                  [x['dem-base'], x['dem-inter'], x['dem-punta']]), axis=1)
    df2 = pd.DataFrame()
    rinv_inf = {}                                  
    rinv_noinf = {}
    for capacidad_gen in [0.5, 0.6, 0.7, 0.8, 0.9, 1]:
        banco_energia = []
        nuevos_consumos = []
        capacidad_total = cap * capacidad_gen
        # print(capacidad_total)
        df[f'generation-{capacidad_gen}'] = df['generation'] * capacidad_gen
        df[f'cap-{capacidad_gen}'] = capacidad_total

        for i, row in df.iterrows():
            generacion = row[f'generation-{capacidad_gen}']
            consumo_base = row['kwh-base']
            consumo_inter = row['kwh-inter']
            consumo_punta = row['kwh-punta']
            consumo = [consumo_base, consumo_inter, consumo_punta]
            consumo_total = sum(consumo)
            if generacion > consumo_total: 
                banco_energia.append(generacion - consumo_total)
                nuevos_consumos.append([0, 0, 0]) #no hubo consumo de red
            else:
                energia_almacenada = 0
                if banco_energia:
                    energia_almacenada = banco_energia[-1] # Energía almacenada del último mes
                
                consumo_real = consumo_total - (energia_almacenada + generacion)
                if consumo_real <= 0: # si la energia almacenada del último mes + la generacion actual es mayor
                    banco_energia.append(abs(consumo_real)) # se agrega el sobrante
                    nuevos_consumos.append([0, 0, 0]) #no hubo consumo de red
                else:
                    banco_energia.append(0)
                    nuevos_consumos.append(
                        obtener_nuevos_consumos(consumo_real, consumo_base, consumo_inter, consumo_punta)
                    )
        
        df[f'banco_energia-{capacidad_gen}'] = banco_energia
        df = pd.concat(
            [df, pd.DataFrame(data=nuevos_consumos, columns=[f'nuevo_kwh-base-{capacidad_gen}',
                        f'nuevo_kwh-inter-{capacidad_gen}', f'nuevo_kwh-punta-{capacidad_gen}'])],
            axis=1
        )
        df[f'nuevo_precio_kwh-{capacidad_gen}'] = df.apply(lambda x: tarifas.calc_tarifa_gdmth(x['fecha'], estado, municipio, tipo,
                                    [x[f'nuevo_kwh-base-{capacidad_gen}'], x[f'nuevo_kwh-inter-{capacidad_gen}'], x[f'nuevo_kwh-punta-{capacidad_gen}']], 
                                    [x['dem-base'], x['dem-inter'], x['dem-punta']]), axis=1)
        
        df[f"ahorro-{capacidad_gen}"] = df["precio_kwh"] - df[f"nuevo_precio_kwh-{capacidad_gen}"]


        ahorro = []
        ahorroinf = []
        anio = []
        ahor = df[f"ahorro-{capacidad_gen}"].sum()
        ahor2 = df[f"ahorro-{capacidad_gen}"].sum()
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
    
        df2["year"] = anio
        df2[f"ahorro_sin_inflacion-{capacidad_gen}"] = ahorro
        df2[f"ahorro_con_inflacion-{capacidad_gen}"] = ahorroinf 
        df2[f'cap-{capacidad_gen}'] = capacidad_total


        costo_inversion = calc_costo_instalacion(capacidad_total)

        df2[f'costo_mto-{capacidad_gen}'] = df2.apply(lambda x: calc_costo_mto(x[f'cap-{capacidad_gen}'], x['year']), axis=1)
        df2[f'costo_total-{capacidad_gen}'] = df2[f'costo_mto-{capacidad_gen}'] + costo_inversion
        df2[f'ahorro_neto_inf-{capacidad_gen}'] = df2[f'ahorro_con_inflacion-{capacidad_gen}'] - df2[f'costo_total-{capacidad_gen}']
        df2[f'ahorro_neto_noinf-{capacidad_gen}'] = df2[f'ahorro_sin_inflacion-{capacidad_gen}'] - df2[f'costo_total-{capacidad_gen}']

        # CON INFLACIÓN
        año_pasado = df2[df2[f"ahorro_neto_inf-{capacidad_gen}"]
                        < 0][f"ahorro_neto_inf-{capacidad_gen}"].iloc[-1]
        año_ahorro = df2[df2[f"ahorro_neto_inf-{capacidad_gen}"]
                        > 0][f"ahorro_neto_inf-{capacidad_gen}"].iloc[0]
        año_riv = df2[df2[f"ahorro_neto_inf-{capacidad_gen}"] < 0]["year"].iloc[-1] + 1

        rinv_inf[capacidad_gen] = (abs(año_pasado) / (abs(año_pasado) + año_ahorro)) + año_riv

        # SIN INFLACIÓN
        año_pasado_noinf = df2[df2[f"ahorro_neto_noinf-{capacidad_gen}"]
                            < 0][f"ahorro_neto_noinf-{capacidad_gen}"].iloc[-1]
        año_ahorro_noinf = df2[df2[f"ahorro_neto_noinf-{capacidad_gen}"]
                            > 0][f"ahorro_neto_noinf-{capacidad_gen}"].iloc[0]
        año_riv_noinf = df2[df2[f"ahorro_neto_noinf-{capacidad_gen}"]
                            < 0]["year"].iloc[-1] + 1

        rinv_noinf[capacidad_gen] = (abs(año_pasado_noinf) / (abs(año_pasado_noinf) + año_ahorro_noinf)) + año_riv_noinf

    return df, df2, rinv_inf, rinv_noinf