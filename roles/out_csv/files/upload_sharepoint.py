#!/usr/bin/env python3
import os
import logging
import json
import sys
import argparse
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

def setup_logging():
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )

def get_args():
   parser = argparse.ArgumentParser()
   parser.add_argument('--file-path', required=True, help='Local zip file path')  
   parser.add_argument('--tenant-id', required=True)
   parser.add_argument('--client-id', required=True)
   parser.add_argument('--client-secret', required=True)
   parser.add_argument('--sharepoint-url', required=True)
   parser.add_argument('--sharepoint-folder', required=True)
   return parser.parse_args()

def upload_to_sharepoint(file_path, sp_url, sp_folder, client_id, client_secret):
   try:
       credentials = ClientCredential(client_id, client_secret)
       ctx = ClientContext(sp_url).with_credentials(credentials)
       folder = ctx.web.get_folder_by_server_relative_url(sp_folder)

       with open(file_path, "rb") as file_content:
           file_name = os.path.basename(file_path)
           file = folder.upload_file(file_name, file_content).execute_query()
           
       result = {
           'success': True,
           'file_name': file_name,
           'url': file.serverRelativeUrl
       }
       
   except Exception as e:
       result = {
           'success': False,
           'error': str(e)
       }
       logging.error(f"Upload failed: {e}")
       
   return result

def main():
   setup_logging()
   args = get_args()
   
   if not os.path.exists(args.file_path):
       print(json.dumps({'success': False, 'error': 'File not found'}))
       sys.exit(1)

   result = upload_to_sharepoint(
       args.file_path,
       args.sharepoint_url,
       args.sharepoint_folder,
       args.client_id, 
       args.client_secret
   )
   
   print(json.dumps(result))
   sys.exit(0 if result['success'] else 1)

if __name__ == '__main__':
   main()
