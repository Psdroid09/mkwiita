# Conversor automático MKWiita PSD09 (Windows)

Esta edición facilita convertir **tu propia copia de Mario Kart Wii USA**
(ID `RMCE01`) en los datos que requiere MKWiita para PS Vita.

## Cómo usarlo

1. Instala una sola vez [Python 3.11+](https://www.python.org/downloads/),
   [Node.js LTS](https://nodejs.org/) y [Git](https://git-scm.com/downloads/).
   En Python, activa la opción **Add python.exe to PATH**.
2. Descarga el ZIP de la rama `opt/psd09-framebuffer-gpu-profile` de este
   repositorio y descomprímelo por completo.
3. Asegúrate de tener **15 GiB libres en la unidad donde descomprimiste el
   proyecto**. No hace falta VitaSDK ni Visual Studio para los *datos*.
4. Haz doble clic en **`Build Game Files.bat`**. En el selector, elige tu ISO
   convencional o WBFS de Mario Kart Wii USA. También puedes arrastrar el
   ISO encima del archivo `.bat`.
5. El programa comprobará el encabezado `RMCE01`, descargará dependencias
   públicas, instalará librerías Python dentro de `.venv`, y ejecutará la
   conversión original de MKWiita, **incluidas sus verificaciones de hashes**.
   La primera ejecución suele tardar entre 30 y 60 minutos o más.
6. Cuando aparezca **CONVERSION COMPLETADA**, abre
   `build\vita\data\mkw\`. Copia **el contenido** de esa carpeta a
   `ux0:data/mkw/` con VitaShell.
7. Descarga el VPK ya compilado en [GitHub Actions](https://github.com/Psdroid09/mkwiita/actions/runs/38489940473)
   (sección **Artifacts**, archivo `MKWiita-PSD09-experimental-VPK`).
   Descomprime el ZIP para obtener `mkw.vpk` e instálalo con VitaShell.
   Debes tener `ur0:data/libshacccg.suprx` y espacio suficiente en la Vita.

## Si el CMD se cierra o falla

La versión PSD09 espera una tecla antes de cerrarse **también después de un
error**. Conserva el registro en `build-assets-log.txt` (en la carpeta raíz
del proyecto). Envía el texto final del registro para diagnosticar el problema.

- **Archivo NKit / RVZ:** no basta renombrar la extensión a `.iso`. El
  conversor necesita ISO normal/WBFS; si el archivo conserva la marca NKit,
  se detendrá para evitar resultados incorrectos.
- **Región:** únicamente `RMCE01`. Un archivo modificado, otra región o
  una extracción incompleta puede ser rechazado por la validación completa.
- **Python/Node/Git:** si falta alguno, instala la herramienta de la URL
  mostrada, cierra CMD y vuelve a iniciar el `.bat`.
- **Reanudar:** usa el mismo archivo de disco y carpeta del proyecto.
  Las etapas completadas normalmente se reutilizan; no borres `build`
  ni `vendor` sin motivo.

La ISO y los datos generados permanecen en tu PC. **No los subas al
repositorio**: contienen material del juego. El VPK solo incluye código
compilado y no los datos de Nintendo.

## Estado

El convertidor está añadido al repositorio y sujeto a las validaciones
automáticas de sus funciones básicas. La conversión completa con un ISO
real debe ejecutarse y comprobarse en Windows; no se ha realizado aquí.
