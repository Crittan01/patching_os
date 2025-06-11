# #!/usr/bin/env python3
# import unicodedata
# import pandas as pd
# import re


# def return_valid_text(value):
#     """Devuelve el valor si no es NaN, o 'None' en caso contrario."""
#     return value if pd.notna(value) else None

# def safe_get(value):
#     """Devuelve el valor si no es NaN, reemplaza caracteres especiales y convierte a minúsculas."""
#     if pd.notna(value):
#         return unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('utf-8').strip().lower()
#     return None

# def sanitize_group_name(group_name):
#     """ 
#     Reemplazar caracteres no permitidos en los nombres de los grupos.
#     - Elimina tildes y acentos.
#     - Sustituye cualquier carácter que no sea alfanumérico, guion o guion bajo por guion bajo.
#     """
#     if not pd.notna(group_name) or not group_name:
#         return "Sin lote"
    
#     normalized_name = unicodedata.normalize('NFKD', group_name)
#     normalized_name = "".join([c for c in normalized_name if not unicodedata.combining(c)])
    
#     # Reemplazar caracteres no alfanuméricos por guión bajo y eliminar dobles guiones bajos
#     return re.sub(r'[_-]+', '_', re.sub(r'[^A-Za-z0-9_-]', '_', normalized_name.strip().lower()))

# def add_host_to_group(group_dict, group_name, hostname):
#     """Agrega un host al grupo correspondiente, creando el grupo si no existe."""
#     if group_name not in group_dict:
#         group_dict[group_name] = {'hosts': []}
#     group_dict[group_name]['hosts'].append(hostname)
    
# def validate_json(field, json_data):
#     if field not in json_data:
#         return ''
#     return json_data[field]
