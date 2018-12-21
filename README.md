# Buildout base para proyectos con OpenERP y PostgreSQL
OpenERP master en el base, PostgreSQL 9.3.4 y Supervisord 3.0
- Buildout crea cron para iniciar Supervisord después de reiniciar (esto no lo he probado)
- Supervisor ejecuta PostgreSQL, más info http://supervisord.org/
- También ejecuta la instancia de PostgreSQL
- Si existe un archivo dump.sql, el sistema generará la base de datos con ese dump
- Si existe  un archivo frozen.cfg es el que se debeía usar ya que contiene las revisiones aprobadas
- PostgreSQL se compila y corre bajo el usuario user (no es necesario loguearse como root), se habilita al autentificación "trust" para conexiones locales. Más info en more http://www.postgresql.org/docs/9.3/static/auth-methods.html
- Existen plantillas para los archivo de configuración de Postgres que se pueden modificar para cada proyecto.


# Uso (adaptado)
En caso de no haberse hecho antes en la máquina en la que se vaya a realizar, instalar las dependencias que mar Anybox
- Añadir el repo a /etc/apt/sources.list:
```
$ deb http://apt.anybox.fr/openerp common main
```
- Para firmar el repositorio
```
$ wget http://apt.anybox.fr/openerp/pool/main/a/anybox-keyring/anybox-keyring_0.2_all.deb
$ sudo dpkg -i anybox-keyring_0.2_all.deb
```
- Actualizar e instalar
```
$ sudo apt-get update
$ sudo apt-get install openerp-server-system-build-deps
```
- Para poder compilar e instalar postgres (debemos valorar si queremos hacerlo siempre), es necesario instalar el siguiente paquete (no e sla solución ideal, debería poder hacerlo el propio buildout, pero de momento queda así)
```
$ sudo apt-get install libreadline-dev
$ sudo apt-get install libcairo2-dev
$ sudo apt-get install libffi-dev
$ sudo apt-get install libpq-dev
$ sudo apt-get install libsasl2-dev
$ sudo apt-get install libldap2-dev
```
- Descargar el  repositorio de buildouts :
```
```
- Crear un virtualenv dentro de la carpeta del respositorio. Esto podría ser opcional, obligatorio para desarrollo o servidor de pruebas, tal vez podríamos no hacerlo para un despliegue en producción. Si no está instalado, instalar el paquete de virtualenv
```
$ sudo apt-get install python-virtualenv
$ cd <ubicacion_local_repo>
$ virtualenv sandbox --no-setuptools
```
- Ahora procedemos a ejecutar el buildout en nuestro entorno virtual
```
$ sandbox/bin/python bootstrap.py -c <configuracion_elegida>
```
- Lanzar el buildout
```
$ bin/buildout -c <configuracion_elegida>
```
- Urls
- Supervisor : http://localhost:9001
- Odoo: http://localhost:8069

- Instalar libreoffice y aero_docs
- https://github.com/aeroo/aeroo_docs/wiki/Installation-example-for-Ubuntu-14.04-LTS
```
$ apt-get install libreoffice-core --no-install-recommends
```

## Configurar OpenERP
Archivo de configuración: etc/openerp.cfg, si sequieren cambiar opciones en  openerp.cfg, no se debe editar el fichero,
si no añadirlas a la sección [openerp] del buildout.cfg
y establecer esas opciones .'add_option' = value, donde 'add_option'  y ejecutar buildout otra vez.

Por ejmplo: cambiar el nivel de logging de OpenERP
```
'buildout.cfg'
...
[openerp]
options.log_handler = [':ERROR']
...
```

Si se quiere jeecutar más de una instancia de OpenERP, se deben cambiar los puertos,
please change ports:
```
openerp_xmlrpc_port = 8069  (8069 default openerp)
openerp_xmlrpcs_port = 8071 (8071 default openerp)
supervisor_port = 9002      (9001 default supervisord)
postgres_port = 5434        (5432 default postgres)
```

# TODO
- Generar Apache and Nginx config for virualhost with Buildout

# TROUBLESHOOT
- Si falla con que no encuentra cairo importando el cairoplot, entrar en el fichero cairplot.py y cambiar import cairo por impor import cairocffi as cairo

# Contributors

## Creators

Rastislav Kober, http://www.kybi.sk
