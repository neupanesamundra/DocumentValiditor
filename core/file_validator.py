from config.rules import ALLOWED_EXTENSIONS
from config.settings import MAX_FILE_SIZE_MB
from utils.helpers import get_extension


def validate_file(file):
    if file.filename == "":
        return False, "No file selected."

    extension = get_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        return False, "Unsupported file type. Use PDF, DOCX, or TXT."

    if MAX_FILE_SIZE_MB and MAX_FILE_SIZE_MB > 0:
        file.seek(0, 2)
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)

        if size_mb > MAX_FILE_SIZE_MB:
            return False, f"File too large. Maximum size is {MAX_FILE_SIZE_MB} MB."

    return True, "Valid file."
