import json
import os

def get_browser_options():
    return [
            '--no-sandbox',
            '--disable-dev-shm-usage', 
            '--disable-extensions',
            '--disable-gpu'
            ]



def save_to_file(comments: list, fileName: str = None, mode: str = 'w'):
    try:
        path = "./file/"
        os.makedirs(path, exist_ok=True)

        fileName = os.path.join(path, fileName+".txt")

        with open(fileName, mode, encoding='utf-8') as f:
            # f.write(comments)
            json.dump(comments, f, ensure_ascii=False, indent=2)
        print(f"file_saved to {fileName}")
    except Exception as e:
        print(f"failed to file save. fileName={fileName}, error={e}")


