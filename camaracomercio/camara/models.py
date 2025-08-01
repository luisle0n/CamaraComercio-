from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission

# para crear un modelo de usuario personalizado
class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('socio', 'Socio'),
        ('visitante', 'Visitante'),
        ('empresa', 'Empresa'),
    ]
    nombre = models.CharField(max_length=255)
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    red_social_preferida = models.CharField(max_length=100, null=True, blank=True)
    aprobado = models.BooleanField(default=False)
    debe_cambiar_contrasena = models.BooleanField(default=False)
    fecha_contrasena_temporal = models.DateTimeField(null=True, blank=True)

    # Soluciona el conflicto de related_name
    groups = models.ManyToManyField(
        Group,
        related_name='usuario_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuario_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def contrasena_temporal_expirada(self):
        if self.fecha_contrasena_temporal:
            return timezone.now() > self.fecha_contrasena_temporal + timezone.timedelta(hours=24)
        return False

    def __str__(self):
        return f"{self.nombre} ({self.email})"


class Afiliacion(models.Model):
    """ Modelo abstracto base para afiliaciones """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_afiliacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')

    # Datos comunes
    tipo_persona = models.CharField(max_length=20, choices=[('natural', 'Natural'), ('juridica', 'Jurídica')])
    correo_electronico = models.EmailField()
    telefono = models.CharField(max_length=20, null=True, blank=True)

    # Redes sociales
    red_social_whatsapp = models.BooleanField(default=False)
    red_social_facebook = models.BooleanField(default=False)
    red_social_instagram = models.BooleanField(default=False)
    red_social_youtube = models.BooleanField(default=False)
    red_social_tiktok = models.BooleanField(default=False)

    comprobante_pago = models.FileField(upload_to='comprobantes/', null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.correo_electronico} - {self.get_tipo_persona_display()} - {self.get_estado_display()}"

    @classmethod
    def total_aprobadas(cls):
        return cls.objects.filter(estado='aprobada').count()


class AfiliacionNatural(Afiliacion):
    nombre_comercial_o_nombres = models.CharField(max_length=255)
    ruc_o_cedula = models.CharField(max_length=20)

    direccion_principal = models.TextField(null=True, blank=True)
    calle = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=50, null=True, blank=True)
    calle_interseccion = models.CharField(max_length=255, null=True, blank=True)
    referencia = models.CharField(max_length=255, null=True, blank=True)
    edificio = models.CharField(max_length=255, null=True, blank=True)
    piso = models.CharField(max_length=10, null=True, blank=True)
    oficina = models.CharField(max_length=10, null=True, blank=True)
    parroquia = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.CharField(max_length=255, null=True, blank=True)
    pais = models.CharField(max_length=255, null=True, blank=True)
    pagina_web = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_comercial_o_nombres[:20]} - {self.ruc_o_cedula} - {self.get_estado_display()}"


class AfiliacionJuridica(Afiliacion):
    razon_social = models.CharField(max_length=255)
    nombre_comercial_o_nombres = models.CharField(max_length=255)
    ruc_o_cedula = models.CharField(max_length=20)

    rep_legal_cedula_pasaporte = models.CharField(max_length=50)
    rep_legal_apellido1 = models.CharField(max_length=100)
    rep_legal_apellido2 = models.CharField(max_length=100, null=True, blank=True)
    rep_legal_nombres = models.CharField(max_length=255)

    direccion_principal = models.TextField(null=True, blank=True)
    calle = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=50, null=True, blank=True)
    calle_interseccion = models.CharField(max_length=255, null=True, blank=True)
    referencia = models.CharField(max_length=255, null=True, blank=True)
    edificio = models.CharField(max_length=255, null=True, blank=True)
    piso = models.CharField(max_length=10, null=True, blank=True)
    oficina = models.CharField(max_length=10, null=True, blank=True)
    parroquia = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.CharField(max_length=255, null=True, blank=True)
    pais = models.CharField(max_length=255, null=True, blank=True)
    pagina_web = models.URLField(null=True, blank=True)
    correo_empresa = models.EmailField(null=True, blank=True)

    telefono1 = models.CharField(max_length=20, null=True, blank=True)
    telefono2 = models.CharField(max_length=20, null=True, blank=True)
    telefono3 = models.CharField(max_length=20, null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)

    tipo_negocio_comercio = models.BooleanField(default=False)
    tipo_negocio_servicios = models.BooleanField(default=False)
    tipo_negocio_import_export = models.BooleanField(default=False)
    tipo_negocio_industria = models.BooleanField(default=False)
    tipo_negocio_otros = models.BooleanField(default=False)
    actividad_economica = models.CharField(max_length=255, null=True, blank=True)

    contacto_juridico_correo = models.EmailField(null=True, blank=True)
    contacto_juridico_telefono = models.CharField(max_length=20, null=True, blank=True)
    contacto_natural_correo = models.EmailField(null=True, blank=True)
    contacto_natural_telefono = models.CharField(max_length=20, null=True, blank=True)

    titular_nombre = models.CharField(max_length=255)
    titular_telefono = models.CharField(max_length=20)
    titular_fecha_nacimiento = models.DateField()
    titular_cedula = models.CharField(max_length=20)

    beneficiario1_nombre = models.CharField(max_length=255, null=True, blank=True)
    beneficiario1_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    beneficiario2_nombre = models.CharField(max_length=255, null=True, blank=True)  # Corregido aquí
    beneficiario2_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    beneficiario3_nombre = models.CharField(max_length=255, null=True, blank=True)
    beneficiario3_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    firma = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.razon_social[:20]} - {self.ruc_o_cedula} - {self.get_estado_display()}"
## ---

class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imagen = models.ImageField(upload_to='servicios/', null=True, blank=True)  # Nuevo campo imagen

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Convenio(models.Model):
    CATEGORIA_CHOICES = [
        ('financieros', 'Servicios Financieros'),
        ('turismo', 'Turismo y Hotelería'),
        ('profesionales', 'Servicios Profesionales'),
        ('graficos', 'Servicios Gráficos'),
    ]
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to='convenios/', null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default='financieros'
    )
    tiene_descuento = models.BooleanField(default=False)  # Nuevo campo
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Nuevo campo
    enlace = models.URLField("Enlace externo", null=True, blank=True)  # Nuevo campo

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"


class Beneficio(models.Model):
    convenio = models.ForeignKey(Convenio, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.descripcion if self.descripcion else "Beneficio sin descripción"

class Credencial(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    hash_contrasena = models.TextField()
    ultimo_inicio_sesion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Credencial de {self.usuario}"


class Documento(models.Model):
    afiliacion_natural = models.ForeignKey('AfiliacionNatural', on_delete=models.SET_NULL, null=True, blank=True)
    afiliacion_juridica = models.ForeignKey('AfiliacionJuridica', on_delete=models.SET_NULL, null=True, blank=True)
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='documentos/', null=True, blank=True)  # Cambiado a FileField

    def __str__(self):
        return f"{self.nombre_archivo}"

    def save_comprobante_afiliacion(self, afiliacion):
        """
        Guarda el comprobante de pago de una afiliación en este documento.
        """
        if hasattr(afiliacion, 'comprobante_pago') and afiliacion.comprobante_pago:
            self.nombre_archivo = afiliacion.comprobante_pago.name
            self.archivo = afiliacion.comprobante_pago
            if isinstance(afiliacion, AfiliacionNatural):
                self.afiliacion_natural = afiliacion
            elif isinstance(afiliacion, AfiliacionJuridica):
                self.afiliacion_juridica = afiliacion
            self.save()


class Empresa(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    tipo_negocio = models.CharField(max_length=100, null=True, blank=True)
    ruc = models.CharField(max_length=20, unique=True)
    representante = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre


class EmpresaConvenio(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True)
    convenio = models.ForeignKey(Convenio, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.empresa} - {self.convenio}"


class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField()

    def __str__(self):
        return f"Notificación para {self.usuario}: {self.mensaje[:30]}..."

    @staticmethod
    def enviar_reserva(reserva):
        """Envía notificación automática al usuario cuando se crea una reserva."""
        # Asegura que fecha_reserva sea un objeto datetime
        from django.utils.dateparse import parse_datetime
        fecha = reserva.fecha_reserva
        if isinstance(fecha, str):
            fecha = parse_datetime(fecha)
        fecha_str = fecha.strftime('%d/%m/%Y %H:%M') if fecha else str(reserva.fecha_reserva)
        mensaje = f"Se ha creado una nueva reserva para el servicio '{reserva.servicio.nombre}' el {fecha_str}."
        Notificacion.objects.create(
            usuario=reserva.usuario,
            mensaje=mensaje,
            fecha_envio=timezone.now()
        )

    @staticmethod
    def enviar_convenio(convenio):
        """Envía notificación automática a todos los usuarios activos cuando se crea un convenio."""
        mensaje = f"Nuevo convenio disponible: '{convenio.nombre}'. ¡Revisa los beneficios y descuentos!"
        from .models import Usuario  # Importación local para evitar problemas de migración
        for usuario in Usuario.objects.filter(is_active=True):
            Notificacion.objects.create(
                usuario=usuario,
                mensaje=mensaje,
                fecha_envio=timezone.now()
            )


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True)
    fecha_reserva = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)

    def __str__(self):
        return f"Reserva de {self.usuario} - {self.servicio} - {self.get_estado_display()}"


class Recibo(models.Model):
    reserva = models.OneToOneField('Reserva', on_delete=models.SET_NULL, null=True, related_name='recibo')
    fecha_emision = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Recibo #{self.pk} - {self.total}"


class SolicitudVida(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    estado_civil = models.CharField(max_length=50, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    correo = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    ocupacion = models.CharField(max_length=255, null=True, blank=True)
    es_empleado = models.BooleanField(null=True)
    otros_seguros = models.TextField(null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    estatura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tension_arterial = models.CharField(max_length=20, null=True, blank=True)
    consume_alcohol = models.BooleanField(null=True)
    fuma = models.BooleanField(null=True)
    usa_drogas = models.BooleanField(null=True)
    deportes = models.TextField(null=True, blank=True)
    beneficiarios = models.TextField(null=True, blank=True)
    detalles_salud = models.TextField(null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Seguro de vida {self.usuario} - {self.fecha_solicitud.date()}"
