from flask import Flask, request, send_file
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import requests
import io
import os

app = Flask(__name__)

@app.route("/merge", methods=["POST"])
def merge_video():
    data = request.json
    background_url = data.get("background_url")
    video_url = data.get("video_url")
    x = int(data.get("x", 0))
    y = int(data.get("y", 0))
    mask_color = data.get("mask_color", [255, 0, 255])  # default: pink

    # Dateien herunterladen
    bg_bytes = requests.get(background_url).content
    vid_bytes = requests.get(video_url).content

    with open("temp_bg.png", "wb") as f:
        f.write(bg_bytes)
    with open("temp_vid.mp4", "wb") as f:
        f.write(vid_bytes)

    # Clips laden
    background = ImageClip("temp_bg.png").set_duration(5)
    overlay = VideoFileClip("temp_vid.mp4").fx(
        lambda clip: clip.remove_color(tuple(mask_color), thr=100, s=5)
    ).set_position((x, y))

    # Dauer angleichen
    background = background.set_duration(overlay.duration)

    # Video kombinieren
    final = CompositeVideoClip([background, overlay])
    final.write_videofile("output.mp4", codec="libx264")

    return send_file("output.mp4", as_attachment=True, download_name="merged_video.mp4")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
