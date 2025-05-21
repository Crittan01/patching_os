Role Name
=========

Este rol de Ansible se encarga de aplicar parches a los servidores objetivo de las familias RHEL, SUSE y Windows. El proceso de parchado incluye la validación previa, la ejecución del parchado y la validación posterior, asegurando que los servidores estén actualizados y funcionando correctamente.

Requirements
------------

Este rol requiere que los servidores objetivo estén configurados en Foreman y que el inventario dinámico esté correctamente asociado mediante los scripts de Python proporcionados. Además, se asume que los servidores están accesibles a través de SSH para Unix y WinRM para Windows.

Role Variables
--------------

parchado_log_dir: Directorio donde se almacenarán los logs del proceso de parchado.
owner: Propietario de los archivos generados.
group: Grupo de los archivos generados.
ansible_pwd: Contraseña encriptada para autenticación.
parchado_dir_reporte: Directorio donde se almacenarán los reportes de actualización para Windows.

Dependencies
------------

Este rol no tiene dependencias de otros roles de Ansible Galaxy, pero requiere que las credenciales y configuraciones estén correctamente definidas en vars/global.yml.

Example Playbook
----------------

Inicialización de Variables
Se inicializan las variables necesarias para el proceso de parchado, como los paquetes objetivo y el estado inicial de los paquetes.

Validación Previa
RHEL y SUSE: Se verifica el estado de los repositorios y se lista el contenido de los paquetes antes del parchado.
Windows: Se busca actualizaciones disponibles y se actualiza el estado de búsqueda.

Proceso de Parchado
RHEL: Se instalan los paquetes utilizando YUM o DNF según el gestor de paquetes disponible.
SUSE: Se actualizan los paquetes utilizando Zypper.
Windows: Se descargan e instalan las actualizaciones necesarias.

Validación Post-parchado
Se compara el listado de paquetes antes y después del parchado para identificar cambios.
Se genera un reporte JSON con los resultados del parchado.

Generación de Reporte JSON
Se crea un archivo JSON con los resultados del parchado, incluyendo el estado de cada chequeo realizado.

PLAYBOOK:

- name: Parchado de Servidores
  hosts: all
  gather_facts: true
  vars_files:
    - vars/global.yml
  roles:
    - role: parchado
      vars:
        owner: "iacolcoauto"
        group: "soporte"
        parchado_log_dir: "/var/log/ansible_patches"
  tasks:
    - name: Mostrar resultado del parchado
      debug:
        msg: "Parchado completado para {{ inventory_hostname }}"

License
-------

BSD

Author Information
------------------

Este rol fue desarrollado por el equipo de NTTDATA para Colcomercio.
