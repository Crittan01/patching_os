# #!/usr/bin/env python3

# import logging
# import textwrap

# from utilities import add_host_to_group, return_valid_text, safe_get, sanitize_group_name, validate_json


# def build_inventory(inventory_data, lote):
#     excluded_hosts = []  # Lista para almacenar exclusiones
#     imported_hosts = [] # Lista para almacenar los host importados
#     # Estructura básica del inventario
#     ansible_inventory = {
#         '_meta': {
#             'hostvars': {}
#         },
#         'all': {
#             'hosts': [],
#             'vars': {}
#         },
#         'server_informes': {
#             'hosts': ['ansibleawx'],
#             'vars': {
#                 'ansible_connection': 'ssh',
#             }
#         }
#     }
    
      
#     os_counts = {}
#     stage_groups = {}
    
#     logging.info(f"Revisando {len(inventory_data)} registros")

#     for inventory in inventory_data:
#                # Añadir host a 'all'
#         ip = inventory["IP"]
#         ansible_inventory['all']['hosts'].append(ip)
#         if (lote == ""):
#             inventory['Lote'] = sanitize_group_name("lote_"+inventory['Almacen'])
#         else:
#             inventory['Lote'] = "lote_"+lote
            
#         stage = sanitize_group_name(inventory['Lote'])
#         inventory['Lote'] = stage



#         data_host = {
#             'environment': validate_json("Ambiente", inventory),
#             'type_device': return_valid_text(validate_json("Tipo_Dispositivo", inventory)),
#             'id': safe_get(validate_json('Id', inventory)),
#             'list': safe_get(validate_json('Lista', inventory)),
#             'description': safe_get(validate_json('Descripción', inventory)),
#             'ip': ip,
#             'store': safe_get(validate_json("Almacen", inventory)),
#             'chain': return_valid_text(validate_json("Negocio", inventory)),
#             'ansible_host': validate_json("IP", inventory),
#             'type': return_valid_text(validate_json("Tipo", inventory)),
#             'os': safe_get(validate_json("Sistema_Operativo", inventory)),
#             'database': safe_get(validate_json("Base_Datos", inventory)),
#             'java': safe_get(validate_json("Java", inventory)),
#             'crq': safe_get(validate_json("CRQ", inventory)),
#             'lote': return_valid_text(validate_json("Lote", inventory)),
#             'notes': return_valid_text(validate_json("Comentarios", inventory)),
#             'type_pos':  return_valid_text(validate_json("Tipo_Caja", inventory))
#         }
#         # Agregar hostvars
#         ansible_inventory['_meta']['hostvars'][ip] = data_host
#         imported_hosts.append(data_host)

#         if stage:
#             add_host_to_group(stage_groups, stage, ip)

#     ansible_inventory['_meta']['hostvars']['ansibleawx'] = {
#             'ansible_host': '10.181.5.247'
#         }

#     # Actualizar el inventario con los grupos
#     ansible_inventory.update(stage_groups)
    
#     logging.info(f"{len(ansible_inventory['all']['hosts'])} registros guardados en inventario")
#     logging.info(textwrap.dedent(f"""\
#     Se han omitido {len(inventory_data) - len(ansible_inventory['all']['hosts'])} registros porque no cumplen
#     con los criterios de filtrado para los sistemas operativos que requieren parches.
#     Por favor, revisa los sistemas operativos en tu inventario para asegurarte de que estén alineados
#     con los criterios establecidos."""))
    
   
#     return ansible_inventory
