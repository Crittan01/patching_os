#!/usr/bin/env python3

import json
import logging
import os
import sys
import textwrap
import time
import re
import unicodedata
import pandas as pd
from dotenv import load_dotenv
import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font
import filter_so
from datetime import datetime
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
import normalizer_excel
import constants

sheet_local_name = "Servidores Windows"
# Define la ruta para la carpeta de logs dentro de generated_files
logs_dir = os.path.join(os.path.dirname(__file__), 'generated_files', 'logs')
stats_dir = os.path.join(os.path.dirname(__file__), 'generated_files', 'stats')

# Crea la carpeta si no existe
os.makedirs(logs_dir, exist_ok=True)
os.makedirs(stats_dir, exist_ok=True)

# Configurar el logger
log_file = os.path.join(logs_dir, f'custom_inventory_{sheet_local_name}.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_lote_format(lote):
    if lote is not None and not re.fullmatch(r'^Lote_\d{1,3}$', lote): 
        logging.error(f"Nombre del lote inválido: {lote}")
    return lote 

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

def upload_to_sharepoint(local_path, remote_path):
    """
    Subir un archivo a SharePoint desde una ruta local a una ruta remota dada en SharePoint.
    
    Args:
        local_path (str): La ruta local del archivo a subir.
        remote_path (str): La ruta remota donde se guardará el archivo en SharePoint.
    """
    url = os.getenv('url_sharepoint')  # URL del sitio de SharePoint
    client_id = os.getenv('client_id')  # ID del cliente para la autenticación
    client_secret = os.getenv('client_secret')  # Secreto del cliente para la autenticación
    
    logging.info(f"Subiendo archivo {local_path} a SharePoint en {remote_path}")
    
    try:
        # Autenticación
        credentials = ClientCredential(client_id, client_secret)
        ctx = ClientContext(url).with_credentials(credentials)
        
        # Obtener la carpeta raíz del sitio (base)
        folder = ctx.web.get_folder_by_server_relative_url(remote_path)
        
        # Abre el archivo local para cargarlo
        with open(local_path, "rb") as file_content:
            # Subir el archivo
            file_name = os.path.basename(local_path)
            file = folder.upload_file(file_name, file_content).execute_query()
            
        logging.info(f"El archivo {file_name} ha sido subido exitosamente a: {file.serverRelativeUrl}")
        return file.serverRelativeUrl
        
    except Exception as e:
        logging.error(f"Error al subir el archivo: {e}")
        print(json.dumps({"_meta": {"hostvars": {}}}))
        sys.exit(1)
 

def download_inventory_file():
    # url = os.getenv('url_sharepoint')
    # folder_base_sharepoint = os.getenv('folder_base_sharepoint')
    # client_id = os.getenv('client_id')
    # client_secret = os.getenv('client_secret')
    # remote_file_name = os.getenv('remote_file_name')
    local_file_name = os.getenv('local_file_name')
    
    # logging.info(f"Descargando el inventario desde {url}")

    try:
        # Autenticación
        # credentials = ClientCredential(client_id, client_secret)
        # ctx = ClientContext(url).with_credentials(credentials)

        # file_url = f'{folder_base_sharepoint}/{remote_file_name}'
        download_path = os.path.join(os.path.dirname(__file__), local_file_name)
        # if os.path.exists(download_path):
        #     os.remove(download_path)
 
        # # Obtener el archivo desde SharePoint
        # with open(download_path, "wb") as local_file:
        #     ctx.web.get_file_by_server_relative_url(file_url).download(local_file).execute_query()
        return download_path

    except Exception as e:
        logging.error(f"Error al descargar el archivo: {e}")
        print(json.dumps({"_meta": {"hostvars": {}}}))
        sys.exit(1)


def load_inventory_data(xlsx_file_path, sheet_name: str):
    logging.info(f"Cargando inventario desde {xlsx_file_path}")
    if not os.path.exists(xlsx_file_path):
        logging.error(f"Archivo {xlsx_file_path} no encontrado.")
        print(json.dumps({"_meta": {"hostvars": {}}}))
        sys.exit(1)

    try:
        df = pd.read_excel(xlsx_file_path, sheet_name=sheet_name)
        return df.to_dict(orient='records')
    except Exception as e:
        logging.error(f"Error al leer o parsear el archivo Excel: {e}")
        print(json.dumps({"_meta": {"hostvars": {}}}))
        sys.exit(1)

def return_valid_text(value):
    """Devuelve el valor si no es NaN, o 'None' en caso contrario."""
    return value if pd.notna(value) else None

def safe_get(value):
    """Devuelve el valor si no es NaN, reemplaza caracteres especiales y convierte a minúsculas."""
    if pd.notna(value):
        return unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('utf-8').strip().lower()
    return None

def add_host_to_group(group_dict, group_name, hostname):
    """Agrega un host al grupo correspondiente, creando el grupo si no existe."""
    if group_name not in group_dict:
        group_dict[group_name] = {'hosts': [], 'vars': {}}
    group_dict[group_name]['hosts'].append(hostname)

def build_inventory(inventory_data, so_filter_to_add):
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
        os_name = return_valid_text(inventory[constants.texts["so"]])
        hostname = return_valid_text(inventory['HostName'])
        operative_system = sanitize_group_name(inventory[constants.texts["so"]])
        stage = validate_lote_format(sanitize_group_name(inventory['Lote']))
        ipv4_address = return_valid_text(inventory["IPv4Address"])
        
        # Razones de exclusión
        if hostname in ansible_inventory['all']['hosts']:
            excluded_hosts.append({"HostName": hostname, "IPv4Address": ipv4_address, constants.texts["reason"]: "Hostname duplicado"})
            continue
        if not os_name:
            excluded_hosts.append({"HostName": hostname, "IPv4Address": ipv4_address, constants.texts["reason"]: "Campo de SO vacío"})
            continue
        if os_name not in so_filter_to_add:
            excluded_hosts.append({"HostName": hostname, "IPv4Address": ipv4_address, constants.texts["reason"]: "SO no agregado en el filtro servers_supported"})
            continue
        
        if os_name not in so_filter_to_add:
            continue
        
        # Add to OS counts
        if operative_system not in os_counts:
            os_counts[operative_system] = 0
        os_counts[operative_system] += 1

        # Añadir host a 'all'
        ansible_inventory['all']['hosts'].append(hostname)

        data_host = {
            'hostname': hostname,
            'os': return_valid_text(inventory[constants.texts["so"]]),
            'type_os': safe_get(inventory['TIPO SO']),
            'location': safe_get(inventory['UBICACIÓN']),
            'tipo_maquina': safe_get(inventory['Tipo Máquina']),
            'ancho_banda': safe_get(inventory["Ancho Banda"]),
            'ambiente': safe_get(inventory["Ambiente"]),
            'lote': validate_lote_format(return_valid_text(inventory["Lote"])),
            'crq': safe_get(inventory["CRQ"]),
            'ansible_host': ipv4_address,
            'tipo_vmware': safe_get(inventory["TIPO_VMWARE"]),
            'vcenter_vmware': safe_get(inventory["VCENTER_VMWARE"]),
            'datacenter_vmware': safe_get(inventory["DATACENTER_VMWARE"]),
            'vm_name': return_valid_text(inventory["VM_NAME"]),
            'azure_resource_group': return_valid_text(inventory["azure_resource_group"]),
        }
        # Agregar hostvars
        ansible_inventory['_meta']['hostvars'][hostname] = data_host
        imported_hosts.append(data_host)

        if stage:
            add_host_to_group(stage_groups, stage, hostname)
            stage_groups[stage]['vars'] = {
                'ansible_connection': 'winrm',
                'ansible_winrm_scheme': 'https',
                'ansible_winrm_message_encryption':  'auto',
                'ansible_winrm_transport': 'ntlm',
                'ansible_winrm_port': 5986,
                'ansible_winrm_server_cert_validation': 'ignore',
                'ansible_winrm_operation_timeout_sec': 600,
                'ansible_winrm_read_timeout_sec': 900,
                'ansible_winrm_connection_timeout': 900
            }

    ansible_inventory['_meta']['hostvars']['ansibleawx'] = {
        'ansible_host': '10.2.0.4'
    }
    # Actualizar el inventario con los grupos
    ansible_inventory.update(stage_groups)
    
    logging.info(f"{len(ansible_inventory['all']['hosts'])} registros guardados en inventario")
    logging.info(textwrap.dedent(f"""\
    Se han omitido {len(inventory_data) - len(ansible_inventory['all']['hosts'])} registros porque no cumplen
    con los criterios de filtrado para los sistemas operativos que requieren parches.
    Por favor, revisa los sistemas operativos en tu inventario para asegurarte de que estén alineados
    con los criterios establecidos."""))
    return ansible_inventory, os_counts, excluded_hosts, imported_hosts

def save_stats_to_excel(total_hosts, processed_hosts, so_filter_to_add, os_counts, excluded_hosts, imported_hosts):
    """Genera las estadísticas en un Excel en la carpeta local"""
    # Crear un nuevo archivo de Excel o cargar uno existente
    workbook = openpyxl.Workbook()
    
    # Hoja de estadísticas
    sheet = workbook.active
    sheet.title = "Inventario Estadísticas"
    
    # Datos de la tabla de estadísticas
    headers = ["Descripción", "Cantidad"]
    sheet.append(headers)
    # Aplicar negrilla a los encabezados
    for cell in sheet[1]:  # sheet[1] accede a la fila de encabezados
        cell.font = Font(bold=True)  # Aplicar la fuente en negrilla
    data = [
        ["Total Hosts", total_hosts],
        ["Hosts Omitidos", total_hosts - processed_hosts],
        ["Hosts en Inventario", processed_hosts]
    ]
    for row in data:
        sheet.append(row)

    # Crear un gráfico de barras para las estadísticas
    chart = BarChart()
    chart.title = "Estadísticas de Hosts"
    chart.x_axis.title = "Inventario"
    chart.y_axis.title = "Cantidad"
    
    # Referencias de datos y categorías para las etiquetas
    data_ref = Reference(sheet, min_col=2, min_row=2, max_row=4)  # Incluir todas las filas de datos (Total, Inventario, Omitidos)
    categories_ref = Reference(sheet, min_col=1, min_row=2, max_row=4)  # Descripciones (Total Hosts, Hosts en Inventario, Hosts Omitidos)
    
    # Añadir datos y categorías sin títulos automáticos
    chart.add_data(data_ref, titles_from_data=False)
    chart.set_categories(categories_ref)
    sheet.add_chart(chart, "E5")  # Ubicación del gráfico

    # Crear una nueva hoja para el filtro de SO con conteos
    sheet_so_filter = workbook.create_sheet(title="Filtro SO")
    sheet_so_filter.append(["Sistema Operativo", "Cantidad"])  # Encabezados
    # Aplicar negrilla a los encabezados
    for cell in sheet_so_filter[1]:  # sheet[1] accede a la fila de encabezados
        cell.font = Font(bold=True)  # Aplicar la fuente en negrilla

    # Agregar los sistemas operativos y sus conteos, solo si están en el filtro
    for os_type in so_filter_to_add:
        sanitized_os = sanitize_group_name(os_type)
        count = os_counts.get(sanitized_os, 0)  # Usar 0 si no está en os_counts
        sheet_so_filter.append([os_type, count])
        
    # Hoja de exclusiones
    sheet_exclusions = workbook.create_sheet(title="Host Excluidos")
    sheet_exclusions.append(["HostName", "IPv4Address", constants.texts["reason"]])
    # Aplicar negrilla a los encabezados
    for cell in sheet_exclusions[1]:  # sheet[1] accede a la fila de encabezados
        cell.font = Font(bold=True)  # Aplicar la fuente en negrilla
    
    for exclusion in excluded_hosts:
        sheet_exclusions.append([exclusion["HostName"], exclusion["IPv4Address"], exclusion[constants.texts["reason"]]])
        
    # Crear una hoja para los hosts importados
    sheet_imported_hosts = workbook.create_sheet(title="Hosts Importados")
    sheet_imported_hosts.append(["HostName", "IPv4Address", "CRQ", "Lote"])
    # Aplicar negrilla a los encabezados
    for cell in sheet_imported_hosts[1]:
        cell.font = Font(bold=True)

    for host in imported_hosts:
        hostname = host.get("hostname")
        ip = host.get("ip")
        crq = host.get("crq")
        lote = sanitize_group_name(host.get("lote"))
        sheet_imported_hosts.append([hostname, ip, crq, lote])

    # Guardar el archivo
    local_path = os.path.join(stats_dir, f'inventario_estadisticas_{sheet_local_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    workbook.save(local_path)
    logging.info(f"Estadísticas guardadas en {local_path}")
    return local_path

def main():
    try:
        logging.info(f"Ejecutando {os.path.basename(__file__)}")
        start_time = time.perf_counter()
        load_dotenv()
        logging.info("Cargando variables...")
        
        so_filter_to_add = filter_so.servers_supported
        local_path = download_inventory_file()
        normalizer_excel.execute(logging=logging)

        # Cargar los datos del inventario
        inventory_data = load_inventory_data(local_path, sheet_name=sheet_local_name)
        ansible_inventory, os_counts, excluded_hosts, imported_hosts = build_inventory(inventory_data, so_filter_to_add)

        # Guardar estadísticas
        total_hosts = len(inventory_data)
        processed_hosts = len(ansible_inventory['all']['hosts'])
        stats_file_path = save_stats_to_excel(total_hosts, processed_hosts, so_filter_to_add, os_counts, excluded_hosts, imported_hosts)
        
        # remote_stats_path = f'{os.getenv("folder_base_sharepoint")}/Archivos_Generados'
        # stats_remote_file = f'{remote_stats_path}/Estadisticas/'
        # log_remote_file = f'{remote_stats_path}/Logs/'
        
        # Subir el archivo de estadísticas al servidor
        # upload_to_sharepoint(stats_file_path, stats_remote_file)
        if os.path.exists(stats_file_path):
            os.remove(stats_file_path)
        

        elapsed_time = time.perf_counter() - start_time
        logging.info(f"Tiempo finalizado: {elapsed_time:.2f} segundos")
        
        # Subir el archivo de logs al servidor
        # upload_to_sharepoint(log_file, log_remote_file)

        # Imprimir el inventario en formato JSON para Ansible
        print(json.dumps(ansible_inventory, indent=4))

    except Exception as e:
        logging.error(f"Error al generar el inventario dinámico: {e}")
        print(json.dumps({"_meta": {"hostvars": {}}}))
        sys.exit(1)

if __name__ == "__main__":
    main()
