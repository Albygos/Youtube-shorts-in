import os
import uuid
import subprocess
from yt_dlp import YoutubeDL

def process_video(url, start_time, duration, output_dir):
    job_id = str(uuid.uuid4())
    download_path = os.path.join(output_dir, f"{job_id}_raw.mp4")
    output_path = os.path.join(output_dir, f"{job_id}_short.mp4")

    # 1. Download video directly to disk
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': download_path,
        'quiet': True,
        'noplaylist': True
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    # 2. Pure FFmpeg (Uses <50MB RAM) to crop 9:16 and trim length
    ffmpeg_cmd = [
        "ffmpeg", 
        "-ss", str(start_time),
        "-i", download_path,
        "-t", str(duration),
        "-vf", "crop=ih*(9/16):ih", 
        "-c:v", "libx264",
        "-c:a", "aac",
        "-threads", "1",  # Restrict threads to keep Render CPU happy
        "-y", 
        output_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        if os.path.exists(download_path):
            os.remove(download_path)
        raise Exception("FFmpeg processing failed.")

    # 3. Clean up the big raw video to save disk space
    if os.path.exists(download_path):
        os.remove(download_path)

    return output_path
