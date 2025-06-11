#!/usr/bin/env python3
 
import json
import logging
import os
import re
import sys
import textwrap
import time
import unicodedata
import argparse

# import pandas as pd  # Comentado para evitar dependencias

def return_valid_text(value):
    """Devuelve el valor si no es NaN, o 'None' en caso contrario."""
    return value if value is not None and str(value).lower() not in ['nan', 'none', ''] else None

def safe_get(value):
    """Devuelve el valor si no es NaN, reemplaza caracteres especiales y convierte a minúsculas."""
    if value is not None and str(value).lower() not in ['nan', 'none', '']:
        return unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('utf-8').strip().lower()
    return ''

def sanitize_group_name(group_name):
    """ 
    Reemplazar caracteres no permitidos en los nombres de los grupos.
    - Elimina tildes y acentos.
    - Sustituye cualquier carácter que no sea alfanumérico, guion o guión bajo por guión bajo.
    """
    if not group_name or str(group_name).lower() in ['nan', 'none', '']:
        return "sin_lote"
    
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

        # print(validate_json('Id', inventory))
        
        
        data_host = {
            'environment': validate_json("Ambiente", inventory),
            'type_device': return_valid_text(validate_json("Tipo_Dispositivo", inventory)),
            'id': ip,
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

def setup_logging():
    """Configura el logging solo si es necesario"""
    try:
        # Define la ruta para la carpeta de logs dentro de generate_files
        logs_dir = os.path.join(os.path.dirname(__file__), 'generated_files', 'logs')
        
        # Crea la carpeta si no existe
        os.makedirs(logs_dir, exist_ok=True)
        
        # Configurar el logger
        log_file = os.path.join(logs_dir, f'result.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    except:
        # Si no se puede configurar el logging, usar configuración básica
        logging.basicConfig(level=logging.ERROR)

def get_inventory_data():
    """Carga y filtra los datos del inventario"""
    try:
        # Parámetros por defecto
        negocio = "*"
        almacen = "*"
        ip = "172.25.16.185"
        lista = "*"
        path = '../inventory/'
        
        # Intentar cargar desde variables de entorno si están disponibles
        negocio = os.environ.get('AWX_NEGOCIO', negocio)
        almacen = os.environ.get('AWX_ALMACEN', almacen)
        ip = os.environ.get('AWX_IP', ip)
        lista = os.environ.get('AWX_LISTA', lista)
        path = os.environ.get('AWX_INVENTORY_PATH', path)
        
        logging.info(f"Ejecutando Conversión de Inventario a AWX")
        logging.info(f"Cargando Archivo de Inventario en JSON")

        # Intentar diferentes rutas para el archivo de inventario
        possible_paths = [
            os.path.join(path, 'inventory.json'),
            'inventory.json',
            '../inventory/inventory.json',
            '/runner/project/inventory/inventory.json'
        ]
        
        inventory_data = None
        for file_path in possible_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as archivo:
                    inventory_data = json.load(archivo)
                    logging.info(f"Inventario cargado desde: {file_path}")
                    break
            except FileNotFoundError:
                continue
        
        if inventory_data is None:
            logging.error("No se pudo encontrar el archivo inventory.json")
            return []
            
        inventory_filter = inventory_data
        lote = ""

        # Aplicar filtros
        if (negocio is not None) and (negocio != '*'):
            inventory_filter = [item for item in inventory_data if item.get("Negocio") == negocio]
            lote = negocio

        if (almacen is not None) and (almacen != '*'):
            inventory_filter = [item for item in inventory_filter if item.get("Almacen") == almacen]
            if lote != "":
                lote = lote + "_" + almacen
            else:
                lote = almacen
        
        if (ip is not None) and (ip != '*'):
            inventory_filter = [item for item in inventory_filter if item.get("IP") == ip]
            if lote != "":
                lote = lote + "_" + ip
            else:
                lote = ip

        if (lista is not None) and (lista != '*'):
            inventory_filter = [item for item in inventory_filter if item.get("Lista") == lista]
            if lote != "":
                lote = lote + "_" + lista
            else:
                lote = lista
                
        return inventory_filter, lote
        
    except Exception as e:
        logging.error(f"Error al cargar datos del inventario: {e}")
        return [], ""

def get_host_vars(hostname):
    """Retorna las variables para un host específico"""
    try:
        inventory_data, lote = get_inventory_data()
        if not inventory_data:
            return {}
            
        ansible_inventory = build_inventory(inventory_data, lote)
        
        # Buscar las variables del host específico
        if hostname in ansible_inventory['_meta']['hostvars']:
            return ansible_inventory['_meta']['hostvars'][hostname]
        else:
            return {}
            
    except Exception as e:
        logging.error(f"Error al obtener variables del host {hostname}: {e}")
        return {}

def get_full_inventory():
    """Retorna el inventario completo"""
    try:
        inventory_data, lote = get_inventory_data()
        if not inventory_data:
            return {"_meta": {"hostvars": {}}}
            
        ansible_inventory = build_inventory(inventory_data, lote)
        return ansible_inventory
        
    except Exception as e:
        logging.error(f"Error al generar el inventario dinámico: {e}")
        return {"_meta": {"hostvars": {}}}

def main():
    """Función principal que maneja los argumentos de Ansible"""
    setup_logging()
    
    # Parser para argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Inventario dinámico de Ansible para AWX')
    parser.add_argument('--list', action='store_true', 
                       help='Listar todos los hosts (requerido por Ansible)')
    parser.add_argument('--host', 
                       help='Obtener variables para un host específico')
    
    args = parser.parse_args()
    
    try:
        if args.list:
            # Ansible solicita el inventario completo
            inventory = get_full_inventory()
            print(json.dumps(inventory, indent=2, ensure_ascii=False))
            
        elif args.host:
            # Ansible solicita variables de un host específico
            host_vars = get_host_vars(args.host)
            print(json.dumps(host_vars, indent=2, ensure_ascii=False))
            
        else:
            # Si no se proporcionan argumentos, mostrar ayuda
            parser.print_help()
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"Error en main: {e}")
        # En caso de error, devolver inventario vacío válido
        print(json.dumps({"_meta": {"hostvars": {}}}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()