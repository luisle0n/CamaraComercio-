from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.http import Http404
import secrets
from .forms import AfiliacionNaturalForm, AfiliacionJuridicaForm
from .models import AfiliacionNatural, AfiliacionJuridica, Usuario, Credencial, Convenio
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.template.loader import render_to_string
from django.db import IntegrityError
import logging
from django.urls import reverse

# Create your views here.
def get_user_group(user):
    if user.is_superuser or user.is_staff:
        return 'admin'
    if user.groups.filter(name='Socio').exists():
        return 'socio'
    if user.groups.filter(name='Visitante').exists():
        return 'visitante'
    return 'otro'

def home(request):
    # Redirige según el tipo de usuario
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin_home')
        if request.user.groups.filter(name='Socio').exists():
            return redirect('dashboard')
        # Puedes agregar lógica para otros grupos si lo necesitas
    return render(request, 'vista_publica/home.html')

def login_view(request):
    if request.method == 'POST':
        identificador = request.POST.get('identificador')
        contrasena = request.POST.get('contrasena')
        user = None

        print(f"[LOGIN] Intento de login con identificador: {identificador}")

        identificador_normalizado = identificador.strip().lower()
        print(f"[LOGIN] Identificador normalizado: {identificador_normalizado}")

        from django.contrib.auth import get_user_model
        from .models import Usuario as UsuarioCustom

        UserModel = get_user_model()
        is_admin_login = False
        admin_user = None

        # Busca por username o email en el modelo de Django
        try:
            admin_user = UserModel.objects.get(username__iexact=identificador_normalizado)
            is_admin_login = admin_user.is_superuser or admin_user.is_staff
        except UserModel.DoesNotExist:
            try:
                admin_user = UserModel.objects.get(email__iexact=identificador_normalizado)
                is_admin_login = admin_user.is_superuser or admin_user.is_staff
            except UserModel.DoesNotExist:
                admin_user = None

        if is_admin_login and admin_user:
            print("[LOGIN] Intento de login como admin/superuser/staff")
            user = authenticate(request, username=admin_user.username, password=contrasena)
            if user is not None:
                login(request, user)
                print("[LOGIN] Login admin exitoso")
                request.session.set_expiry(0)  # Sesión expira al cerrar navegador
                return redirect('admin_home')
            else:
                print("[LOGIN] Credenciales admin inválidas")
                messages.error(request, 'Credenciales inválidas.')
                return render(request, 'vista_publica/login.html')

        # Si no es admin, busca en el modelo personalizado
        print("[LOGIN] Emails registrados en la tabla Usuario:")
        for u in UsuarioCustom.objects.all():
            print(f" - {u.email} (username: {u.username})")

        try:
            user_obj = UsuarioCustom.objects.get(email__iexact=identificador_normalizado)
            username = user_obj.username
            print(f"[LOGIN] Usuario encontrado: username={username}, email={user_obj.email}, tipo_usuario={getattr(user_obj, 'tipo_usuario', None)}, aprobado={getattr(user_obj, 'aprobado', None)}, is_active={user_obj.is_active}")
            print(f"[LOGIN] El nombre de usuario (username) de este usuario es: {username}")
            if not user_obj.aprobado:
                print("[LOGIN] Usuario no aprobado")
                messages.error(request, 'Tu cuenta aún no ha sido aprobada por el administrador.')
                return render(request, 'vista_publica/login.html')
        except UsuarioCustom.DoesNotExist:
            print("[LOGIN] Usuario no encontrado con ese email")
            username = None

        if username:
            print(f"[LOGIN] Autenticando con username: {username} y contraseña: {contrasena}")
            user_obj.refresh_from_db()
            if user_obj.check_password(contrasena):
                print("[LOGIN] check_password OK, autenticando...")
                from django.contrib.auth import login as auth_login
                user = user_obj
                if user.is_active:
                    auth_login(request, user)
                    print(f"[LOGIN] Login manual exitoso para: {user.username}")
                    request.session.set_expiry(0)  # Sesión expira al cerrar navegador
                    # Forzar guardar la sesión antes de redirigir
                    request.session.modified = True
                    if getattr(user, 'debe_cambiar_contrasena', False):
                        print("[LOGIN] Usuario debe cambiar contraseña, redirigiendo a cambio_obligatorio_contrasena")
                        from django.urls import reverse
                        return redirect(reverse('cambio_obligatorio_contrasena'))
                    tipo_usuario = getattr(user, 'tipo_usuario', None)
                    if tipo_usuario == 'socio':
                        print("[LOGIN] Usuario es socio")
                        return redirect('dashboard')
                    elif tipo_usuario == 'empresa':
                        print("[LOGIN] Usuario es empresa")
                        return redirect('dashboard_empresa')
                    elif tipo_usuario == 'visitante':
                        print("[LOGIN] Usuario es visitante")
                        return redirect('home')
                    else:
                        print("[LOGIN] Usuario es otro tipo")
                        return redirect('home')
                else:
                    print("[LOGIN] Usuario inactivo")
                    messages.error(request, 'La cuenta está inactiva.')
                    return render(request, 'vista_publica/login.html')
            else:
                print("[LOGIN] check_password FAIL: la contraseña no coincide con el hash en la base de datos")
                user = None
        else:
            print("[LOGIN] No hay username para autenticar")
            user = None

        if user is None:
            print("[LOGIN] Credenciales inválidas")
            messages.error(request, 'Credenciales inválidas.')
    return render(request, 'vista_publica/login.html')

def dashboard_empresa(request):
    grupo = get_user_group(request.user)
    if grupo != 'empresa':
        return redirect('home')
    # Aquí puedes agregar la lógica específica para el dashboard de empresas
    return render(request, 'vista_empresa_registrada/dashboard_empresa.html')

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

def afiliacion(request): return render(request, 'vista_publica/afiliacion.html')
def convenios(request):
    convenios = Convenio.objects.all()
    return render(request, 'vista_publica/convenios.html', {'convenios': convenios})
def faq(request): return render(request, 'vista_publica/faq.html')

# Quitar todos los decoradores @login_required de las vistas protegidas
def dashboard(request):
    grupo = get_user_group(request.user)
    if not request.user.is_authenticated or grupo != 'socio':
        return redirect('home')
    reservas = []
    notificaciones = []
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
    if not request.user.is_authenticated or grupo != 'socio':
        return redirect('home')
    reservas = []
    return render(request, 'vista_socio_registrado/historial_reservas.html', {'reservas': reservas})

def notificaciones(request):
    grupo = get_user_group(request.user)
    if not request.user.is_authenticated or grupo != 'socio':
        return redirect('home')
    notificaciones = []
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
    # Intentar buscar primero en AfiliacionNatural, luego en AfiliacionJuridica
    try:
        afiliacion = AfiliacionNatural.objects.get(pk=pk)
    except AfiliacionNatural.DoesNotExist:
        try:
            afiliacion = AfiliacionJuridica.objects.get(pk=pk)
        except AfiliacionJuridica.DoesNotExist:
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
                username=afiliacion.ruc_o_cedula
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

            # Enviar correo con credenciales
            send_mail(
                'Tu cuenta ha sido aprobada',
                '',
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                html_message=render_to_string('emails/aprobacion_usuario.html', {
                    'usuario': usuario,
                    'temp_password': password_plain,
                })
            )

        elif action == 'rechazar':
            afiliacion.estado = 'rechazada'
            afiliacion.save()

        return redirect('afiliaciones_pendientes')

    return render(request, 'adminview/detalle_afiliacion.html', {'afiliacion': afiliacion})

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and (u.is_superuser or u.is_staff), login_url='/login/')(view_func)

@admin_required
def admin_convenios_list(request):
    convenios = Convenio.objects.all()
    return render(request, 'adminview/convenios_list.html', {'convenios': convenios})

@admin_required
def admin_convenio_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        fecha_fin = request.POST.get('fecha_fin')
        imagen = request.FILES.get('imagen')
        convenio = Convenio(nombre=nombre, descripcion=descripcion)
        if fecha_fin:
            convenio.fecha_fin = fecha_fin
        if imagen:
            convenio.imagen = imagen
        convenio.save()
        return redirect('admin_convenios_list')
    return render(request, 'adminview/convenio_form.html', {'accion': 'Crear'})

@admin_required
def admin_convenio_edit(request, pk):
    convenio = Convenio.objects.get(pk=pk)
    if request.method == 'POST':
        convenio.nombre = request.POST.get('nombre')
        convenio.descripcion = request.POST.get('descripcion')
        fecha_fin = request.POST.get('fecha_fin')
        imagen = request.FILES.get('imagen')
        if fecha_fin:
            convenio.fecha_fin = fecha_fin
        else:
            convenio.fecha_fin = None
        if imagen:
            convenio.imagen = imagen
        convenio.save()
        return redirect('admin_convenios_list')
    return render(request, 'adminview/convenio_form.html', {'convenio': convenio, 'accion': 'Editar'})

@admin_required
def admin_convenio_delete(request, pk):
    convenio = Convenio.objects.get(pk=pk)
    if request.method == 'POST':
        convenio.delete()
        return redirect('admin_convenios_list')
    return render(request, 'adminview/convenio_confirm_delete.html', {'convenio': convenio})

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