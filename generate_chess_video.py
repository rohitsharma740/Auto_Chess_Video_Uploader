import os
import io
import json
import time
import cv2
import numpy as np
import requests
import chess
import chess.pgn
import chess.svg
from PIL import Image
from datetime import datetime
from io import BytesIO
import tempfile
import subprocess

# Fetch Chess.com game data
username = "rohitsharma740431"
current_year = datetime.now().year
current_month = str(datetime.now().month).zfill(2)
url = f"https://api.chess.com/pub/player/{username}/games/{current_year}/{current_month}"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
except requests.RequestException as e:
    print("❌ Failed to fetch data:", e)
    data = None
except json.JSONDecodeError:
    print("❌ Error decoding JSON response!")
    data = None

if not data or "games" not in data or not data["games"]:
    print("❌ No games found!")
else:
    # Extract moves from the latest game
    latest_game = data["games"][-1]
    pgn_text = latest_game.get("pgn", "").strip()
    if not pgn_text:
        print("❌ PGN data is empty!")
    else:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            print("❌ Error parsing PGN!")
        else:
            board = game.board()
            frames = []

            # Convert SVG to PNG manually without CairoSVG
            def svg_to_png(svg_code):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_svg:
                        temp_svg.write(svg_code.encode("utf-8"))
                        temp_svg_path = temp_svg.name
                    
                    temp_png_path = temp_svg_path.replace(".svg", ".png")
                    
                    command = ["inkscape", temp_svg_path, "--export-filename", temp_png_path]
                    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    return Image.open(temp_png_path)
                except FileNotFoundError:
                    print("❌ Inkscape is not installed. Please install it or ensure it is in your system PATH.")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error executing Inkscape: {e}")
                except Exception as e:
                    print(f"❌ Error converting SVG to PNG: {e}")
                return None

            # Process each move
            for move in game.mainline_moves():
                board.push(move)
                board_svg = chess.svg.board(board)
                img = svg_to_png(board_svg)
                if img:
                    frames.append(img)

            if not frames:
                print("❌ No frames generated! Check if Inkscape is installed and working correctly.")
            else:
                # Convert images to a video using OpenCV
                frame_width, frame_height = frames[0].size
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video = cv2.VideoWriter("chess_game.mp4", fourcc, 2, (frame_width, frame_height))

                for frame in frames:
                    img_array = np.array(frame)
                    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    video.write(img_bgr)

                video.release()
                print("✅ Video created: chess_game.mp4")

                # Add background music using FFmpeg
                try:
                    command = [
                        'ffmpeg', '-i', 'chess_game.mp4', '-i', 'background.mp3', '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', 'chess_short.mp4'
                    ]
                    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print("✅ Chess video generated successfully: chess_short.mp4")
                except FileNotFoundError:
                    print("❌ FFmpeg is not installed. Please install it or ensure it is in your system PATH.")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error executing FFmpeg: {e}")
                except Exception as e:
                    print(f"❌ Error adding audio: {e}")
