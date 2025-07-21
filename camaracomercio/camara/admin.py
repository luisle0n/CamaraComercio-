from django.contrib import admin
from .models import (
    Usuario, AfiliacionNatural, AfiliacionJuridica, Empresa, Servicio, Convenio, Beneficio,
    ContactoPrincipal, Credencial, Documento, EmpresaConvenio, Notificacion,
    Reserva, Recibo, ServicioProveedor, SolicitudVida
)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'tipo_usuario', 'aprobado', 'is_active')
    search_fields = ('nombre', 'email', 'cedula')
    list_filter = ('tipo_usuario', 'aprobado', 'is_active')

@admin.register(AfiliacionNatural)
class AfiliacionNaturalAdmin(admin.ModelAdmin):
    list_display = ('nombre_comercial_o_nombres', 'ruc_o_cedula', 'correo_electronico', 'estado', 'fecha_solicitud')
    search_fields = ('nombre_comercial_o_nombres', 'ruc_o_cedula', 'correo_electronico')
    list_filter = ('estado',)

@admin.register(AfiliacionJuridica)
class AfiliacionJuridicaAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nombre_comercial_o_nombres', 'ruc_o_cedula', 'correo_electronico', 'estado', 'fecha_solicitud')
    search_fields = ('razon_social', 'nombre_comercial_o_nombres', 'ruc_o_cedula', 'correo_electronico')
    list_filter = ('estado',)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'telefono', 'tipo_negocio')
    search_fields = ('nombre', 'ruc')
    list_filter = ('tipo_negocio',)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')
    search_fields = ('nombre',)
    list_filter = ('precio',)

@admin.register(Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_fin', 'categoria', 'tiene_descuento', 'porcentaje_descuento', 'imagen_tag')
    search_fields = ('nombre',)
    list_filter = ('categoria', 'tiene_descuento')

    def imagen_tag(self, obj):
        if obj.imagen:
            return f'<img src="{obj.imagen.url}" style="max-height:100px;"/>'
        return ''
    imagen_tag.short_description = 'Imagen'
    imagen_tag.allow_tags = True

@admin.register(Beneficio)
class BeneficioAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'convenio')
    search_fields = ('descripcion',)
    list_filter = ('convenio',)

@admin.register(ContactoPrincipal)
class ContactoPrincipalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email', 'usuario')
    search_fields = ('nombre', 'email')
    list_filter = ('usuario',)

@admin.register(Credencial)
class CredencialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ultimo_inicio_sesion')
    search_fields = ('usuario__nombre',)
    list_filter = ('usuario',)

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre_archivo', 'afiliacion_natural', 'afiliacion_juridica')
    search_fields = ('nombre_archivo',)
    list_filter = ('afiliacion_natural', 'afiliacion_juridica')

@admin.register(EmpresaConvenio)
class EmpresaConvenioAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'convenio')
    search_fields = ('empresa__nombre', 'convenio__nombre')
    list_filter = ('empresa', 'convenio')

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'mensaje', 'fecha_envio')
    search_fields = ('usuario__nombre', 'mensaje')
    list_filter = ('fecha_envio',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'servicio', 'fecha_reserva', 'estado')
    search_fields = ('usuario__nombre', 'servicio__nombre')
    list_filter = ('estado',)

@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'fecha_emision', 'total')
    search_fields = ('reserva__usuario__nombre',)
    list_filter = ('fecha_emision',)

@admin.register(ServicioProveedor)
class ServicioProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'servicio')
    search_fields = ('proveedor__nombre', 'servicio__nombre')
    list_filter = ('proveedor', 'servicio')

@admin.register(SolicitudVida)
class SolicitudVidaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'estado_civil', 'fecha_nacimiento', 'fecha_solicitud')
    search_fields = ('usuario__nombre', 'estado_civil')
    list_filter = ('fecha_solicitud',)

