import youtube_dl
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from utils.translator import translate_text, text_to_speech
import os
import speech_recognition as sr

def download_video(url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict.get('title', 'video')

def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

def transcribe_audio(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        raise Exception("Could not understand audio")
    except sr.RequestError:
        raise Exception("Could not request results from speech recognition service")

def create_subtitle_file(text, output_path):
    # Simplified subtitle creation - in real app would include timing
    with open(output_path, 'w') as f:
        f.write(text)

def process_video(youtube_url, languages, output_dir, generate_subtitles=True, generate_dubbed=False, preserve_original=True):
    # Step 1: Download video
    video_path = os.path.join(output_dir, 'original.mp4')
    video_title = download_video(youtube_url, video_path)
    
    # Step 2: Extract and transcribe audio
    audio_path = os.path.join(output_dir, 'original_audio.wav')
    extract_audio(video_path, audio_path)
    original_text = transcribe_audio(audio_path)
    
    results = []
    
    for lang in languages:
        lang_results = {'language': lang, 'subtitle_path': None, 'dubbed_path': None}
        
        # Step 3: Translate text
        translated_text = translate_text(original_text, lang)
        
        # Step 4: Generate subtitles if requested
        if generate_subtitles:
            subtitle_path = os.path.join(output_dir, f'subtitles_{lang}.srt')
            create_subtitle_file(translated_text, subtitle_path)
            lang_results['subtitle_path'] = f'subtitles_{lang}.srt'
        
        # Step 5: Generate dubbed audio if requested
        if generate_dubbed:
            dubbed_audio_path = os.path.join(output_dir, f'dubbed_{lang}.mp3')
            text_to_speech(translated_text, lang, dubbed_audio_path)
            
            # Combine with original video
            video_clip = VideoFileClip(video_path)
            
            if preserve_original:
                # Mix original and dubbed audio
                original_audio = AudioFileClip(audio_path)
                dubbed_audio = AudioFileClip(dubbed_audio_path)
                final_audio = CompositeAudioClip([original_audio.volumex(0.3), dubbed_audio.volumex(0.7)])
            else:
                # Use only dubbed audio
                final_audio = AudioFileClip(dubbed_audio_path)
            
            final_clip = video_clip.set_audio(final_audio)
            output_video_path = os.path.join(output_dir, f'output_{lang}.mp4')
            final_clip.write_videofile(output_video_path, codec='libx264')
            
            lang_results['dubbed_path'] = f'output_{lang}.mp4'
        
        results.append(lang_results)
    
    return {
        'video_title': video_title,
        'results': results
    }
