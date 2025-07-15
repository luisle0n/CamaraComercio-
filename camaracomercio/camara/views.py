from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
import secrets
from .forms import AfiliacionNaturalForm, AfiliacionJuridicaForm
from .models import AfiliacionNatural, AfiliacionJuridica, Usuario, Credencial
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages

# Create your views here.
def home(request):
    # Si el usuario es superusuario o staff, redirige al admin
    if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
        return redirect('/admin/')
    return render(request, 'vista_publica/home.html')

def login_view(request):
    if request.method == 'POST':
        identificador = request.POST.get('identificador')
        contrasena = request.POST.get('contrasena')
        user = authenticate(request, username=identificador, password=contrasena)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_home')  # Redirige a tu panel adminview
            else:
                return redirect('dashboard')
        else:
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

def afiliacion(request): return render(request, 'vista_publica/afiliacion.html')
def convenios(request): return render(request, 'vista_publica/convenios.html')
def faq(request): return render(request, 'vista_publica/faq.html')

@login_required
def dashboard(request):
    # Solo usuarios normales pueden acceder, no superusuarios ni staff
    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin/')
    # Puedes personalizar la lógica según tu modelo
    reservas = []  # Ejemplo: Reserva.objects.filter(usuario=request.user)
    notificaciones = []  # Ejemplo: Notificacion.objects.filter(usuario=request.user)
    return render(request, 'vista_socio_registrado/dashboard.html', {
        'reservas': reservas,
        'notificaciones': notificaciones,
    })

@login_required
def perfil_usuario(request):
    # Puedes personalizar la lógica según tu modelo
    return render(request, 'vista_socio_registrado/perfil_usuario.html')

@login_required
def historial_reservas(request):
    # Puedes personalizar la lógica según tu modelo
    reservas = []  # Ejemplo: Reserva.objects.filter(usuario=request.user)
    return render(request, 'vista_socio_registrado/historial_reservas.html', {'reservas': reservas})

@login_required
def notificaciones(request):
    # Puedes personalizar la lógica según tu modelo
    notificaciones = []  # Ejemplo: Notificacion.objects.filter(usuario=request.user)
    return render(request, 'vista_socio_registrado/notificaciones.html', {'notificaciones': notificaciones})

def logout_view(request):
    logout(request)
    return redirect('home')

# Vistas de administración con permisos
@permission_required('camara.view_afiliacionnatural', login_url='/login/')
def admin_home(request):
    return render(request, 'adminview/home.html')

@permission_required('camara.view_afiliacionnatural', login_url='/login/')
def afiliaciones_pendientes(request):
    pendientes_natural = AfiliacionNatural.objects.filter(estado='pendiente')
    pendientes_juridica = AfiliacionJuridica.objects.filter(estado='pendiente')
    pendientes = list(pendientes_natural) + list(pendientes_juridica)
    return render(request, 'adminview/afiliaciones_pendientes.html', {
        'pendientes': pendientes,
    })

@permission_required('camara.change_afiliacionnatural', login_url='/login/')
def detalle_afiliacion(request, pk):
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