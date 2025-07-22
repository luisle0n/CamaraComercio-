function setDisabled(containerId, disabled) {
    var container = document.getElementById(containerId);
    if (!container) return;
    var elements = container.querySelectorAll('input, select, textarea');
    elements.forEach(function(el) {
        el.disabled = disabled;
    });
}
function toggleCampos() {
    var tipo = document.getElementById('tipo_usuario').value;
    var personaVisible = tipo === 'persona';
    var empresaVisible = tipo === 'empresa';
    document.getElementById('persona-campos').style.display = personaVisible ? 'block' : 'none';
    document.getElementById('empresa-campos').style.display = empresaVisible ? 'block' : 'none';
    setDisabled('persona-campos', !personaVisible);
    setDisabled('empresa-campos', !empresaVisible);
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('tipo_usuario').addEventListener('change', toggleCampos);
    toggleCampos();

    // Modal y impresión para persona jurídica
    var btnImprimir = document.getElementById('btn-imprimir-juridica');
    if (btnImprimir) {
        btnImprimir.addEventListener('click', function() {
            generarResumenJuridica();
            var modal = new bootstrap.Modal(document.getElementById('modalImprimirJuridica'));
            modal.show();
        });
    }
});

function generarResumenJuridica() {
    var form = document.getElementById('registro-form');
    var fields = form.querySelectorAll('#empresa-campos input, #empresa-campos select, #empresa-campos textarea');
    var html = '<div class="p-3">';
    html += '<h4 class="mb-3 text-primary"><i class="fas fa-building me-2"></i>Resumen de datos de Persona Jurídica</h4>';
    html += '<div class="row">';
    var col = 0;
    fields.forEach(function(field, idx) {
        var label = '';
        var labelEl = form.querySelector('label[for="' + field.id + '"]');
        if (labelEl) label = labelEl.innerText;
        if (field.type !== 'hidden' && field.name !== 'comprobante_pago' && field.value) {
            html += '<div class="col-md-4 mb-3"><strong>' + label + ':</strong><br><span>' + field.value + '</span></div>';
            col++;
        }
    });
    html += '</div>';
    html += '<div class="mt-4 mb-2 text-center"><strong>Firma digital:</strong> <span id="firma-preview"></span></div>';
    html += '</div>';
    document.getElementById('print-content-juridica').innerHTML = html;
}

function printJuridicaForm() {
    var printContents = document.getElementById('print-content-juridica').innerHTML;
    var win = window.open('', '', 'height=700,width=1100');
    win.document.write('<html><head><title>Imprimir Formulario Jurídico</title>');
    win.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">');
    win.document.write('<style>body{padding:30px;} .col-md-4{border:1px solid #e9ecef;border-radius:8px;background:#f8f9fa;page-break-inside:avoid;}</style>');
    win.document.write('</head><body>');
    win.document.write('<div class="container"><div class="row">' + printContents + '</div></div>');
    win.document.write('</body></html>');
    win.document.close();
    win.focus();
    win.print();
}

function guardarFirma() {
    var firma = document.getElementById('firma-digital').value;
    document.getElementById('firma-preview').innerText = firma ? firma : 'Sin firma';
}
