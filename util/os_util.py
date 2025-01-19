import subprocess, os, platform

def open_with_associated_program(filepath: str):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:
        print(f"File to open at: {filepath}")