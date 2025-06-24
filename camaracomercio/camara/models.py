from django.db import models

class Usuario(models.Model):
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

    def __str__(self):
        return self.nombre


class Afiliacion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_solicitud = models.DateTimeField()
    fecha_afiliacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)

    def __str__(self):
        return f"{self.usuario} - {self.estado}"


class Convenio(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Beneficio(models.Model):
    convenio = models.ForeignKey(Convenio, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(null=True, blank=True)


class Chatbot(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    mensaje_usuario = models.TextField()
    respuesta_bot = models.TextField()
    fecha_interaccion = models.DateTimeField()


class ContactoPrincipal(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)


class Credencial(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    hash_contrasena = models.TextField()
    ultimo_inicio_sesion = models.DateTimeField(null=True, blank=True)


class Documento(models.Model):
    afiliacion = models.ForeignKey(Afiliacion, on_delete=models.SET_NULL, null=True)
    nombre_archivo = models.CharField(max_length=255)
    contenido = models.BinaryField(null=True, blank=True)


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


class Estadistica(models.Model):
    descripcion = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField()


class Notificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField()


class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.nombre


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


class Recibo(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.SET_NULL, null=True)
    fecha_emision = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)


class ServicioProveedor(models.Model):
    proveedor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True)


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
