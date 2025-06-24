from django.contrib import admin
from .models import (
    Usuario, Afiliacion, Convenio, Beneficio, Chatbot,
    ContactoPrincipal, Credencial, Documento, Empresa,
    EmpresaConvenio, Estadistica, Notificacion, Servicio,
    Reserva, Recibo, ServicioProveedor, SolicitudVida
)

admin.site.register(Usuario)
admin.site.register(Afiliacion)
admin.site.register(Convenio)
admin.site.register(Beneficio)
admin.site.register(Chatbot)
admin.site.register(ContactoPrincipal)
admin.site.register(Credencial)
admin.site.register(Documento)
admin.site.register(Empresa)
admin.site.register(EmpresaConvenio)
admin.site.register(Estadistica)
admin.site.register(Notificacion)
admin.site.register(Servicio)
admin.site.register(Reserva)
admin.site.register(Recibo)
admin.site.register(ServicioProveedor)
admin.site.register(SolicitudVida)
