import os
import sys
import glob
import subprocess
from datetime import datetime, timedelta
from allsky.config import OUTPUT_IMAGES_DIR

def get_second_latest_folder(directory=None):
    ''' Function to get the second latest created folder in a directory '''
    if directory is None: 
        directory=OUTPUT_IMAGES_DIR
    folders = [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    sorted_folders = sorted(folders, key=os.path.getctime, reverse=True)
    return sorted_folders[1] if len(sorted_folders) > 1 else None

# Function to create the video from the input_path
def create_video(input_path=None):
    ''' Get the name of the last folder in the input path '''
    if input_path is None:
        input_path = get_second_latest_folder()
    folder_name = os.path.basename(os.path.normpath(input_path))
    output_name = 'timelapse_' + folder_name + ".mp4"
    output_video = os.path.join(input_path, output_name)

    # Check if the output video file already exists
    if os.path.exists(output_video):
        print(f"Video already exists in the directory: {output_video}")
        return

    # Get all .jpg files in the input path and sort them by date
    jpg_files = glob.glob(os.path.join(input_path, "pic_*.jpg"))
    jpg_files.sort(key=lambda x: os.path.getmtime(x))
    print('> Creating output video: ' + output_video + ', from ' + str(len(jpg_files)) + ' images.')

    # Create a list file for mencoder
    list_file = os.path.join(input_path, "files.txt")
    with open(list_file, "w") as f:
        for jpg_file in jpg_files:
            f.write(f"{jpg_file}\n")

    # Run mencoder to produce a video
    mencoder_command = f"mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=5000 -vf scale=640:480 -o {output_video} -mf type=jpeg:fps=24 mf://@{list_file}"
    subprocess.call(mencoder_command, shell=True)

    # Clean up the list file
    #os.remove(list_file)

def create_all_videos(directory):
    ''' Function to process all folders in a given directory, skipping folders created in the last 24 hours '''
    now = datetime.now()
    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            folder_ctime = datetime.fromtimestamp(os.path.getctime(folder_path))
            if now - folder_ctime > timedelta(hours=24):
                create_video(folder_path)

if __name__ == "__main__":
    # Get input path
    #input_path = sys.argv[1] if len(sys.argv) > 1 else get_second_latest_folder()
    #create_video(input_path)
    create_all_videos(OUTPUT_IMAGES_DIR)
