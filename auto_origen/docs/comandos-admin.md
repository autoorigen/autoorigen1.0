# Comandos y rutas del administrador — Autoorigen

Referencia rápida de lo que usa quien administra el taller: comandos de
terminal (se corren una sola vez o de vez en cuando) y las rutas del panel
web `/admin` (se usan todos los días).

## Comandos de terminal

Se corren desde la raíz del proyecto (`auto_origen/`), con el entorno
virtual activado.

| Comando | Para qué |
|---|---|
| `python app.py` | Arranca el servidor (web + Socket.IO). |
| `flask --app app crear-admin <usuario> <password>` | Crea un admin nuevo, o le cambia la contraseña si ya existe. El **primero** que se crea en todo el sistema queda automáticamente como **superadmin**. |
| `flask --app app crear-admin <usuario> <password> --superadmin` | Crea un admin adicional que también sea superadmin. |
| `flask --app app crear-tecnico <usuario> <password> "<Nombre>"` | Crea (o le cambia la contraseña a) un mecánico con acceso a la app/web de inspecciones. |
| `pip install -r requirements.txt` | Instala o actualiza las dependencias del proyecto. |

### Roles

- **admin**: puede gestionar clientes, vehículos, citas y órdenes.
- **superadmin**: además puede aprobar/rechazar informes, crear otros
  admins, crear mecánicos y generar tokens para la futura app iOS.

## Rutas del panel (`/admin`)

| Ruta | Para qué | Quién |
|---|---|---|
| `/admin/login` | Entrar al panel. | admin |
| `/admin` | Resumen: clientes, vehículos, citas pendientes, órdenes activas. | admin |
| `/admin/clientes` | Crear, editar y eliminar clientes. | admin |
| `/admin/vehiculos` | Crear vehículos y ver el código de acceso de cada uno. | admin |
| `/admin/vehiculos/<id>` | Ficha del carro: código de acceso, botón "Enviar por WhatsApp", regenerar código, crear una nueva orden. | admin |
| `/admin/ordenes/<id>` | Cambiar la etapa del carro (dispara los informes con IA), agregar eventos a la línea de tiempo, regenerar el informe final. | admin |
| `/admin/citas` | Ver y cambiar el estado de las citas agendadas desde la web. | admin |
| `/admin/informes` | Aprobar o rechazar los informes finales antes de que le lleguen al cliente. | **superadmin** |
| `/admin/usuarios` | Crear otros usuarios admin. | **superadmin** |
| `/admin/mecanicos` | Crear mecánicos desde la web (alternativa a `crear-tecnico`). | **superadmin** |
| `/admin/api-tokens` | Generar tokens de dispositivo para cuando exista la app iOS. | **superadmin** |

## Notas relacionadas

- Los informes preliminar y final los genera la IA sola (Ollama, local) al
  cambiar la etapa de una orden — ver `autoorigen/ia.py`.
- El código de acceso de cada vehículo es aleatorio y se genera solo al
  crear el vehículo — ver `autoorigen/models.py::generar_codigo_acceso`.
- Manual paso a paso para el técnico (no el admin): documento aparte
  publicado como artifact — "Manual del técnico".
