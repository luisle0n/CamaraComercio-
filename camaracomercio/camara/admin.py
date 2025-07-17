from django.contrib import admin
from .models import Usuario, AfiliacionNatural, AfiliacionJuridica, Empresa, Servicio, Convenio, Beneficio, Chatbot, ContactoPrincipal, Credencial, Documento, EmpresaConvenio, Estadistica, Notificacion, Reserva, Recibo, ServicioProveedor, SolicitudVida

# Registra todos los modelos excepto los que ya tienen @admin.register decorador
admin.site.register(Usuario)
admin.site.register(AfiliacionNatural)
admin.site.register(AfiliacionJuridica)
admin.site.register(Empresa)
admin.site.register(Beneficio)
admin.site.register(Chatbot)
admin.site.register(ContactoPrincipal)
admin.site.register(Credencial)
admin.site.register(Documento)
admin.site.register(EmpresaConvenio)
admin.site.register(Estadistica)
admin.site.register(Notificacion)
admin.site.register(Reserva)
admin.site.register(Recibo)
admin.site.register(SolicitudVida)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    pass

@admin.register(ServicioProveedor)
class ServicioProveedorAdmin(admin.ModelAdmin):
    pass

@admin.register(Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_fin', 'imagen_tag')
    readonly_fields = ('imagen_tag',)
    fields = ('nombre', 'descripcion', 'imagen', 'imagen_tag', 'fecha_fin')

    def imagen_tag(self, obj):
        if obj.imagen:
            return f'<img src="{obj.imagen.url}" style="max-height:100px;"/>'
        return "-"
    imagen_tag.short_description = 'Imagen'
    imagen_tag.allow_tags = True

