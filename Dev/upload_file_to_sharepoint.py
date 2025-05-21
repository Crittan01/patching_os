from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from dotenv import load_dotenv
import os

load_dotenv()

def upload_to_sharepoint(local_path):
    """
    Subir un archivo a SharePoint desde una ruta local a una ruta remota dada en SharePoint.
    
    Args:
        local_path (str): La ruta local del archivo a subir.
        remote_path (str): La ruta remota donde se guardará el archivo en SharePoint.
    """
    url = os.getenv('url_sharepoint')  # URL del sitio de SharePoint
    client_id = os.getenv('client_id')  # ID del cliente para la autenticación
    client_secret = os.getenv('client_secret')  # Secreto del cliente para la autenticación
    remote_base_path = f'{os.getenv("folder_base_sharepoint")}/Archivos_Generados'
    remote_path = f'{remote_base_path}/Logs_CRQ/'
    
    print(f"Subiendo archivo {local_path} a SharePoint en {remote_path}")
    
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
            
        return file.serverRelativeUrl
        
    except Exception as e:
        print(f"Error al subir el archivo: {e}")
