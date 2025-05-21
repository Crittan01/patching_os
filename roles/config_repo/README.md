Role Name
=========

Configurar Repositorios

Este rol de Ansible se encarga de configurar los repositorios de paquetes en los servidores objetivo de las familias RHEL, SUSE y validacion Repo Windows. Se asegura de que los repositorios estén correctamente configurados y accesibles antes de proceder con otras operaciones de gestión de parches.

Requirements
------------

Este rol requiere que los servidores objetivo estén configurados en Foreman y que el inventario dinámico esté correctamente asociado mediante los scripts de Python proporcionados. Además, se asume que los servidores están accesibles a través de SSH para Unix y WinRM para Windows.

Role Variables
--------------

config_repo_log_dir: Directorio donde se almacenarán los logs de configuración de repositorios.
owner: Propietario de los archivos generados.
group: Grupo de los archivos generados.
ansible_pwd: Contraseña encriptada para autenticación.
config_repo_repos_config: Diccionario que contiene las configuraciones de URL de los repositorios para diferentes distribuciones y versiones.

Estas variables se pueden definir en defaults/main.yml, vars/main.yml, o pasarse como parámetros al rol.

Dependencies
------------

Este rol no tiene dependencias de otros roles de Ansible Galaxy, pero requiere que las credenciales y configuraciones estén correctamente definidas en vars/global.yml.

Example Playbook
----------------

Inicialización de Variables
Se inicializan las variables necesarias para la configuración de los repositorios, como repo_states, repos_creados, y repo_error.

Verificación de Repositorios
Acceso al Servidor de Repositorios: Se valida la conectividad con el servidor de repositorios configurado en Foreman.
Gestión de Repos Existentes: Se listan y respaldan los repositorios existentes antes de realizar cualquier cambio.

Configuración de Nuevos Repositorios
Obtención de URLs de Repositorios: Se obtienen las URLs de los repositorios necesarios según la distribución y versión del sistema operativo.
Verificación de Repositorios: Se verifica el acceso a cada repositorio mediante una solicitud HTTP.
Añadir Repositorios Locales: Se configuran los repositorios locales en el sistema, asegurando que estén habilitados y accesibles.

Generación de Reporte JSON
Se genera un archivo JSON con los resultados de la configuración, incluyendo el estado de cada repositorio configurado.

Example Playbook
- name: Configuración de Repositorios en Servidores
  hosts: all
  gather_facts: true
  vars_files:
    - vars/global.yml
  roles:
    - role: config_repo
      vars:
        owner: "iacolcoauto"
        group: "soporte"
        config_repo_log_dir: "/var/log/ansible_patches"
  tasks:
    - name: Mostrar resultado de configuración
      debug:
        msg: "Configuración completada para {{ inventory_hostname }}"

License
-------

BSD

Author Information
------------------

Este rol fue desarrollado por el equipo de NTTDATA para Colcomercio.
