from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('afiliacion/', views.afiliacion, name='afiliacion'),
    path('convenios/', views.convenios, name='convenios'),
    path('faq/', views.faq, name='faq'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('historial-reservas/', views.historial_reservas, name='historial_reservas'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('logout/', views.logout_view, name='logout'),  # Añadido aquí
    path('admin-home/', views.admin_home, name='admin_home'),
    path('afiliaciones-pendientes/', views.afiliaciones_pendientes, name='afiliaciones_pendientes'),
    path('afiliacion/<int:pk>/', views.detalle_afiliacion, name='detalle_afiliacion'),
    path('admin-convenios/', views.admin_convenios_list, name='admin_convenios_list'),
    path('admin-convenios/crear/', views.admin_convenio_create, name='admin_convenio_create'),
    path('admin-convenios/<int:pk>/editar/', views.admin_convenio_edit, name='admin_convenio_edit'),
    path('admin-convenios/<int:pk>/eliminar/', views.admin_convenio_delete, name='admin_convenio_delete'),
]
