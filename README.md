# Firmar un Word

Web en Python y Streamlit para cargar **tu propio archivo Word**, dibujar una firma y descargar una copia firmada. No necesita una plantilla especial ni una base de datos.

La búsqueda inicial es la palabra **firma**: sirve para «Firma», «Firma del docente», «Firma del responsable» y otros rótulos. Ignora mayúsculas y espacios repetidos. Si hay varias coincidencias, elegís una. En **Buscar otro texto** podés indicar otro rótulo.

## Ejecutar en Windows

Requiere Python 3.11 o posterior. Desde esta carpeta:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Abrí http://localhost:8501. Si ya activaste el entorno virtual, también podés usar `streamlit run app.py`.

Las dependencias ya están instaladas en `.venv` en esta copia del proyecto. Para volver a iniciarla, basta el último comando.

## Usar desde el celular

1. Conectá la computadora y el celular a la misma red Wi-Fi.
2. Iniciá la web con:

   ```powershell
   .venv\Scripts\python.exe -m streamlit run app.py --server.address 0.0.0.0
   ```

3. En la computadora, ejecutá `ipconfig` y buscá la dirección IPv4 de Wi-Fi, por ejemplo `192.168.1.20`.
4. En el celular, abrí `http://192.168.1.20:8501`, usando la IP de tu computadora. Si Windows solicita acceso de red para Python, permitilo en la red privada que estés usando.
5. Cargá el Word desde el celular, dibujá la firma y descargá el resultado. La computadora debe permanecer encendida.

Esto permite acceso en la red local. Publicarla en Internet requiere un servidor con HTTPS; este proyecto no incluye un despliegue público ni enlaces individuales para terceros.

## Cómo funciona

- Admite un `.docx` de hasta 10 MB a la vez. El nombre del archivo cargado aparece en la pantalla.
- Busca rótulos en párrafos y tablas del cuerpo, incluidas tablas anidadas y celdas combinadas. La firma va encima del **párrafo** elegido, dentro de la misma celda cuando corresponda.
- El recuadro admite mouse, touchpad y pantalla táctil. «Borrar firma» permite empezar de nuevo.
- La firma se recorta y se inserta como PNG transparente, con proporciones conservadas y un máximo de 5 × 2 cm, reducido para celdas estrechas.
- «Preparar documento firmado» genera una copia; «Descargar Word firmado» la guarda como `nombre_firmado.docx`.
- Cada generación parte del original. Dibujar de nuevo o cambiar la ubicación invalida la descarga anterior. Cambiar de archivo reinicia el proceso.
- Documentos y firmas se mantienen en la memoria de la sesión de Streamlit. La aplicación no los escribe a disco ni los comparte mediante una caché. Al recargar o perder la sesión puede ser necesario volver a cargar el archivo. Streamlit puede retener sesiones desconectadas temporalmente; no se promete borrado instantáneo al cerrar la pestaña.

## Límites

Es una firma manuscrita como imagen, sin certificado criptográfico. No verifica la identidad del firmante ni impide modificaciones posteriores al Word.

No incluye edición del texto, visualización exacta de páginas, PDF, `.doc`, varios firmantes por operación, cuentas o historial. No busca en cuadros de texto, encabezados, pies de página ni controles de contenido. Si dos rótulos están en un mismo párrafo, se consideran una ubicación: separalos en párrafos o celdas en Word para elegirlos por separado.

La inserción puede modificar la paginación. Se procura mantener la firma junto al rótulo; documentos con filas de altura fija, objetos flotantes o diseños especiales pueden necesitar un ajuste en Word. Revisá el resultado descargado.

## Pruebas

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
```

Las pruebas cubren búsqueda general, fragmentos de texto con distintos formatos, tablas anidadas y celdas combinadas, dimensiones de imagen, conservación del rótulo, saltos de página, archivos inválidos y firmas vacías.

Para la comprobación manual: cargar un documento propio, elegir el rótulo correcto, firmar, borrar y repetir, descargar y abrir en Word. Repetir con otro archivo y en el navegador del celular. Comprobar que la firma quede visible sobre el rótulo y que el resto del documento conserve su diseño.
