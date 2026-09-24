from flask_login import UserMixin

from . import models


class AdminUser(UserMixin):
    def __init__(self, row):
        self.id = str(row["id"])
        self.usuario = row["usuario"]
        self.rol = row["rol"]

    @property
    def es_superadmin(self):
        return self.rol == "superadmin"


def cargar_admin(admin_id):
    row = models.obtener_admin(admin_id)
    return AdminUser(row) if row else None
