Role Name
=========

Este rol de Ansible gestiona la creación, cancelación y omisión de snapshots en máquinas virtuales (VM) que operan bajo entornos VMware, tanto en configuraciones standalone como en vCenter. Este proceso es crucial para asegurar que se pueda revertir a un estado anterior en caso de que un parcheo falle

Requirements
------------

Los servidores objetivo deben estar configurados en Foreman (Familia RedHat, SUSE).
El inventario dinámico debe estar correctamente asociado mediante los scripts de Python proporcionados.
Acceso SSH para servidores Unix y credenciales válidas para VMware.
Los servidores deben ser accesibles y configurados correctamente.

Role Variables
--------------

snapshot_log_dir: Directorio donde se almacenarán los logs de snapshot.
owner: Propietario de los archivos generados.
group: Grupo de los archivos generados.
ansible_pwd: Contraseña encriptada para autenticación.
vcenter_credentials: Credenciales para acceso a vCenter.
esxi_credentials: Credenciales para acceso a servidores ESXi.

Estas variables se pueden definir en defaults/main.yml, vars/main.yml, o pasarse como parámetros al rol.

Dependencies
------------

Este rol no tiene dependencias de otros roles de Ansible Galaxy, pero requiere que las credenciales y configuraciones estén correctamente definidas en vars/global.yml.

Example Playbook
----------------

Inicialización de Variables
Se inicializan variables por defecto necesarias para la operación de snapshot, como snapshot_name, snapshot_description, y detalles de conexión.

Validación de Configuración
Se valida la configuración del entorno VMware para asegurar que las credenciales y el tipo de VMware sean correctos.

Verificación de Conectividad
Se verifica la conectividad SSH a los servidores ESXi para asegurar que las credenciales sean válidas.

Creación de Snapshot
Dependiendo del tipo de VMware (standalone o vCenter), se ejecutan tareas específicas para crear snapshots en las VMs.

Cancelación y Omisión de Snapshot
Se manejan casos donde la creación de snapshots no es necesaria o debe ser cancelada debido a configuraciones incorrectas o servidores físicos.

Generación de Reporte JSON
Se crea un archivo JSON con los resultados de la operación de snapshot, incluyendo detalles de errores si los hubiera.

License
-------

BSD

Author Information
------------------

Este rol fue desarrollado por el equipo de NTTDATA para Colcomercio.
