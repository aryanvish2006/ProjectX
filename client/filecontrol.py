import os
def list_folder(relative_path):
    home = os.path.expanduser("~")
    folder_path = os.path.join(home, relative_path)
    folder_path = os.path.abspath(folder_path)

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
        result = {"error": f"Permission denied for folder '{folder_path}'"}

    return result


# Read a file

def read_file(relative_path, file_name):
    if not file_name:
        return {"error": "Please provide a file name to read"}

    home = os.path.expanduser("~")
    folder_path = os.path.join(home, relative_path)
    folder_path = os.path.abspath(folder_path)

    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"file": file_name, "content": content}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": f"File '{file_name}' does not exist"}


# Delete a file

def delete_file(relative_path, file_name):
    if not file_name:
        return {"error": "Please provide a file name to delete"}

    home = os.path.expanduser("~")
    folder_path = os.path.join(home, relative_path)
    folder_path = os.path.abspath(folder_path)

    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        try:
            os.remove(file_path)
            return {"deleted": file_name}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": f"File '{file_name}' does not exist"}
    


