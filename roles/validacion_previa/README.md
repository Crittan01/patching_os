Role Name
=========

Este rol de Ansible se encarga de realizar validaciones previas en los servidores objetivo antes de aplicar parches. Las validaciones aseguran que los servidores cumplan con los requisitos necesarios para proceder con el parchado, verificando aspectos como espacio en disco, estado de reinicio y servicios activos.

Requirements
------------

Este rol requiere que los servidores objetivo estén configurados en Foreman y que el inventario dinámico esté correctamente asociado mediante los scripts de Python proporcionados. Además, se asume que los servidores están accesibles a través de SSH para Unix y WinRM para Windows.

Role Variables
--------------

- validacion_previa_log_dir: Directorio donde se almacenarán los logs de validación.
- owner: Propietario de los archivos generados.
- group: Grupo de los archivos generados.
- ansible_pwd: Contraseña encriptada para autenticación.
- validacion_previa_fs_space_requirements: Requisitos mínimos de espacio por filesystem.

Estas variables se pueden definir en defaults/main.yml, vars/main.yml, o pasarse como parámetros al rol.

Dependencies
------------

Este rol no tiene dependencias de otros roles de Ansible Galaxy, pero requiere que las credenciales y configuraciones estén correctamente definidas en vars/global.yml.

Example Playbook
----------------

Tasks Overview
1. Inicialización de Variables
Se inicializan las variables necesarias para la validación, como el estado de reinicio (Windows), espacio en disco, y servicios.
2. Validación de Reinicio
Verificar estado de reinicio: Comprueba si un reinicio está pendiente (Windows).
Ejecutar reinicio si está pendiente: Reinicia el servidor si es necesario, con tiempos de espera configurados (Windows).
3. Validación de Espacio en Disco
Obtener Información de Discos: Recopila datos sobre las particiones de disco.
Calcular espacio Libre: Calcula el espacio libre y total en la unidad especificada.
Validar espacio disponible: Verifica si el espacio libre cumple con el umbral requerido.
4. Validación de Servicios
Obtener listado de Servicios: Recopila información sobre los servicios en ejecución.
Crear lista de servicios a monitorear: Filtra los servicios que deben estar activos.
5. Generación de Reporte JSON
Crea un archivo JSON con los resultados de la validación, incluyendo el estado de cada chequeo realizado.

PLAYBOOK:
- name: Validación Previa de Servidores
  hosts: all
  gather_facts: true
  vars_files:
    - vars/global.yml
  roles:
    - role: validacion_previa
      vars:
        owner: "iacolcoauto"
        group: "soporte"
        validacion_previa_log_dir: "/var/log/ansible_patches"
  tasks:
    - name: Mostrar resultado de validaciones
      debug:
        msg: "Validaciones completadas para {{ inventory_hostname }}"

License
-------

BSD

Author Information
------------------

Este rol fue desarrollado por el equipo de NTTDATA para Colcomercio
