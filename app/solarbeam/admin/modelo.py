import pulp

def main(input_modelo):
    iter_obj = []
    for oferta_compra, oferta_vtas in input_modelo.items():
        for id_oferta_vta in oferta_vtas.keys():
            iter_obj.append((oferta_compra, id_oferta_vta))

    
    ofertas_pulp = pulp.LpVariable.dicts("ofertas",
        ((id_off_comp, id_off_vta) for id_off_comp, id_off_vta in iter_obj),
        lowBound=0,
        cat='Integer')

    model = pulp.LpProblem("Asignacion", pulp.LpMinimize)
    #Minimización de precio
    model += pulp.lpSum(
        [ofertas_pulp[id_off_comp, id_off_vta] * 
        input_modelo[id_off_comp][id_off_vta] for id_off_comp, id_off_vta in iter_obj]
    ) 
    #Sistemas
    for oferta_compra in input_modelo:
        ofertas_pulp_en_oferta_compra = [oferta_pulp for oferta_pulp_ids, oferta_pulp 
                                        in ofertas_pulp.items() if oferta_pulp_ids[0] == oferta_compra ]
        model += pulp.lpSum(ofertas_pulp_en_oferta_compra) <= 1
        model += pulp.lpSum(ofertas_pulp_en_oferta_compra) >= 1
        
    model.solve()

    output = []
    for ids, oferta_pulp in ofertas_pulp.items():
        id_off_comp, id_off_vta = ids
        var_output = {
            'oferta_compra': id_off_comp,
            'oferta_venta': id_off_vta,
            'variable': bool(oferta_pulp.varValue),
        }
        output.append(var_output)
    
    return output