# VideoTranscriptor

VideoTranscriptor es una herramienta de Python para transcribir audio de videos de YouTube, Google Drive o archivos locales. La herramienta extrae el audio de los videos, lo transcribe utilizando el modelo de transcripción Whisper y guarda los resultados de la transcripción en un archivo de texto o documento.

## Requisitos

- Python 3.7 o superior
- Bibliotecas de Python: `os`, `logging`, `enum`, `pathlib`, `pydub`, `yt_dlp`, `whisper`, `pydrive`

## Instalación

Para instalar las dependencias necesarias, ejecute el siguiente comando:

```bash
pip install pydub yt-dlp whisper pydrive
```

## Uso

Primero, importe la clase `VideoTranscriptor` de su script:

```python
from video_transcriptor import VideoTranscriptor
```

Luego, cree una instancia de `VideoTranscriptor` y llame al método `process`:

```python
transcriptor = VideoTranscriptor(source_type='youtube', source_format='one', source_id='VIDEO_ID')
transcriptor.process()
```

Los parámetros para el constructor de `VideoTranscriptor` son:

- `source_type`: El tipo de fuente para la transcripción. Puede ser 'youtube', 'drive' o 'local'.
- `source_format`: El formato de la fuente para la transcripción. Puede ser 'one' o 'multiple'.
- `source_id`: El ID de la fuente. Por defecto es None.
- `intermediate_folder`: La carpeta para almacenar archivos intermedios. Por defecto es 'temp'.
- `audio_file_type`: El tipo de archivo de audio para la transcripción. Por defecto es AudioFileType.MP3.
- `keep_intermediate_files`: Si se deben mantener los archivos intermedios. Por defecto es True.
- `transcription_model`: El modelo de transcripción a utilizar. Por defecto es TranscriptionModel.WHISPER.
- `transcription_quality`: El nivel de calidad para la transcripción de audio. Por defecto es TranscriptionQuality.BASE.
- `output_folder`: La carpeta para almacenar la salida de la transcripción. Por defecto es 'output'.
- `output_format`: El formato de la salida de la transcripción. Por defecto es OutputFormat.TXT.

## Contribución

Las contribuciones son bienvenidas. Por favor, abra un problema para discutir lo que le gustaría cambiar o enviar una solicitud de extracción.

## Licencia

[MIT](https://choosealicense.com/licenses/mit/)