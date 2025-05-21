Role Name
=========

Generación de Informes Consolidados en CSV

Este rol de Ansible se encarga de generar informes consolidados en formato CSV para los servidores objetivo, categorizados por las familias de sistemas operativos RHEL, SUSE, y Windows. Estos informes son esenciales para el seguimiento y auditoría del proceso de parchado.

Requirements
------------

Este rol requiere que los servidores objetivo estén configurados en Foreman y que el inventario dinámico esté correctamente asociado mediante los scripts de Python proporcionados. Además, se asume que los servidores están accesibles a través de SSH para Unix y WinRM para Windows

Role Variables
--------------

log_dir: Directorio donde se almacenarán los logs de los parches.
owner: Propietario de los archivos generados.
group: Grupo de los archivos generados.
ansible_pwd: Contraseña encriptada para autenticación.
out_csv_name: Nombre base del archivo CSV generado.

Estas variables se pueden definir en defaults/main.yml, vars/main.yml, o pasarse como parámetros al rol.

Dependencies
------------

Este rol no tiene dependencias de otros roles de Ansible Galaxy, pero requiere que las credenciales y configuraciones estén correctamente definidas en vars/global.yml.

Example Playbook
----------------

Creación del Archivo CSV y Encabezado
Se crea un archivo CSV en el directorio especificado, con un encabezado que incluye columnas para CRQ, Lote, Hostname, IP, Distribución, Fecha, Repositorio Fuente, Cantidad de Paquetes, Paquetes Eliminados, Paquetes Instalados, Punto de Fallo, y Estado Final.

Escribir Columnas del CSV
Se añaden filas al archivo CSV con la información recopilada de cada servidor, utilizando los resultados de las validaciones y el proceso de parchado.

Generación de CSV por Familia de SO
Se generan archivos CSV específicos para cada familia de sistemas operativos (RHEL, SUSE, Windows), incluyendo solo los servidores que pertenecen a cada categoría.

Example Playbook
- name: Generación de Informes Consolidados en CSV
  hosts: all
  gather_facts: true
  vars_files:
    - vars/global.yml
  roles:
    - role: out_csv
      vars:
        owner: "iacolcoauto"
        group: "soporte"
        log_dir: "/var/log/ansible_patches"
        out_csv_name: "consolidado"
  tasks:
    - name: Mostrar resultado de generación de CSV
      debug:
        msg: "CSV generado para {{ inventory_hostname }}"

License
-------

BSD

Author Information
------------------

Este rol fue desarrollado por el equipo de NTTDATA para Colcomercio.
