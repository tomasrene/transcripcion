import os
import logging
from enum import Enum
from pathlib import Path
from pydub import AudioSegment
import yt_dlp
import whisper
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SourceType(Enum):
    """
    Enum class representing the source types for transcription.
    """
    YOUTUBE = 'youtube'
    DRIVE = 'drive'
    LOCAL = 'local'

class SourceFormat(Enum):
    """
    Enum class representing the source formats for transcription.
    """
    ONE = 'one'
    MULTIPLE = 'multiple'

class AudioFileType(Enum):
    """
    Enum class representing the audio file types for transcription.
    """
    MP3 = 'mp3'
    WAV = 'wav'

class TranscriptionModel(Enum):
    """
    Enum class representing the transcription models for audio transcription.
    """
    WHISPER = 'whisper'

class TranscriptionQuality(Enum):
    """
    Enum class representing the transcription quality levels for audio transcription.
    """
    BASE = 'base'
    MEDIUM = 'medium'
    LARGE = 'large'

class OutputFormat(Enum):
    """
    Enum class representing the output formats for transcription results.
    """
    TXT = 'txt'
    DOC = 'doc'


class VideoTranscriptor:
    def __init__(self, source_type, source_format, source_id=None, intermediate_folder='temp', audio_file_type=AudioFileType.MP3, keep_intermediate_files=True, transcription_model=TranscriptionModel.WHISPER, transcription_quality=TranscriptionQuality.BASE, output_folder='output', output_format=OutputFormat.TXT):
        """
        Initializes the VideoTranscriptor object.

        Args:
            source_type (str): The type of source for transcription.
            source_format (str): The format of the source for transcription.
            source_id (str, optional): The ID of the source. Defaults to None.
            intermediate_folder (str, optional): The folder to store intermediate files. Defaults to 'temp'.
            audio_file_type (AudioFileType, optional): The type of audio file for transcription. Defaults to AudioFileType.MP3.
            keep_intermediate_files (bool, optional): Whether to keep intermediate files. Defaults to True.
            transcription_model (TranscriptionModel, optional): The transcription model to use. Defaults to TranscriptionModel.WHISPER.
            transcription_quality (TranscriptionQuality, optional): The quality level for audio transcription. Defaults to TranscriptionQuality.BASE.
            output_folder (str, optional): The folder to store the transcription output. Defaults to 'output'.
            output_format (OutputFormat, optional): The format of the transcription output. Defaults to OutputFormat.TXT.
        """
        self.source_id = source_id
        self.source_type = SourceType(source_type)
        self.source_format = SourceFormat(source_format)
        self.intermediate_folder = Path(intermediate_folder)
        self.audio_file_type = audio_file_type
        self.keep_intermediate_files = keep_intermediate_files
        self.transcription_model = transcription_model
        self.transcription_quality = transcription_quality
        self.output_folder = Path(output_folder)
        self.output_format = output_format
        self.drive = None

    def process_source(self):
        """
        Processes the source for transcription.
        """
        try:
            logging.info("Processing source...")
            if self.source_type == SourceType.DRIVE:
                self.authenticate_drive()

                if self.source_format == SourceFormat.ONE:
                    self.extract_google_audio(self.source_id)
                
                elif self.source_format == SourceFormat.MULTIPLE:
                    self.process_drive_directory(self.source_id)
            
            elif self.source_type == SourceType.YOUTUBE:
                self.extract_google_audio(self.source_id)

            elif self.source_type == SourceType.LOCAL:
                self.process_local_files()

            logging.info("Source processing completed.")
        except Exception as e:
            logging.error("Error processing source: %s", e)
            raise

    def authenticate_drive(self):
        """
        Authenticates with Google Drive.
        """
        try:
            logging.info("Authenticating with Google Drive...")
            gauth = GoogleAuth()
            self.drive = GoogleDrive(gauth)
            logging.info("Google Drive authentication successful.")
        except Exception as e:
            logging.error("Error authenticating with Google Drive: %s", e)
            raise

    def write_query(self, folder_id, file_type):
        """
        Writes a query for retrieving files from Google Drive.

        Args:
            folder_id (str): The ID of the folder.
            file_type (str): The type of file.

        Returns:
            str: The query string.
        """
        return f"'{folder_id}' in parents and (mimeType contains '{file_type}/')"

    def process_drive_directory(self, folder_id):
        """
        Processes a directory in Google Drive.

        Args:
            folder_id (str): The ID of the folder.
        """
        try:
            logging.info("Processing Google Drive directory...")
            self.process_drive_files(folder_id, "video")
            self.process_drive_files(folder_id, "audio")
            self.process_drive_subfolders(folder_id)
            logging.info("Google Drive directory processing completed.")
        except Exception as e:
            logging.error("Error processing Google Drive directory: %s", e)
            raise

    def process_drive_files(self, folder_id, file_type):
        """
        Processes files in a Google Drive folder.

        Args:
            folder_id (str): The ID of the folder.
            file_type (str): The type of file.
        """
        file_list = self.drive.ListFile({'q': self.write_query(folder_id, file_type)}).GetList()
        for file in file_list:
            if file_type == "video":
                self.extract_google_audio(file['id'])
            elif file_type == "audio":
                file.GetContentFile(self.intermediate_folder / file["title"])

    def process_drive_subfolders(self, folder_id):
        """
        Processes subfolders in a Google Drive folder.

        Args:
            folder_id (str): The ID of the folder.
        """
        folder_list = self.drive.ListFile({'q': self.write_query(folder_id, "application/vnd.google-apps.folder")}).GetList()
        for folder in folder_list:
            self.process_drive_directory(folder['id'])

    def extract_google_audio(self, video_id):
        """
        Extracts audio from a Google Drive or YouTube video.

        Args:
            video_id (str): The ID of the video.
        """
        try:
            logging.info("Extracting audio from Google video...")
            video_url = self.get_video_url(video_id)
            self.download_audio(video_url)
            logging.info("Audio extraction completed.")
        except Exception as e:
            logging.error("Error extracting Google audio: %s", e)
            raise

    def get_video_url(self, video_id):
        """
        Gets the URL of a video based on the source type and format.

        Args:
            video_id (str): The ID of the video.

        Returns:
            str: The video URL.
        """
        if self.source_type == SourceType.YOUTUBE:
            if self.source_format == SourceFormat.ONE:
                return f'https://www.youtube.com/watch?v={video_id}'
            elif self.source_format == SourceFormat.MULTIPLE:
                return f'https://www.youtube.com/playlist?list={video_id}'
        elif self.source_type == SourceType.DRIVE:
            return f'https://drive.google.com/uc?id={video_id}'

    def download_audio(self, video_url):
        """
        Downloads the audio from a video.

        Args:
            video_url (str): The URL of the video.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_file_type.value,
                'preferredquality': '192'
            }],
            'outtmpl': str(self.intermediate_folder / '%(title)s.%(ext)s')
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

    def process_local_files(self):
        """
        Processes local files for transcription.
        """
        try:
            path = f'./input/{self.source_id}'
            if not os.path.exists(path):
                logging.error("Path does not exist: %s", path)
                return
            if os.path.isfile(path):
                logging.error("Expected a directory, but found a file: %s", path)
                return
            if not os.listdir(path):
                logging.error("Directory is empty: %s", path)
                return

            logging.info("Processing local files...")
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.mp4', '.avi', '.mov')):
                        self.extract_local_audio(Path(root) / file)
            logging.info("Local file processing completed.")
        except FileNotFoundError:
            logging.error("File not found: %s", path)
        except IsADirectoryError:
            logging.error("Expected a file, but found a directory: %s", path)
        except PermissionError:
            logging.error("Permission denied: %s", path)
        except Exception as e:
            logging.error("Error processing local files: %s", e)
            raise

    def extract_local_audio(self, video_path):
        """
        Extracts audio from a local video file.

        Args:
            video_path (str): The path to the video file.
        """
        try:
            logging.info("Extracting audio from local video...")
            video_name = video_path.stem
            video = AudioSegment.from_file(video_path)
            audio_output_path = self.intermediate_folder / f'{video_name}'
            video.export(audio_output_path, format=f"{self.audio_file_type.value}")
            logging.info("Audio extraction completed.")
        except Exception as e:
            logging.error("Error extracting local audio: %s", e)
            raise

    def transcribe_audio(self):
        """
        Transcribes the audio files using the selected transcription model.

        Returns:
            None
        """
        try:
            if not any(self.intermediate_folder.iterdir()):
                logging.error("No files found in the intermediate folder.")
                return

            logging.info("Transcribing audio...")
            if self.transcription_model == TranscriptionModel.WHISPER:
                model = whisper.load_model(self.transcription_quality.value)

            for file in self.intermediate_folder.iterdir():
                self.transcribe_file(file, model)
            logging.info("Audio transcription completed.")
        except FileNotFoundError:
            logging.error("File not found: %s", file)
        except IsADirectoryError:
            logging.error("Expected a file, but found a directory: %s", file)
        except PermissionError:
            logging.error("Permission denied: %s", file)
        except Exception as e:
            logging.error("Error transcribing audio: %s", e)
            raise

    def transcribe_file(self, file, model):
        """
        Transcribes a single audio file using the selected model.

        Args:
            file (str): The path to the audio file. Expected to be a .mp3 file.
            model (whisper.Model): The transcription model.

        Returns:
            None
        """
        try:
            file_name = file.stem
            audio = AudioSegment.from_mp3(file)
            audio_chunks = [audio[i:i + 1200000] for i in range(0, len(audio), 1200000)]

            with open(self.output_folder / f'{file_name}.{self.output_format.value}', 'w', encoding='utf-8') as f:
                for i, chunk in enumerate(audio_chunks):
                    temp_file_name = f'./{self.intermediate_folder}/{file_name}-chunk{i+1}'
                    chunk.export(temp_file_name, format=self.audio_file_type.value)
                    result = model.transcribe(temp_file_name, fp16=False)
                    f.write(result["text"])
                    f.write("\n")
                    os.remove(temp_file_name)
        except FileNotFoundError:
            logging.error("File not found: %s", file)
        except IsADirectoryError:
            logging.error("Expected a file, but found a directory: %s", file)
        except PermissionError:
            logging.error("Permission denied: %s", file)
        except Exception as e:
            logging.error("Error transcribing file: %s", e)
            raise

    def clean_up(self):
        """
        Cleans up the intermediate files if keep_intermediate_files is set to False.
        """
        if not self.keep_intermediate_files:
            for file in self.intermediate_folder.iterdir():
                file.unlink()

    def process(self):
        """
        Processes the source, transcribes the audio, and performs clean-up.
        """
        logging.info("Process started.")
        self.process_source()
        self.transcribe_audio()
        self.clean_up()
        logging.info("Process completed.")
