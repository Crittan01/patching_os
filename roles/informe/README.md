Role Name
=========

Este rol de Ansible se encarga de generar informes detallados sobre el estado de los servidores objetivo después de aplicar parches. Los informes incluyen información sobre el sistema operativo, validaciones previas y posteriores, estado del snapshot, configuración del repositorio y detalles del parchado.

Requirements
------------

Este rol requiere que los servidores objetivo estén configurados en Foreman y que el inventario dinámico esté correctamente asociado mediante los scripts de Python proporcionados. Además, se asume que los servidores están accesibles a través de SSH para Unix y WinRM para Windows. Los servidores objetivo son RHEL, SUSE y Windows

Role Variables
--------------

log_dir: Directorio donde se almacenarán los informes generados.
owner: Propietario de los archivos generados.
group: Grupo de los archivos generados.
ansible_pwd: Contraseña encriptada para autenticación.
server_informes: Servidor donde se almacenan los informes.

Estas variables se pueden definir en defaults/main.yml, vars/main.yml, o pasarse como parámetros al rol.

Dependencies
------------

Este rol no tiene dependencias de otros roles de Ansible Galaxy, pero requiere que las credenciales y configuraciones estén correctamente definidas en vars/global.yml.

Example Playbook
----------------

Preparar Contenido del Informe
Se establece el contenido del informe basado en los resultados de las validaciones y el proceso de parchado.
Se incluyen detalles como el estado del sistema operativo, espacio en disco, servicios, y resultados de las actualizaciones.

Generar Informe
Se copia el contenido del informe a un archivo en el directorio especificado, asegurando que el propietario y el grupo sean correctos.
Se utiliza el servidor de informes configurado para almacenar los archivos generados.

Mostrar Informe en Consola
Se muestra el contenido del informe en la consola para verificación rápida.

Example Playbook
- name: Generación de Informe de Servidores
  hosts: all
  gather_facts: true
  vars_files:
    - vars/global.yml
  roles:
    - role: informe
      vars:
        owner: "iacolcoauto"
        group: "soporte"
        log_dir: "/var/log/ansible_patches"
  tasks:
    - name: Mostrar resultado de generación de informe
      debug:
        msg: "Informe generado para {{ inventory_hostname }}"

License
-------

BSD

Author Information
------------------

Este rol fue desarrollado por el equipo de NTTDATA para Colcomercio
