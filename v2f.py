import cv2
import os
from moviepy.editor import *

#VidStitcher Created by Andro.Meta

# For audio and video extraction to be in HH:MM:SS
def time_to_seconds(time_str):
    """Convert HH:MM:SS format to seconds."""
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

#Progress Bar
def print_progress_bar(iteration, total, bar_length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(progress * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    print('\rProgress: [%s%s] %d%%' % (arrow, spaces, int(round(progress * 100))), end='')

def video_to_frames(video_path, fps=None, start_time=None, end_time=None):
    # Create a VideoCapture object
    vidcap = cv2.VideoCapture(video_path)
    
    # Check if video opened successfully
    if not vidcap.isOpened():
        print("Error: Cannot open video.")
        return

    # Get original FPS if not provided
    if fps is None:
        fps = int(vidcap.get(cv2.CAP_PROP_FPS))

    # Calculate frame skip rate
    frame_skip = int(fps / fps)  # Note: This will always be 1. You might want to use the original FPS here.

    # Calculate start and end frames
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    start_frame = int(start_time * fps) if start_time else 0
    end_frame = int(end_time * fps) if end_time else total_frames

    # Determine the number of digits required for naming
    num_digits = len(str(total_frames))

    # Extract video filename without extension
    video_filename = os.path.basename(video_path).rsplit('.', 1)[0]

    # Create output folder named after the video file and FPS
    output_folder_name = f"{video_filename}_fps{fps}"
    output_folder = os.path.join(os.path.dirname(video_path), output_folder_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    count = 0
    success = True
    while success:
        success, image = vidcap.read()
        if count % frame_skip == 0 and start_frame <= count <= end_frame:
            # Save the frame with consistent naming
            cv2.imwrite(os.path.join(output_folder, f"frame{count:0{num_digits}d}.png"), image)
        # Update the progress bar
        print_progress_bar(count, total_frames)
        count += 1

    vidcap.release()
    print(f"\nFrames extracted to {output_folder}")
    
def frames_to_video(input_folder, output_video_filename, fps):
    images = [img for img in os.listdir(input_folder) if img.endswith(".png")]
    
    # Check if the images list is empty
    if not images:
        print("No .png images found in the specified directory.")
        return

    # Sort images
    try:
        images.sort(key=lambda x: int(x[5:-4]))  # Assuming the format is "frame<number>.png"
    except ValueError:
        print("Error: Image filenames do not follow the expected 'frame<number>.png' format.")
        return

    frame = cv2.imread(os.path.join(input_folder, images[0]))
    h, w, layers = frame.shape
    size = (w, h)

    # Ensure the output video filename ends with .mp4
    if not output_video_filename.endswith('.mp4'):
        output_video_filename += '.mp4'
    
    # Determine the output video path
    parent_dir = os.path.dirname(input_folder)
    output_video_path = os.path.join(parent_dir, output_video_filename)
    
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
    
    for i in range(len(images)):
        img_path = os.path.join(input_folder, images[i])
        img = cv2.imread(img_path)
        out.write(img)
        print_progress_bar(i, len(images))
    
    out.release()
    print(f"\nVideo saved to {output_video_path}")


def extract_audio_from_video(video_path, start_time=None, end_time=None, format='mp3'):
    # Load video
    clip = VideoFileClip(video_path)
    
    # If start_time and end_time are provided, subclip the video
    if start_time and end_time:
        clip = clip.subclip(start_time, end_time)
    
    # Extract audio
    audio = clip.audio
    
    # Extract video filename without extension
    video_filename = os.path.basename(video_path).rsplit('.', 1)[0]
    
    # Define the audio filename based on whether it's a section or the entire video
    if start_time and end_time:
        audio_filename = f"section of {video_filename}.{format}"
    else:
        audio_filename = f"{video_filename}.{format}"
    
    # Define output path
    output_path = os.path.join(os.path.dirname(video_path), audio_filename)
    
    # Export audio
    if format == 'mp3':
        audio.write_audiofile(output_path, codec='mp3')
    elif format == 'wav':
        audio.write_audiofile(output_path, codec='pcm_s16le')
    
    print(f"Audio extracted to {output_path}")


if __name__ == "__main__":
    while True:
        try:
            print("\nChoose an option:")  
            print("1. Convert video to frames")
            print("2. Convert frames to video")
            print("3. Extract audio from video")
            print("4. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                video_path = input("Enter path to video: ").strip('"')
                
                print("Do you want to alter the FPS?")
                alter_fps_choice = input("1. Yes\n2. No\nChoice: ")
                fps = None
                if alter_fps_choice == '1':
                    fps = float(input("Enter desired FPS: "))

                print("Do you want to extract a specific section of the video?")
                extract_section_choice = input("1. Yes\n2. No\nChoice: ")
                start_time, end_time = None, None
                if extract_section_choice == '1':
                    start_time_str = input("Enter start time (in HH:MM:SS format): ")
                    end_time_str = input("Enter end time (in HH:MM:SS format): ")
                    start_time = time_to_seconds(start_time_str)
                    end_time = time_to_seconds(end_time_str)

                video_to_frames(video_path, fps, start_time, end_time)

            elif choice == "2":
                input_folder = input("Enter the path to the folder containing frames: ").strip('"')
                output_video_filename = input("Enter the desired filename for the output video (without file extension, will be saved as .mp4): ").strip('"')
                fps = float(input("Enter desired FPS for the video: "))
                frames_to_video(input_folder, output_video_filename, fps)

            elif choice == "3":
                video_path = input("Enter path to video: ").strip('"')
                
                print("Do you want to extract audio from the entire video or a specific section?")
                audio_section_choice = input("1. Entire video\n2. Specific section\nChoice: ")
                start_time, end_time = None, None
                if audio_section_choice == '2':
                    start_time_str = input("Enter start time (in HH:MM:SS format): ")
                    end_time_str = input("Enter end time (in HH:MM:SS format): ")
                    start_time = time_to_seconds(start_time_str)
                    end_time = time_to_seconds(end_time_str)

                print("Choose the audio format:")
                format_choice = input("1. mp3\n2. wav\nChoice: ")
                audio_format = 'mp3' if format_choice == '1' else 'wav'

                extract_audio_from_video(video_path, start_time, end_time, audio_format)

            elif choice == "4":
                print("Exiting program.")
                break

            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
