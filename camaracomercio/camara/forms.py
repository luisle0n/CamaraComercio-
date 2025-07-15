from django import forms
from .models import AfiliacionNatural, AfiliacionJuridica

class AfiliacionNaturalForm(forms.ModelForm):
    class Meta:
        model = AfiliacionNatural
        fields = [
            'tipo_persona',  # Añadido aquí
            'nombre_comercial_o_nombres', 'ruc_o_cedula', 'direccion_principal', 'calle', 'numero',
            'calle_interseccion', 'referencia', 'edificio', 'piso', 'oficina', 'parroquia', 'ciudad',
            'pais', 'pagina_web', 'correo_electronico', 'telefono', 'red_social_whatsapp',
            'red_social_facebook', 'red_social_instagram', 'red_social_youtube', 'red_social_tiktok',
            'comprobante_pago'
        ]
        widgets = {
            'tipo_persona': forms.HiddenInput(),
        }

class AfiliacionJuridicaForm(forms.ModelForm):
    class Meta:
        model = AfiliacionJuridica
        fields = [
            'tipo_persona',  # Añadido aquí
            'razon_social', 'nombre_comercial_o_nombres', 'ruc_o_cedula', 'rep_legal_cedula_pasaporte',
            'rep_legal_apellido1', 'rep_legal_apellido2', 'rep_legal_nombres', 'direccion_principal',
            'calle', 'numero', 'calle_interseccion', 'referencia', 'edificio', 'piso', 'oficina',
            'parroquia', 'ciudad', 'pais', 'pagina_web', 'correo_empresa', 'telefono1', 'telefono2',
            'telefono3', 'celular', 'tipo_negocio_comercio', 'tipo_negocio_servicios',
            'tipo_negocio_import_export', 'tipo_negocio_industria', 'tipo_negocio_otros',
            'actividad_economica', 'contacto_juridico_correo', 'contacto_juridico_telefono',
            'contacto_natural_correo', 'contacto_natural_telefono', 'titular_nombre', 'titular_telefono',
            'titular_fecha_nacimiento', 'titular_cedula', 'beneficiario1_nombre', 'beneficiario1_porcentaje',
            'beneficiario2_nombre', 'beneficiario2_porcentaje', 'beneficiario3_nombre',
            'beneficiario3_porcentaje', 'firma', 'correo_electronico', 'telefono', 'red_social_whatsapp',
            'red_social_facebook', 'red_social_instagram', 'red_social_youtube', 'red_social_tiktok',
            'comprobante_pago'
        ]
        widgets = {
            'tipo_persona': forms.HiddenInput(),
        }

