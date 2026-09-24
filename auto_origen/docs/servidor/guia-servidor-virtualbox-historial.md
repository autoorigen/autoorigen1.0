# Guía: servidor propio de Autoorigen en VirtualBox

Guía interactiva publicada (con checklist de progreso): https://claude.ai/code/artifact/f1123407-f656-478b-b739-78b442b38913

## Decisión final: Debian 13 ("Trixie"), no Ubuntu

Se intentó primero con Ubuntu Desktop 26.04.1 LTS, pero la descarga de la ISO (~5.9 GB) falló repetidamente (ISO corrupta/incompleta, error de arranque "invalid magic number" en GRUB). Se cambió a **Debian 13**, cuya imagen de instalación "netinst" pesa ~700 MB y descarga el resto de paquetes (incluido el escritorio) durante la instalación — mucho más resistente a conexiones inestables. Debian se administra igual que Ubuntu (mismo `apt`, `systemctl`), así que el resto del plan no cambió.

Ventaja adicional de Debian sobre Ubuntu Desktop: en la pantalla de selección de software (tasksel) se puede marcar **escritorio GNOME y servidor SSH al mismo tiempo**, evitando el paso extra de instalar OpenSSH a mano que sí hacía falta en Ubuntu Desktop.

## Resumen del plan

Objetivo: montar una VM de Debian 13 (con escritorio GNOME) en VirtualBox que sirva la app de Flask (`app.py` + `requirements.txt` + `autoorigen-v1-unico-movil.html`) dentro de la red local, como base para más adelante exponerla con dominio y hosting propios.

Pasos cubiertos en la guía:
1. Descargar la imagen netinst de Debian 13 amd64 desde debian.org (o cdimage.debian.org/debian-cd/current/amd64/iso-cd/).
2. Crear la VM en VirtualBox: 4–8 GB RAM, 2–4 CPU, 25–40 GB disco dinámico, 128 MB de video + aceleración 3D, adaptador de red en modo puente (Bridged).
3. Instalar con "Graphical install": idioma/ubicación/teclado, hostname, contraseña de root en blanco (para que el usuario normal tenga sudo), usuario normal, particionado guiado de disco completo, mirror por defecto, y en tasksel marcar "Debian desktop environment" + "GNOME" + "servidor SSH".
4. Primer arranque: `apt update && apt full-upgrade`, instalar `git curl ufw build-essential python3-venv python3-pip`; Guest Additions de VirtualBox (requiere `dkms linux-headers-$(uname -r)` primero).
5. Red: obtener la IP de la VM con `ip a` (modo puente le da IP propia en la LAN).
6. Conectarse por SSH desde el equipo anfitrión (`ssh usuario@ip`).
7. Traer el proyecto (git clone o scp) y crear entorno virtual + `pip install -r requirements.txt`.
8. Probar la app: `flask --app app run --host=0.0.0.0 --port=5000` (el `app.run(debug=True)` original solo escucha en localhost), abrir puerto 5000 en `ufw`.
9. Tomar una instantánea de VirtualBox ("base-debian-instalado") antes de seguir configurando.
10. Próximos pasos (pendientes, para cuando se quiera exponer con dominio propio): Gunicorn + systemd, Nginx como reverse proxy, salida a internet (reenvío de puertos o Cloudflare Tunnel si hay CGNAT), DNS + certificado SSL (Let's Encrypt).

Estado actual (2026-09-06): el usuario va a descargar la ISO netinst de Debian 13 y recrear la VM desde cero (la VM anterior con Ubuntu se eliminó por problemas de descarga).
