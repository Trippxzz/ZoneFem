function mostrarPreviewYRadios() {
    const input = document.getElementById('id_imagenes');
    const preview = document.getElementById('preview_imagenes');
    preview.innerHTML = '';
    const files = input.files;
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();
        const div = document.createElement('div');
        div.style.display = 'inline-block';
        div.style.margin = '10px';
        // Radio para marcar principal. Por defecto, la primera está seleccionada
        div.innerHTML = `<input type='radio' name='principal_radio' value='${i}' ${i===0?'checked':''} onchange='document.getElementById("imgprincipal").value=${i}'> Principal<br>`;
        reader.onload = function(e) {
            div.innerHTML += `<img src='${e.target.result}' style='max-width:100px;max-height:100px;display:block;'>`;
        };
        reader.readAsDataURL(file);
        preview.appendChild(div);
    }
    // Si el usuario cambia el radio, actualiza el input hidden
    document.querySelectorAll("input[name='principal_radio']").forEach(radio => {
        radio.addEventListener('change', function() {
            document.getElementById('imgprincipal').value = this.value;
        });
    });
}