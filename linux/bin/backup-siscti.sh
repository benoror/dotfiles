#!/bin/bash
# Ejecuta el siguiente comando.
# Primerpo lo haces ejecutable con chmod +x backup-siscti.sh
# Luego lo mueves a /usr/bin o una ruta en el PATH, sudo mv backup-siscti.sh /usr/bin/
cp /ruta/al/archivo.tar.gz /destino/backup-siscti-$(date +%F-%b).bak
