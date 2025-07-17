from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
import secrets
from .forms import AfiliacionNaturalForm, AfiliacionJuridicaForm
from .models import AfiliacionNatural, AfiliacionJuridica, Usuario, Credencial, Convenio
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test

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
        user = authenticate(request, username=identificador, password=contrasena)
        if user is not None:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect('admin_home')  # Redirige a tu panel admin personalizado
            elif user.groups.filter(name='Socio').exists():
                return redirect('dashboard')
            else:
                return redirect('home')
        else:
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

@login_required
def dashboard(request):
    grupo = get_user_group(request.user)
    if grupo != 'socio':
        return redirect('home')
    # Solo usuarios normales pueden acceder, no superusuarios ni staff
    # if request.user.is_superuser or request.user.is_staff:
    #     return redirect('/admin/')
    # Puedes personalizar la lógica según tu modelo
    reservas = []  # Ejemplo: Reserva.objects.filter(usuario=request.user)
    notificaciones = []  # Ejemplo: Notificacion.objects.filter(usuario=request.user)
    return render(request, 'vista_socio_registrado/dashboard.html', {
        'reservas': reservas,
        'notificaciones': notificaciones,
    })

@login_required
def perfil_usuario(request):
    grupo = get_user_group(request.user)
    if grupo != 'socio':
        return redirect('home')
    # Puedes personalizar la lógica según tu modelo
    return render(request, 'vista_socio_registrado/perfil_usuario.html')

@login_required
def historial_reservas(request):
    grupo = get_user_group(request.user)
    if grupo != 'socio':
        return redirect('home')
    # Puedes personalizar la lógica según tu modelo
    reservas = []  # Ejemplo: Reserva.objects.filter(usuario=request.user)
    return render(request, 'vista_socio_registrado/historial_reservas.html', {'reservas': reservas})

@login_required
def notificaciones(request):
    grupo = get_user_group(request.user)
    if grupo != 'socio':
        return redirect('home')
    # Puedes personalizar la lógica según tu modelo
    notificaciones = []  # Ejemplo: Notificacion.objects.filter(usuario=request.user)
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
            password_plain = secrets.token_urlsafe(8)
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

            usuario = Usuario.objects.create(
                nombre=afiliacion.nombre_comercial_o_nombres,
                tipo_usuario='socio',
                cedula=afiliacion.ruc_o_cedula,
                email=afiliacion.correo_electronico,
                telefono='',
                red_social_preferida=red_preferida,
            )

            Credencial.objects.create(
                usuario=usuario,
                hash_contrasena=make_password(password_plain)
            )

            afiliacion.usuario = usuario
            afiliacion.estado = 'aprobada'
            afiliacion.fecha_afiliacion = timezone.now()
            afiliacion.save()

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