# Servidor Autoorigen

**Entorno actual:** Debian 13 "Trixie" nativo en torre ASUS. Usuario y hostname: `autoorigen`.

`guia-servidor-virtualbox-historial.md` es la guía original cuando el servidor iba a ser una máquina virtual en VirtualBox. Se conserva como historial; los pasos de Linux (apt, venv, Flask, ufw) siguen aplicando igual.

## Hecho
- Debian 13 instalado con GNOME
- Usuario `autoorigen` agregado al grupo sudo
- Instalados: git, curl, ufw, python3-venv, python3-pip

## Pendiente
- Clonar este repositorio en la torre
- Entorno virtual + Flask en red local (puerto 5000)
- Firewall (ufw)
- Producción: Gunicorn + systemd, Nginx, salida a internet, dominio y SSL
