# VideoTranscriptor

VideoTranscriptor es una clase de Python que permite transcribir audios de videos de YouTube, Google Drive o locales. La transcripción se realiza utilizando el modelo de transcripción 'whisper'.

## Requisitos

- Python 3.6+
- Librerías: os, pydub, yt_dlp, whisper, pydrive

## Instalación

Para instalar las dependencias, ejecute el siguiente comando:

```bash
pip install pydub yt-dlp whisper pydrive
```

## Uso

Para utilizar la clase VideoTranscriptor, primero debe instanciarla con los parámetros deseados. A continuación, se muestra un ejemplo de cómo hacerlo:

```python
transcriptor = VideoTranscriptor(
    source_type='youtube', 
    source_format='one', 
    source_id='video_id', 
    intermediate_folder='temp', 
    audio_file_type='mp3', 
    keep_intermediate_files=True, 
    transcription_model='whisper', 
    transcription_quality='base', 
    output_folder='output', 
    output_format='txt'
)
```

Luego, puede llamar al método `process()` para iniciar el proceso de transcripción:

```python
transcriptor.process()
```

## Parámetros

- `source_type`: Tipo de fuente del video. Puede ser 'youtube', 'drive' o 'local'.
- `source_format`: Formato de la fuente. Puede ser 'one' para un solo video o 'multiple' para múltiples videos.
- `source_id`: ID del video o carpeta de videos. No es necesario para videos locales.
- `intermediate_folder`: Carpeta para almacenar archivos intermedios.
- `audio_file_type`: Tipo de archivo de audio a generar. Puede ser 'mp3' o 'wav'.
- `keep_intermediate_files`: Si es True, se conservarán los archivos intermedios. Si es False, se eliminarán.
- `transcription_model`: Modelo de transcripción a utilizar. Actualmente, solo se admite 'whisper'.
- `transcription_quality`: Calidad de la transcripción. Puede ser 'base', 'medium' o 'large'.
- `output_folder`: Carpeta para almacenar los archivos de transcripción.
- `output_format`: Formato de los archivos de transcripción. Puede ser 'txt' o 'doc'.

## Métodos

- `process_link()`: Procesa el enlace de la fuente.
- `authenticate_drive()`: Autentica con Google Drive.
- `write_query(folder_id, file_type)`: Escribe una consulta para Google Drive.
- `process_drive_directory(folder_id)`: Procesa una carpeta de Google Drive.
- `extract_google_audio(video_id)`: Extrae el audio de un video de Google.
- `extract_local_audio(video_path)`: Extrae el audio de un video local.
- `transcribe_audio()`: Transcribe el audio.
- `clean_up()`: Limpia los archivos intermedios.
- `process()`: Inicia el proceso de transcripción.

## Nota

Este código aún está en desarrollo y puede contener errores. Por favor, utilícelo con precaución.