# Transcripción

Una herramienta de Python para extraer audio de videos de YouTube, Google Drive o archivos locales y transcribirlo con Whisper.

**Estado: herramienta histórica, con dependencias fijadas en 2023.** La documentación se corrigió para reflejar los nombres del código. No se verificó de nuevo la integración con servicios externos.

## Preparar el entorno

Requiere Python y FFmpeg disponible en el sistema.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

La integración con Google Drive usa PyDrive y necesita su propia configuración OAuth fuera del repositorio.

## Ejemplo de uso

El archivo es `main.py` y la clase se llama `Transcriptor`.

```python
from main import Transcriptor

transcriptor = Transcriptor(
    source_type="youtube",
    source_format="one",
    source_id="VIDEO_ID",
)
transcriptor.process()
```

El código contempla archivos individuales o múltiples, entradas locales y Drive y salida de transcripciones. Las opciones están definidas en los enums de `main.py`.

## Qué sigue abierto

Volver a comprobar descargas, autenticación y compatibilidad de dependencias antes de usarlo con material nuevo.

[Más exploraciones](https://github.com/tomasrene/exploraciones) · [Mi web](https://tomasrene.com)
