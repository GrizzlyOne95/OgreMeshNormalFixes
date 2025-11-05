import os
import subprocess

# Change this to your root folder
ROOT_DIR = r"path\to"

def convert_dds_to_tga(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(".dds"):
                dds_path = os.path.join(dirpath, filename)
                tga_path = os.path.splitext(dds_path)[0] + ".tga"

                if os.path.exists(tga_path):
                    print(f"Skipping (already exists): {tga_path}")
                    continue

                # Run FFmpeg command
                cmd = ["ffmpeg", "-y", "-i", dds_path, tga_path]
                try:
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"Converted: {dds_path} → {tga_path}")
                except subprocess.CalledProcessError:
                    print(f"Error converting: {dds_path}")

if __name__ == "__main__":
    convert_dds_to_tga(ROOT_DIR)
