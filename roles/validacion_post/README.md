Role Name
=========

Este rol de Ansible se encarga de realizar validaciones posteriores en los servidores objetivo después de aplicar parches. Las validaciones aseguran que los servidores estén en un estado óptimo tras el parchado, verificando aspectos como el estado de los servicios y la necesidad de reinicios.

Requirements
------------

Este rol requiere que los servidores objetivo estén configurados en Foreman y que el inventario dinámico esté correctamente asociado mediante los scripts de Python proporcionados. Además, se asume que los servidores están accesibles a través de SSH para Unix y WinRM para Windows.


Role Variables
--------------

- validacion_post_log_dir: Directorio donde se almacenarán los logs de validación.
- owner: Propietario de los archivos generados.
- group: Grupo de los archivos generados.
- ansible_pwd: Contraseña encriptada para autenticación.
- previous_results: Resultados de validaciones previas, utilizados para comparación.
- services_info: Información sobre el estado de los servicios antes y después del parchado.

Estas variables se pueden definir en defaults/main.ym, vars/main.yml, o pasarse como parámetros al rol.

Dependencies
------------

Este rol no tiene dependencias de otros roles de Ansible Galaxy, pero requiere que las credenciales y configuraciones estén correctamente definidas en vars/global.yml.

Example Playbook
----------------

1. Inicialización de Variables
   - Se inicializan las variables necesarias para la validación, como el estado de los servicios y los resultados previos.

2. Decodificación de Resultados Previos
   - Se decodifican los resultados del parchado anterior para su uso en validaciones posteriores.

3. Validación de Servicios
   - Validar servicios críticos: Se recopila información sobre los servicios en ejecución.
   - Analizar cambios en servicios: Se comparan los servicios activos antes y después del parchado.
   - Intentar recuperación de servicios: Se intenta reiniciar servicios que se detuvieron inesperadamente.

4. Validación de Reinicio (solo para Windows)
   - Verificar si un reinicio está pendiente y ejecutarlo si es necesario.

5. Generación de Reporte JSON
   - Se crea un archivo JSON con los resultados de la validación, incluyendo el estado de cada chequeo realizado.

Example Playbook
----------------

- name: Validación Post de Servidores
  hosts: all
  gather_facts: true
  vars_files:
    - vars/global.yml
  roles:
    - role: validacion_post
      vars:
        owner: "iacolcoauto"
        group: "soporte"
        validacion_post_log_dir: "/var/log/ansible_patches"
  tasks:
    - name: Mostrar resultado de validaciones
      debug:
        msg: "Validaciones post-parchado completadas para {{ inventory_hostname }}"

License
-------

BSD

Author Information
------------------

Este rol fue desarrollado por el equipo de NTTDATA para Colcomercio.