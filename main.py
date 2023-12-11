import os
from pydub import AudioSegment
import yt_dlp
import whisper
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class VideoTranscriptor:
    def __init__(self, source_type, source_format, source_id=None, intermediate_folder='temp', audio_file_type='mp3', keep_intermediate_files=True, transcription_model='whisper', transcription_quality='base', output_folder='output', output_format='txt'):
        assert source_type in ['youtube', 'drive', 'local'], "source must be either 'youtube', 'drive' or 'local'"
        assert source_format in ['one', 'multiple'], "source_type must be 'one' or 'multiple'"
        assert audio_file_type in ['mp3', 'wav'], "audio_file_type must be either 'mp3' or 'wav'"
        assert keep_intermediate_files in [True, False], "keep_intermediate_files must be either True or False"
        assert transcription_model in ['whisper'], "For now the only transcription model available is 'whisper"
        assert transcription_quality in ['base', 'medium','large'], "quality must be either 'base', 'medium', or 'large'"
        assert output_format in ['txt', 'doc'], "output_format must be either 'txt' or 'doc'"

        self.source_id = source_id
        self.source_type = source_type
        self.source_format = source_format
        self.intermediate_folder = intermediate_folder
        self.audio_file_type = audio_file_type
        self.keep_intermediate_files = keep_intermediate_files
        self.transcription_model = transcription_model
        self.transcription_quality = transcription_quality
        self.output_folder = output_folder
        self.output_format = output_format
    
    def process_link(self):
        if self.source_type == 'drive':
            self.authenticate_drive()

            if self.source_format == 'one':
                # Obtener el título del video
                self.extract_google_audio(self.source_id)
            
            elif self.source_format == 'multiple':
                self.process_drive_directory(self.source_id)
        
        elif self.source_type == 'youtube':
            self.extract_google_audio(self.source_id)

        elif self.source_type == 'local':
            if self.source_format == 'one':
                self.extract_local_audio(f'./input/{self.source_id}')
            
            elif self.source_format == 'multiple':
                for root, dirs, files in os.walk(f'./input/{self.source_id}'):
                    for file in files:
                        if file.endswith(('.mp4', '.avi', '.mov')):  # add or modify the file extensions as needed
                            self.extract_local_audio(os.path.join(root, file))

            return

    def authenticate_drive(self):
        #### TODO: Authentication with Google Drive
        gauth = GoogleAuth()
        self.drive = GoogleDrive(gauth)

        return

    def write_query(self, folder_id, file_type):
        return f"'{folder_id}' in parents and (mimeType contains '{file_type}/')"

    def process_drive_directory(self, folder_id):
        # Obtener la lista de archivos
        file_list = self.drive.ListFile({'q': self.write_query(folder_id,"video")}).GetList()

        # Imprimir los IDs de los archivos
        for file in file_list:
            self.extract_google_audio(file['id'])

        # Obtener la lista de archivos
        file_list = self.drive.ListFile({'q': self.write_query(folder_id,"audio")}).GetList()

        # Imprimir los IDs de los archivos
        for file in file_list:
            # Descargar el archivo
            file.GetContentFile(f'./{self.intermediate_folder}/{file["title"]}')
        
        # Obtener la lista de subcarpetas
        folder_list = self.drive.ListFile({'q': self.write_query(folder_id, "application/vnd.google-apps.folder")}).GetList()

        # Recorrer cada subcarpeta y listar los archivos en ellas
        for folder in folder_list:
            self.process_drive_directory(folder['id'])
                
    def extract_google_audio(self, video_id):
        # Obtener el enlace de descarga del video
        if self.source_type == 'youtube':
            if self.source_format == 'one':
                video_url = f'https://www.youtube.com/watch?v={video_id}'
            elif self.source_format == 'multiple':
                video_url = f'https://www.youtube.com/playlist?list={video_id}'

        elif self.source_type == 'drive':
            video_url = f'https://drive.google.com/uc?id={video_id}'
        
        # Descargar el audio utilizando yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_file_type,
                'preferredquality': '192'
            }],
            'outtmpl': f'./{self.intermediate_folder}/%(title)s.%(ext)s',  # Ruta y nombre del archivo de salida de audio
            #'outtmpl': f'./{self.intermediate_folder}/{video_title}'  # Ruta y nombre del archivo de salida de audio
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        return

    def extract_local_audio(self, video_path):
        # Extraer el nombre del video
        video_name = os.path.splitext(os.path.split(video_path)[-1])[0]

        # Cargar el archivo de video
        video = AudioSegment.from_file(video_path)

        # Ruta de salida del archivo de audio
        audio_output_path = f'./{self.intermediate_folder}/{video_name}.{self.audio_file_type}'

        # Exportar el archivo de audio
        video.export(audio_output_path, format=f"{self.audio_file_type}")

        return

    def transcribe_audio(self):
        if self.transcription_model == 'whisper':
            model = whisper.load_model(self.transcription_quality)

        # Recorrer los archivos de audio en la carpeta temporal
        for file in os.listdir(f'./{self.intermediate_folder}'):
            # Obtener el nombre del archivo
            file_name = os.path.splitext(file)[0]

            # Obtener la ruta del archivo
            file_path = f'./{self.intermediate_folder}/{file}'
            
            # Cargar el audio
            audio = AudioSegment.from_mp3(file_path)

            # Dividir el audio en segmentos de 20 minutos
            audio_chunks = [audio[i:i + 1200000] for i in range(0, len(audio), 1200000)]

            with open(f'./{self.output_folder}/{file_name}.{self.output_format}', 'w') as f:
    
                for i, chunk in enumerate(audio_chunks):
                    temp_file_name = f'./{self.intermediate_folder}/{file_name}-chunk{i+1}.{self.audio_file_type}'
                    
                    # Exportar el segmento de audio
                    chunk.export(temp_file_name, format=self.audio_file_type)

                    result = model.transcribe(temp_file_name, fp16=False)

                    f.write(result["text"])
                    f.write("\n")  # Agrega un salto de línea entre cada transcripción

                    os.remove(temp_file_name)
                    
        return
    
    def clean_up(self):
        # Código para eliminar los archivos temporales
        if self.keep_intermediate_files == False:
            for file in os.listdir(f'./{self.intermediate_folder}'):
                os.remove(f'./{self.intermediate_folder}/{file}')
        return
    
    def process(self):
        self.process_link()
        self.transcribe_audio()
        self.clean_up()

