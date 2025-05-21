Proyecto de Parchado de Servidores
=========
Descripción
=========

Este proyecto tiene como objetivo automatizar el proceso de parchado de servidores de las familias RHEL (incluyendo CentOS y Oracle Linux), SLES, y terminales POS SLED y Windows Server. La automatización se realiza utilizando Ansible, ejecutado a través de AWX sobre un clúster K3s. El proyecto está diseñado para asegurar que los servidores estén actualizados con los últimos parches de seguridad y mejoras, minimizando el tiempo de inactividad y asegurando la continuidad del negocio.

Arquitectura
=========
El sistema está compuesto por varias fases que se ejecutan secuencialmente para asegurar un parchado exitoso:

Validación Previa: Verifica que los servidores cumplan con los requisitos necesarios antes de aplicar parches, como espacio en disco y estado de reinicio.
Creación de Snapshot: Crea un snapshot de la máquina virtual para permitir la recuperación en caso de fallos durante el parchado.
Configuración del Repositorio: Configura los repositorios de paquetes necesarios para el parchado.
Parchado: Aplica los parches a los servidores.
Validación Post-Parchado: Verifica que los servidores estén en un estado correcto después del parchado.
Generación de Informe: Crea un informe detallado del proceso de parchado.

Requisitos
=========
Foreman: Los servidores Unix deben estar configurados en Foreman para la gestión de repositorios.
AWX: Utilizado para orquestar la ejecución de los playbooks de Ansible.
K3s: Clúster ligero de Kubernetes para ejecutar AWX.
Inventario Dinámico: Los inventarios se gestionan mediante scripts de Python que leen archivos Excel.

Estructura del Proyecto
=========
El proyecto está organizado en directorios y archivos que facilitan la gestión y ejecución de las diferentes fases del parchado:

roles/: Contiene los roles de Ansible que definen las tareas específicas para cada fase del parchado.
vars/: Archivos de variables globales y específicas del proyecto.
playbooks: Archivos YAML que definen las secuencias de ejecución de las tareas.
Dev/: Scripts de Python para la gestión del inventario y otras utilidades.

Uso
=========
Para ejecutar el proceso de parchado, sigue estos pasos:

Configura el Inventario: Asegúrate de que los scripts de inventario están actualizados y apuntan a los archivos Excel correctos.
Ejecuta los Playbooks: Utiliza AWX para ejecutar los playbooks en el orden correcto, comenzando por 1_validacion_previa.yml.
Revisa los Informes: Después de la ejecución, revisa los informes generados para verificar el estado de los servidores.

Contribuciones
=========
Este proyecto está abierto a contribuciones. Si deseas colaborar, por favor sigue las pautas de contribución y asegúrate de que tus cambios son consistentes con el estilo y la estructura del proyecto.

Licencia
=========
Este proyecto está licenciado bajo la licencia BSD. Consulta el archivo LICENSE para más detalles.

Información de Contacto
=========
Este proyecto fue desarrollado por el equipo de NTTDATA para Colcomercio.