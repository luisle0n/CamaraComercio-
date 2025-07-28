from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.http import Http404
import secrets
from .forms import AfiliacionNaturalForm, AfiliacionJuridicaForm, ConvenioForm, ServicioForm, EmpresaForm, ReservaServicioForm, SolicitudVidaForm
from .models import AfiliacionNatural, AfiliacionJuridica, Usuario, Credencial, Convenio, Servicio, Reserva, Empresa, SolicitudVida, Recibo, Notificacion
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.template.loader import render_to_string, get_template
from django.db import IntegrityError
import logging
from django.urls import reverse
from django.shortcuts import redirect, render
from .forms import EmpresaForm
from .models import Empresa
import weasyprint

# Create your views here.
def get_user_group(user):
    if user.is_superuser or user.is_staff:
        return 'admin'
    # Cambia la lógica para socios: revisa tipo_usuario, no solo grupos
    if getattr(user, 'tipo_usuario', None) == 'socio':
        return 'socio'
    if user.groups.filter(name='Socio').exists():
        return 'socio'
    if user.groups.filter(name='Visitante').exists():
        return 'visitante'
    return 'otro'

def home(request):
    # DEBUG: Verifica si la sesión realmente persiste tras login
    print(f"[HOME] request.user: {request.user}")
    print(f"[HOME] request.user.is_authenticated: {getattr(request.user, 'is_authenticated', None)}")
    print(f"[HOME] sessionid: {request.COOKIES.get('sessionid')}")
    print(f"[HOME] session keys: {list(request.session.keys())}")
    print(f"[HOME] AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
    print(f"[HOME] user class: {type(request.user)}")
    print(f"[HOME] _auth_user_id: {request.session.get('_auth_user_id', None)}")
    print(f"[HOME] _auth_user_backend: {request.session.get('_auth_user_backend', None)}")

    if request.user.is_authenticated:
        # Si es su primer ingreso, fuerza cambio de contraseña
        if hasattr(request.user, 'debe_cambiar_contrasena') and request.user.debe_cambiar_contrasena:
            return redirect('cambio_obligatorio_contrasena')
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_home')
        print(f"[HOME] tipo_usuario: {getattr(request.user, 'tipo_usuario', None)} aprobado: {getattr(request.user, 'aprobado', None)} is_active: {getattr(request.user, 'is_active', None)}")
        print(f"[HOME] grupos: {[g.name for g in request.user.groups.all()]}")
        if (
            getattr(request.user, 'tipo_usuario', None) == 'socio'
            and getattr(request.user, 'aprobado', True)
            and getattr(request.user, 'is_active', True)
        ):
            print("[HOME] Renderizando vista_socio_registrado/home.html por tipo_usuario")
            reservas = []
            # Obtiene las notificaciones del usuario
            from .models import Notificacion
            notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_envio')
            return render(request, 'vista_socio_registrado/home.html', {
                'reservas': reservas,
                'notificaciones': notificaciones,
            })
        elif getattr(request.user, 'tipo_usuario', None) == 'empresa':
            print("[HOME] Renderizando vista_empresa/home.html por tipo_usuario empresa")
            return render(request, 'vista_empresa/home.html')
        elif request.user.groups.filter(name='Socio').exists():
            print("[HOME] Renderizando vista_socio_registrado/home.html por grupo Socio")
            reservas = []
            notificaciones = []
            return render(request, 'vista_socio_registrado/home.html', {
                'reservas': reservas,
                'notificaciones': notificaciones,
            })
        else:
            print("[HOME] Usuario autenticado pero no es socio ni grupo Socio, mostrando home público")
    else:
        print("[HOME] Usuario no autenticado, mostrando home público")
    return render(request, 'vista_publica/home.html')

def login_view(request):
    if request.method == 'POST':
        identificador = request.POST.get('identificador')
        contrasena = request.POST.get('contrasena')
        user = None

        print(f"[LOGIN] Intento de login con identificador: {identificador}")

        identificador_normalizado = identificador.strip().lower()
        print(f"[LOGIN] Identificador normalizado: {identificador_normalizado}")

        # Lógica 1: superuser/staff de camara.Usuario (modelo custom)
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        try:
            user_obj = UserModel.objects.get(username__iexact=identificador_normalizado)
        except UserModel.DoesNotExist:
            try:
                user_obj = UserModel.objects.get(email__iexact=identificador_normalizado)
            except UserModel.DoesNotExist:
                user_obj = None

        if user_obj and (user_obj.is_superuser or user_obj.is_staff):
            print("[LOGIN] Intento de login como superuser/staff (camara.Usuario)")
            user = authenticate(request, username=user_obj.username, password=contrasena)
            if user is not None:
                login(request, user)
                print("[LOGIN] Login superuser/staff exitoso")
                request.session.set_expiry(0)
                request.session.modified = True
                return redirect('admin_home')
            else:
                print("[LOGIN] Credenciales admin inválidas")
                messages.error(request, 'Credenciales inválidas.')
                return render(request, 'vista_publica/login.html')

        # Lógica 2: usuario normal de camara.Usuario
        if not user_obj:
            # Buscar por email en modelo custom (por si no es superuser/staff)
            try:
                user_obj = UserModel.objects.get(email__iexact=identificador_normalizado)
            except UserModel.DoesNotExist:
                user_obj = None

        if user_obj:
            print(f"[LOGIN] Usuario encontrado: username={user_obj.username}, email={user_obj.email}, tipo_usuario={getattr(user_obj, 'tipo_usuario', None)}, aprobado={getattr(user_obj, 'aprobado', None)}, is_active={user_obj.is_active}")
            if not user_obj.aprobado and not user_obj.is_superuser and not user_obj.is_staff:
                print("[LOGIN] Usuario no aprobado")
                messages.error(request, 'Tu cuenta aún no ha sido aprobada por el administrador.')
                return render(request, 'vista_publica/login.html')
            user = authenticate(request, username=user_obj.username, password=contrasena)
            if user is not None:
                login(request, user)
                print("[LOGIN] Login usuario custom exitoso")
                request.session.set_expiry(0)
                request.session.modified = True
                if user.is_superuser or user.is_staff:
                    return redirect('admin_home')
                else:
                    return redirect('home')
            else:
                print("[LOGIN] Credenciales inválidas para usuario custom")
                messages.error(request, 'Credenciales inválidas.')
                return render(request, 'vista_publica/login.html')
        else:
            print("[LOGIN] Usuario no encontrado en camara.Usuario")
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'vista_publica/login.html')

def registro(request):
    tipo = request.POST.get('tipo_usuario', 'persona')
    if request.method == 'POST':
        if tipo == 'persona':
            post_data = request.POST.copy()
            post_data['tipo_persona'] = 'natural'
            form = AfiliacionNaturalForm(post_data, request.FILES)
            empresa_form = AfiliacionJuridicaForm()
            if form.is_valid():
                form.save()
                return redirect('home')
        else:
            post_data = request.POST.copy()
            post_data['tipo_persona'] = 'juridica'
            empresa_form = AfiliacionJuridicaForm(post_data, request.FILES)
            form = AfiliacionNaturalForm()
            if empresa_form.is_valid():
                empresa_form.save()
                return redirect('home')
    else:
        form = AfiliacionNaturalForm()
        empresa_form = AfiliacionJuridicaForm()
    return render(request, 'vista_publica/registro.html', {
        'form': form,
        'empresa_form': empresa_form,
        'tipo': tipo
    })

from .forms import EmpresaForm
from .models import Empresa

def registro_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            empresa = form.save(commit=False)
            empresa.representante = request.user
            empresa.save()
            # Cambia aquí la redirección a una URL válida, por ejemplo al home del usuario
            return redirect('home')  # Usa el nombre de una URL existente, como 'home' o 'perfil_usuario'
    else:
        form = EmpresaForm(initial={'representante': request.user.pk})
    return render(request, 'vista_socio_registrado/registroEmpresa.html', {
        'form': form
    })

def afiliacion(request): return render(request, 'vista_publica/afiliacion.html')
def convenios(request):
    convenios = Convenio.objects.all()
    return render(request, 'vista_publica/convenios.html', {'convenios': convenios})
def faq(request): return render(request, 'vista_publica/faq.html')

# Quitar todos los decoradores @login_required de las vistas protegidas
def dashboard(request):
    grupo = get_user_group(request.user)
    if not request.user.is_authenticated:
        return redirect('home')
    # Si es empresa, muestra dashboard empresa con solo sus reservas y notificaciones
    if getattr(request.user, 'tipo_usuario', None) == 'empresa':
        reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha_reserva')
        notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_envio')
        return render(request, 'vista_empresa/dashboard.html', {
            'reservas': reservas,
            'notificaciones': notificaciones,
        })
    # Si es socio, muestra dashboard socio con solo sus reservas y notificaciones
    if grupo != 'socio':
        return redirect('home')
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha_reserva')
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_envio')
    return render(request, 'vista_socio_registrado/dashboard.html', {
        'reservas': reservas,
        'notificaciones': notificaciones,
    })

def perfil_usuario(request):
    grupo = get_user_group(request.user)
    if not request.user.is_authenticated or grupo != 'socio':
        return redirect('home')
    return render(request, 'vista_socio_registrado/perfil_usuario.html')

def historial_reservas(request):
    grupo = get_user_group(request.user)
    if not request.user.is_authenticated:
        return redirect('home')
    # Si es empresa, muestra solo sus reservas
    if getattr(request.user, 'tipo_usuario', None) == 'empresa':
        reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha_reserva')
        return render(request, 'vista_empresa/historial_reservas.html', {'reservas': reservas})
    # Si es socio, muestra solo sus reservas
    if getattr(request.user, 'tipo_usuario', None) != 'socio':
        return redirect('home')
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha_reserva')
    return render(request, 'vista_socio_registrado/historial_reservas.html', {'reservas': reservas})

def notificaciones(request):
    grupo = get_user_group(request.user)
    if not request.user.is_authenticated:
        return redirect('home')
    # Si es empresa, muestra notificaciones empresa
    if getattr(request.user, 'tipo_usuario', None) == 'empresa':
        notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_envio')
        return render(request, 'vista_empresa/notificaciones.html', {'notificaciones': notificaciones})
    # Si es socio, muestra notificaciones socio
    if grupo != 'socio':
        return redirect('home')
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_envio')
    return render(request, 'vista_socio_registrado/notificaciones.html', {'notificaciones': notificaciones})

def logout_view(request):
    logout(request)
    return redirect('home')

# Vistas de administración con permisos
@permission_required('camara.view_afiliacionnatural', login_url='/login/')
def admin_home(request):
    grupo = get_user_group(request.user)
    if grupo != 'admin':
        return redirect('home')
    from .models import Usuario, Empresa, Convenio, AfiliacionNatural, AfiliacionJuridica

    num_socios = Usuario.objects.filter(tipo_usuario='socio').count()
    num_empresas = Empresa.objects.count()
    num_convenios = Convenio.objects.count()
    solicitudes_aprobadas = AfiliacionNatural.objects.filter(estado='aprobada').count() + AfiliacionJuridica.objects.filter(estado='aprobada').count()
    solicitudes_rechazadas = AfiliacionNatural.objects.filter(estado='rechazada').count() + AfiliacionJuridica.objects.filter(estado='rechazada').count()

    # Estadística 1: Redes sociales más usadas
    redes = [
        ('Whatsapp', 'red_social_whatsapp'),
        ('Facebook', 'red_social_facebook'),
        ('Instagram', 'red_social_instagram'),
        ('YouTube', 'red_social_youtube'),
        ('TikTok', 'red_social_tiktok'),
    ]
    labels = []
    data = []
    for nombre, campo in redes:
        total = AfiliacionNatural.objects.filter(**{campo: True}).count() + AfiliacionJuridica.objects.filter(**{campo: True}).count()
        labels.append(nombre)
        data.append(total)
    estadistica1 = {
        "label": "Redes sociales más usadas",
        "labels": labels,
        "data": data,
    }

    estadistica2 = {
        "label": "Solicitudes por estado",
        "labels": ["Aprobadas", "Rechazadas", "Pendientes"],
        "data": [solicitudes_aprobadas, solicitudes_rechazadas,
                 AfiliacionNatural.objects.filter(estado='pendiente').count() + AfiliacionJuridica.objects.filter(estado='pendiente').count()],
    }
    return render(request, 'adminview/home.html', {
        'num_socios': num_socios,
        'num_empresas': num_empresas,
        'num_convenios': num_convenios,
        'solicitudes_aprobadas': solicitudes_aprobadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'estadistica1': estadistica1,
        'estadistica2': estadistica2,
    })

@permission_required('camara.view_afiliacionnatural', login_url='/login/')
def afiliaciones_pendientes(request):
    grupo = get_user_group(request.user)
    if grupo != 'admin':
        return redirect('home')
    pendientes_natural = AfiliacionNatural.objects.filter(estado='pendiente')
    pendientes_juridica = AfiliacionJuridica.objects.filter(estado='pendiente')
    pendientes = list(pendientes_natural) + list(pendientes_juridica)
    return render(request, 'adminview/afiliaciones_pendientes.html', {
        'pendientes': pendientes,
    })

@permission_required('camara.change_afiliacionnatural', login_url='/login/')
def detalle_afiliacion(request, pk):
    grupo = get_user_group(request.user)
    if grupo != 'admin':
        return redirect('home')
    # Buscar primero en AfiliacionJuridica, luego en AfiliacionNatural
    afiliacion = None
    tipo_persona = None
    try:
        afiliacion = AfiliacionJuridica.objects.get(pk=pk)
        tipo_persona = 'juridica'
    except AfiliacionJuridica.DoesNotExist:
        try:
            afiliacion = AfiliacionNatural.objects.get(pk=pk)
            tipo_persona = 'natural'
        except AfiliacionNatural.DoesNotExist:
            raise Http404("Afiliación no encontrada")

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'aprobar':
            password_plain = secrets.token_urlsafe(12)
            # Determinar red social preferida por orden de prioridad
            if afiliacion.red_social_whatsapp:
                red_preferida = 'Whatsapp'
            elif afiliacion.red_social_instagram:
                red_preferida = 'Instagram'
            elif afiliacion.red_social_facebook:
                red_preferida = 'Facebook'
            elif afiliacion.red_social_youtube:
                red_preferida = 'YouTube'
            elif afiliacion.red_social_tiktok:
                red_preferida = 'TikTok'
            else:
                red_preferida = ''

            # Verifica si ya existe un usuario con ese email o cédula
            if Usuario.objects.filter(email=afiliacion.correo_electronico).exists() or Usuario.objects.filter(cedula=afiliacion.ruc_o_cedula).exists():
                messages.error(request, "Ya existe un usuario registrado con este correo o cédula.")
                return redirect('afiliaciones_pendientes')

            usuario = Usuario.objects.create(
                nombre=afiliacion.nombre_comercial_o_nombres,
                tipo_usuario='socio',
                cedula=afiliacion.ruc_o_cedula,
                email=afiliacion.correo_electronico,
                telefono='',
                red_social_preferida=red_preferida,
                aprobado=True,
                debe_cambiar_contrasena=True,
                fecha_contrasena_temporal=timezone.now(),
                username=afiliacion.correo_electronico  # Usar correo como usuario
            )

            usuario.set_password(password_plain)
            usuario.save()

            Credencial.objects.create(
                usuario=usuario,
                hash_contrasena=make_password(password_plain)
            )

            afiliacion.usuario = usuario
            afiliacion.estado = 'aprobada'
            afiliacion.fecha_afiliacion = timezone.now()
            afiliacion.save()

            # Enviar correo con credenciales (correo como usuario)
            send_mail(
                'Tu cuenta ha sido aprobada',
                '',
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                html_message=render_to_string('emails/aprobacion_usuario.html', {
                    'usuario': usuario,
                    'correo_login': usuario.email,
                    'temp_password': password_plain,
                })
            )

        elif action == 'rechazar':
            afiliacion.estado = 'rechazada'
            afiliacion.save()

        return redirect('afiliaciones_pendientes')

    return render(request, 'adminview/detalle_afiliacion.html', {
        'afiliacion': afiliacion,
        'tipo_persona': tipo_persona,
    })

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.is_staff), login_url='/login/')(view_func)

@admin_required
def admin_convenios_list(request):
    convenios = Convenio.objects.all()
    return render(request, 'adminview/convenios_list.html', {'convenios': convenios})

@admin_required
def admin_convenio_create(request):
    from .forms import ConvenioForm
    if request.method == 'POST':
        form = ConvenioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_convenios_list')
    else:
        form = ConvenioForm()
    return render(request, 'adminview/convenio_form.html', {
        'form': form,
        'accion': 'Crear'
    })

@admin_required
def admin_convenio_edit(request, pk):
    convenio = Convenio.objects.get(pk=pk)
    if request.method == 'POST':
        form = ConvenioForm(request.POST, request.FILES, instance=convenio)
        if form.is_valid():
            form.save()
            return redirect('admin_convenios_list')
    else:
        form = ConvenioForm(instance=convenio)
    return render(request, 'adminview/convenio_edit.html', {
        'form': form,
        'convenio': convenio,
    })

@admin_required
def admin_convenio_delete(request, pk):
    convenio = Convenio.objects.get(pk=pk)
    if request.method == 'POST':
        convenio.delete()
        return redirect('admin_convenios_list')
    return render(request, 'adminview/convenio_confirm_delete.html', {'convenio': convenio})

@admin_required
def admin_servicios_list(request):
    servicios = Servicio.objects.all()
    return render(request, 'adminview/servicios_list.html', {'servicios': servicios})

@admin_required
def admin_servicio_create(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_servicios_list')
    else:
        form = ServicioForm()
    return render(request, 'adminview/servicio_form.html', {
        'form': form,
        'accion': 'Crear'
    })

@admin_required
def admin_servicio_edit(request, pk):
    servicio = Servicio.objects.get(pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('admin_servicios_list')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'adminview/servicio_form.html', {
        'form': form,
        'accion': 'Editar'
    })

@admin_required
def admin_servicio_delete(request, pk):
    servicio = Servicio.objects.get(pk=pk)
    if request.method == 'POST':
        servicio.delete()
        return redirect('admin_servicios_list')
    return render(request, 'adminview/servicio_confirm_delete.html', {'servicio': servicio})

@admin_required
def admin_reservas_list(request):
    from .models import Reserva
    estado = request.GET.get('estado')
    reservas = Reserva.objects.select_related('usuario', 'servicio').all()
    if estado:
        reservas = reservas.filter(estado=estado)
    reservas = reservas.order_by('-fecha_reserva')
    return render(request, 'adminview/reservas_list.html', {
        'reservas': reservas,
    })

@admin_required
def admin_reserva_estado(request, pk):
    from .models import Reserva
    reserva = Reserva.objects.get(pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Reserva.ESTADO_CHOICES):
            reserva.estado = nuevo_estado
            reserva.save()
            messages.success(request, 'Estado de la reserva actualizado.')
        else:
            messages.error(request, 'Estado inválido.')
        return redirect('admin_reservas_list')
    return render(request, 'adminview/reserva_estado_form.html', {'reserva': reserva})

def aprobar_usuario(request, user_id):
    user = Usuario.objects.get(pk=user_id)
    if not user.aprobado:
        temp_password = get_random_string(12)
        user.set_password(temp_password)
        user.aprobado = True
        user.debe_cambiar_contrasena = True
        user.fecha_contrasena_temporal = timezone.now()
        user.save()
        send_mail(
            'Tu cuenta ha sido aprobada',
            '',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=render_to_string('emails/aprobacion_usuario.html', {
                'usuario': user,
                'temp_password': temp_password,
            })
        )
    return redirect('afiliaciones_pendientes')

@login_required(login_url='/login/')
def cambio_obligatorio_contrasena(request):
    # Sin decorador login_required, control manual
    if not hasattr(request, "user") or not request.user.is_authenticated:
        print("[CAMBIO CONTRASEÑA] Usuario no autenticado, forzando logout y redirigiendo a login SIN parámetro next")
        try:
            logout(request)
        except Exception as e:
            print(f"[CAMBIO CONTRASEÑA] Error en logout: {e}")
        if hasattr(request, "session"):
            request.session.flush()
        # Redirige a /login/ sin next, usando HttpResponseRedirect y borrando el parámetro GET
        from django.http import HttpResponseRedirect
        response = HttpResponseRedirect('/login/')
        response.status_code = 302
        return response
    if not getattr(request.user, 'debe_cambiar_contrasena', False):
        return redirect('dashboard')
    if hasattr(request.user, 'contrasena_temporal_expirada') and request.user.contrasena_temporal_expirada():
        logout(request)
        if hasattr(request, "session"):
            request.session.flush()
        messages.error(request, 'La contraseña temporal ha expirado. Contacte al administrador.')
        from django.http import HttpResponseRedirect
        response = HttpResponseRedirect('/login/')
        response.status_code = 302
        return response
    if request.method == 'POST':
        nueva = request.POST.get('nueva')
        nueva2 = request.POST.get('nueva2')
        if nueva and nueva == nueva2:
            request.user.set_password(nueva)
            request.user.debe_cambiar_contrasena = False
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Contraseña cambiada correctamente.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Las contraseñas no coinciden.')
    return render(request, 'vista_publica/cambio_obligatorio_contrasena.html')

def servicios_publicos(request):
    servicios = Servicio.objects.all()
    return render(request, 'vista_socio_registrado/servicios_list.html', {'servicios': servicios})

@login_required(login_url='/login/')
def reservar_servicio(request, pk):
    servicio = Servicio.objects.get(pk=pk)
    if request.method == 'POST':
        form = ReservaServicioForm(request.POST)
        if form.is_valid():
            fecha_reserva = form.cleaned_data['fecha_reserva']
            reserva = Reserva.objects.create(
                usuario=request.user,
                servicio=servicio,
                fecha_reserva=fecha_reserva,
                estado='pendiente'
            )
            Notificacion.enviar_reserva(reserva)
            messages.success(request, f'Reserva realizada para el servicio: {servicio.nombre}')
            return redirect('servicios_publicos')
    else:
        form = ReservaServicioForm()
    return render(request, 'vista_socio_registrado/reservar_servicio.html', {
        'servicio': servicio,
        'form': form,
    })

from .models import SolicitudVida

@login_required(login_url='/login/')
def solicitar_seguro_vida(request):
    if request.method == 'POST':
        form = SolicitudVidaForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.save()
            messages.success(request, 'Solicitud de seguro de vida enviada correctamente.')
            return redirect('home')
    else:
        form = SolicitudVidaForm()
    return render(request, 'vista_socio_registrado/solicitar_seguro_vida.html', {
        'form': form
    })

@permission_required('camara.add_notificacion', login_url='/login/')
def admin_notificacion(request):
    from .models import Usuario, Notificacion
    usuarios = Usuario.objects.filter(is_active=True)
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario')
        mensaje = request.POST.get('mensaje')
        if usuario_id and mensaje:
            usuario = Usuario.objects.get(pk=usuario_id)
            Notificacion.objects.create(
                usuario=usuario,
                mensaje=mensaje,
                fecha_envio=timezone.now()
            )
            messages.success(request, f'Notificación enviada a {usuario.email}')
        else:
            messages.error(request, 'Debes seleccionar un usuario y escribir un mensaje.')
    return render(request, 'adminview/notificacion.html', {'usuarios': usuarios})

@admin_required
def admin_beneficio_create(request, convenio_id):
    from .models import Convenio, Beneficio
    convenio = Convenio.objects.get(pk=convenio_id)
    if request.method == 'POST':
        descripciones = request.POST.getlist('descripcion')
        for desc in descripciones:
            if desc.strip():
                Beneficio.objects.create(convenio=convenio, descripcion=desc.strip())
        # Redirige a la lista de convenios o donde corresponda
        return redirect('admin_convenios_list')
    return render(request, 'adminview/beneficio_form.html', {'convenio': convenio})

@admin_required
def admin_beneficio_edit(request, pk):
    from .models import Beneficio
    beneficio = Beneficio.objects.get(pk=pk)
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            beneficio.descripcion = descripcion
            beneficio.save()
            messages.success(request, 'Beneficio editado correctamente.')
            return redirect('admin_convenios_list')
        else:
            messages.error(request, 'Debes ingresar la descripción del beneficio.')
    return render(request, 'adminview/beneficio_form.html', {'convenio': beneficio.convenio, 'beneficio': beneficio})

@admin_required
def admin_beneficio_delete(request, pk):
    from .models import Beneficio
    beneficio = Beneficio.objects.get(pk=pk)
    convenio = beneficio.convenio
    if request.method == 'POST':
        beneficio.delete()
        messages.success(request, 'Beneficio eliminado correctamente.')
        return redirect('admin_convenios_list')
    return render(request, 'adminview/beneficio_confirm_delete.html', {'beneficio': beneficio, 'convenio': convenio})

@permission_required('camara.view_afiliacionnatural', login_url='/login/')
def admin_ver_afiliados(request):
    grupo = get_user_group(request.user)
    if grupo != 'admin':
        return redirect('home')
    afiliados_naturales = AfiliacionNatural.objects.filter(estado='aprobada')
    afiliados_juridicos = AfiliacionJuridica.objects.filter(estado='aprobada')
    return render(request, 'adminview/ver_afiliados.html', {
        'afiliados_naturales': afiliados_naturales,
        'afiliados_juridicos': afiliados_juridicos,
    })

@login_required(login_url='/login/')
def generar_recibo(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if reserva.usuario != request.user or reserva.estado != 'confirmada':
        messages.error(request, 'No tienes permiso para generar el recibo.')
        return redirect('historial_reservas')
    if hasattr(reserva, 'recibo'):
        messages.info(request, 'Ya existe un recibo para esta reserva.')
        return redirect('historial_reservas')
    recibo = Recibo.objects.create(
        reserva=reserva,
        fecha_emision=timezone.now(),
        total=reserva.servicio.precio or 0
    )
    messages.success(request, 'Recibo generado correctamente.')
    return redirect('historial_reservas')

@login_required(login_url='/login/')
def ver_recibo(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)
    if recibo.reserva.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver este recibo.')
        return redirect('historial_reservas')
    return render(request, 'vista_socio_registrado/recibo.html', {'recibo': recibo})

from django.http import HttpResponse  # Asegúrate de tener esta importación

def descargar_recibo_pdf(request, pk):
    from .models import Recibo
    from django.template.loader import get_template
    import weasyprint

    recibo = Recibo.objects.get(pk=pk)
    template = get_template('vista_socio_registrado/recibo.html')
    html = template.render({'recibo': recibo, 'user': request.user})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_{recibo.pk}.pdf"'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)
    return response

from .models import Empresa

def admin_empresas_list(request):
    empresas = Empresa.objects.all().order_by('nombre')
    return render(request, 'adminview/empresas_list.html', {
        'empresas': empresas,
    })

def mis_empresas(request):
    empresas = Empresa.objects.filter(representante=request.user)
    return render(request, 'vista_socio_registrado/mis_empresas.html', {
        'empresas': empresas
    })