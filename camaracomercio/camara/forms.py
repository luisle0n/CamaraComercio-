from django import forms
from .models import AfiliacionNatural, AfiliacionJuridica, Convenio, Beneficio, Servicio, Empresa, SolicitudVida

class AfiliacionNaturalForm(forms.ModelForm):
    class Meta:
        model = AfiliacionNatural
        fields = [
            'tipo_persona',
            'nombre_comercial_o_nombres', 'ruc_o_cedula', 'direccion_principal', 'calle', 'numero',
            'calle_interseccion', 'referencia', 'edificio', 'piso', 'oficina', 'parroquia', 'ciudad',
            'pais', 'pagina_web', 'correo_electronico', 'telefono', 'red_social_whatsapp',
            'red_social_facebook', 'red_social_instagram', 'red_social_youtube', 'red_social_tiktok',
            'comprobante_pago'
        ]
        widgets = {
            'tipo_persona': forms.HiddenInput(),
            'direccion_principal': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_ruc_o_cedula(self):
        cedula = self.cleaned_data.get('ruc_o_cedula')
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")
        if len(cedula) != 10:
            raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos.")
        return cedula

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero and not numero.isdigit():
            raise forms.ValidationError("El campo 'Número' debe contener solo números.")
        return numero

    def clean_piso(self):
        piso = self.cleaned_data.get('piso')
        if piso and not piso.isdigit():
            raise forms.ValidationError("El campo 'Piso' debe contener solo números.")
        return piso

class AfiliacionJuridicaForm(forms.ModelForm):
    class Meta:
        model = AfiliacionJuridica
        fields = [
            'tipo_persona',
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
            'direccion_principal': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero and not numero.isdigit():
            raise forms.ValidationError("El campo 'Número' debe contener solo números.")
        return numero

    def clean_piso(self):
        piso = self.cleaned_data.get('piso')
        if piso and not piso.isdigit():
            raise forms.ValidationError("El campo 'Piso' debe contener solo números.")
        return piso

class ConvenioForm(forms.ModelForm):
    class Meta:
        model = Convenio
        fields = [
            'nombre',
            'descripcion',
            'imagen',
            'fecha_fin',
            'categoria',
            'tiene_descuento',
            'porcentaje_descuento',
            'enlace',  # Añadido aquí
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del convenio'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del convenio'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tiene_descuento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'porcentaje_descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': 'Ej: 10.00'}),
            'enlace': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enlace externo (opcional)'}),
        }

class ConvenioEditForm(forms.ModelForm):
    class Meta:
        model = Convenio
        fields = [
            'nombre',
            'descripcion',
            'imagen',
            'fecha_fin',
            'categoria',
            'tiene_descuento',
            'porcentaje_descuento',
            'enlace',  # Añadido aquí
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del convenio'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del convenio'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tiene_descuento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'porcentaje_descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': 'Ej: 10.00'}),
            'enlace': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enlace externo (opcional)'}),
        }

class BeneficioForm(forms.ModelForm):
    class Meta:
        model = Beneficio
        fields = ['descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el beneficio que ofrece este convenio'
            }),
        }

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del servicio'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del servicio'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'Precio'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'direccion', 'telefono', 'tipo_negocio', 'ruc', 'representante']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'tipo_negocio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de negocio'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUC'}),
            'representante': forms.Select(attrs={'class': 'form-select'}),
        }

class ReservaServicioForm(forms.Form):
    fecha_reserva = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Fecha y Hora",
        required=True
    )

class SolicitudVidaForm(forms.ModelForm):
    class Meta:
        model = SolicitudVida
        exclude = ['usuario', 'fecha_solicitud']
        widgets = {
            'estado_civil': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'ocupacion': forms.TextInput(attrs={'class': 'form-control'}),
            'es_empleado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'otros_seguros': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estatura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tension_arterial': forms.TextInput(attrs={'class': 'form-control'}),
            'consume_alcohol': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fuma': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'usa_drogas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'deportes': forms.TextInput(attrs={'class': 'form-control'}),
            'beneficiarios': forms.TextInput(attrs={'class': 'form-control'}),
            'detalles_salud': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

