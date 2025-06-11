#!/usr/bin/env python3
 
import json
import logging
import os
import re
import sys
import textwrap
import time
import unicodedata

import pandas as pd

# #Recibir los parametros
# parser = argparse.ArgumentParser(description="Parametros para Filtrar el Inventario")
# parser.add_argument("--negocio", type=str, help="negocio", default=None)
# parser.add_argument("--almacen", type=str, help="almacen", default=None)
# parser.add_argument("--ip", type=str, help="negocio", default=None)
# parser.add_argument("--lista", type=str, help="lista", default=None)
# parser.add_argument("--path", type=str, help="lista", default="source")


# = parser.parse_)

def return_valid_text(value):
    """Devuelve el valor si no es NaN, o 'None' en caso contrario."""
    return value if pd.notna(value) else None

def safe_get(value):
    """Devuelve el valor si no es NaN, reemplaza caracteres especiales y convierte a minúsculas."""
    if pd.notna(value):
        return unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('utf-8').strip().lower()
    return None

def sanitize_group_name(group_name):
    """ 
    Reemplazar caracteres no permitidos en los nombres de los grupos.
    - Elimina tildes y acentos.
    - Sustituye cualquier carácter que no sea alfanumérico, guion o guion bajo por guion bajo.
    """
    if not pd.notna(group_name) or not group_name:
        return "Sin lote"
    
    normalized_name = unicodedata.normalize('NFKD', group_name)
    normalized_name = "".join([c for c in normalized_name if not unicodedata.combining(c)])
    
    # Reemplazar caracteres no alfanuméricos por guión bajo y eliminar dobles guiones bajos
    return re.sub(r'[_-]+', '_', re.sub(r'[^A-Za-z0-9_-]', '_', normalized_name.strip().lower()))

def add_host_to_group(group_dict, group_name, hostname):
    """Agrega un host al grupo correspondiente, creando el grupo si no existe."""
    if group_name not in group_dict:
        group_dict[group_name] = {'hosts': []}
    group_dict[group_name]['hosts'].append(hostname)
    
def validate_json(field, json_data):
    if field not in json_data:
        return ''
    return json_data[field]

def build_inventory(inventory_data, lote):
    excluded_hosts = []  # Lista para almacenar exclusiones
    imported_hosts = [] # Lista para almacenar los host importados
    # Estructura básica del inventario
    ansible_inventory = {
        '_meta': {
            'hostvars': {}
        },
        'all': {
            'hosts': [],
            'vars': {}
        },
        'server_informes': {
            'hosts': ['ansibleawx'],
            'vars': {
                'ansible_connection': 'ssh',
            }
        }
    }
    
      
    os_counts = {}
    stage_groups = {}
    
    logging.info(f"Revisando {len(inventory_data)} registros")

    for inventory in inventory_data:
               # Añadir host a 'all'
        ip = inventory["IP"]
        ansible_inventory['all']['hosts'].append(ip)
        if (lote == ""):
            inventory['Lote'] = sanitize_group_name("lote_"+inventory['Almacen'])
        else:
            inventory['Lote'] = "lote_"+lote
            
        stage = sanitize_group_name(inventory['Lote'])
        inventory['Lote'] = stage



        data_host = {
            'environment': validate_json("Ambiente", inventory),
            'type_device': return_valid_text(validate_json("Tipo_Dispositivo", inventory)),
            'id': safe_get(validate_json('Id', inventory)),
            'list': safe_get(validate_json('Lista', inventory)),
            'description': safe_get(validate_json('Descripción', inventory)),
            'ip': ip,
            'store': safe_get(validate_json("Almacen", inventory)),
            'chain': return_valid_text(validate_json("Negocio", inventory)),
            'ansible_host': validate_json("IP", inventory),
            'type': return_valid_text(validate_json("Tipo", inventory)),
            'os': safe_get(validate_json("Sistema_Operativo", inventory)),
            'database': safe_get(validate_json("Base_Datos", inventory)),
            'java': safe_get(validate_json("Java", inventory)),
            'crq': safe_get(validate_json("CRQ", inventory)),
            'lote': return_valid_text(validate_json("Lote", inventory)),
            'notes': return_valid_text(validate_json("Comentarios", inventory)),
            'type_pos':  return_valid_text(validate_json("Tipo_Caja", inventory))
        }
        # Agregar hostvars
        ansible_inventory['_meta']['hostvars'][ip] = data_host
        imported_hosts.append(data_host)

        if stage:
            add_host_to_group(stage_groups, stage, ip)

    ansible_inventory['_meta']['hostvars']['ansibleawx'] = {
            'ansible_host': '10.181.5.247'
        }

    # Actualizar el inventario con los grupos
    ansible_inventory.update(stage_groups)
    
    logging.info(f"{len(ansible_inventory['all']['hosts'])} registros guardados en inventario")
    logging.info(textwrap.dedent(f"""\
    Se han omitido {len(inventory_data) - len(ansible_inventory['all']['hosts'])} registros porque no cumplen
    con los criterios de filtrado para los sistemas operativos que requieren parches.
    Por favor, revisa los sistemas operativos en tu inventario para asegurarte de que estén alineados
    con los criterios establecidos."""))
    
   
    return ansible_inventory


# Define la ruta para la carpeta de logs dentro de generate_files
logs_dir = os.path.join(os.path.dirname(__file__), 'generated_files', 'logs')
stats_dir = os.path.join(os.path.dirname(__file__), 'generated_files', 'stats')

# Crea la carpeta si no existe
os.makedirs(logs_dir, exist_ok=True)
os.makedirs(stats_dir, exist_ok=True)

# Configurar el logger
log_file = os.path.join(logs_dir, f'result.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        # input_data = json.load(sys.stdin)
        # negocio = input_data.get('negocio')
        # almacen = input_data.get('almacen')
        # ip = input_data.get('ip')
        # lista = input_data.get('lista')
        negocio="*"
        almacen="*"
        ip="10.185.0.0"
        lista="*"
        path = '../inventory/'
        logging.info(f"Ejecutando Conversión de Inventario a AWX")

        start_time = time.perf_counter()
        

        # Abrir y cargar el archivo JSON
        logging.info(f"Cargando Archivo de Inventario en JSON")


        with open(path+'/inventory.json', 'r', encoding='utf-8') as archivo:
            inventory_data = json.load(archivo)
            

            
        inventory_filter = inventory_data
        lote = ""

        if (negocio is not None) and (negocio != '*'):
            inventory_filter = [item for item in inventory_data if item.get("Negocio") == negocio]
            if lote!="":
                lote = lote + "_" + negocio
            else:
                lote = negocio

        if (almacen is not None) and (almacen != '*'):
            inventory_filter = [item for item in inventory_data if item.get("Almacen") == almacen]
            if lote!="":
                lote = lote + "_" + almacen
            else:
                lote = almacen
        
        if (ip is not None) and (ip != '*'):
            inventory_filter = [item for item in inventory_data if item.get("IP") == ip]
            if lote!="":
                lote = lote + "_" + ip
            else:
                lote = ip

        if (lista is not None) and (lista != '*'):
            inventory_filter = [item for item in inventory_data if item.get("Lista") == lista]
            if lote!="":
                lote = lote + "_" + lista
            else:
                lote = lista
        ansible_inventory = build_inventory(inventory_filter, lote)
        
        elapsed_time = time.perf_counter() - start_time

        # Imprimir el inventario en formato JSON para Ansible
        jsonString = json.dumps(ansible_inventory, indent=4, ensure_ascii=False)

        logging.info(f"Guardando archivo de Salida")

        # with open('output.json', 'w') as f:
        #     f.write(jsonString)

        logging.info(f"Tiempo finalizado: {elapsed_time:.2f} segundos")
        print(json.dumps(ansible_inventory, indent=4, ensure_ascii=False))

    except Exception as e:
        logging.error(f"Error al generar el inventario dinámico: {e}")
        print(json.dumps({"_meta": {"hostvars": {}}}))
        sys.exit(1)
        
        
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        main()
    else:
        print(json.dumps({"_meta": {"hostvars": {}}}))