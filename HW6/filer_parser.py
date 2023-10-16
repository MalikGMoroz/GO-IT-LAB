import sys
from pathlib import Path

FILE_CATEGORIES = {
    'JPEG': [],
    'PNG': [],
    'JPG': [],
    'SVG': [],
    'MP3': [],
    'OGG': [],
    'WAV': [],
    'AMR': [],
    'AVI': [],
    'MP4': [],
    'MOV': [],
    'MKV': [],
    'DOC': [],
    'DOCX': [],
    'TXT': [],
    'PDF': [],
    'XLSX': [],
    'PPTX': [],
    'ZIP': [],
    'GZ': [],
    'TAR': []
}

OTHER_FILES = []
FOLDERS = []
EXTENSIONS = set()
UNKNOWN = set()


def get_extension(filename: str) -> str:
    """Returns the file extension in uppercase, without the dot."""
    return Path(filename).suffix[1:].upper()


def scan(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'other_files'):
                FOLDERS.append(item)
                scan(item)
            continue

        ext = get_extension(item.name)
        fullname = folder / item.name

        if not ext:
            OTHER_FILES.append(fullname)
        else:
            container = FILE_CATEGORIES.get(ext)
            if container is not None:
                EXTENSIONS.add(ext)
                container.append(fullname)
            else:
                UNKNOWN.add(ext)
                OTHER_FILES.append(fullname)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide a folder path to scan.")
        sys.exit(1)

    folder_for_scan = sys.argv[1]
    print(f'Start in folder {folder_for_scan}')

    scan(Path(folder_for_scan))

    for ext, files in FILE_CATEGORIES.items():
        print(f'{ext} files: {files}')

    print(f'Other files: {OTHER_FILES}')
    print(f'Types of files in folder: {EXTENSIONS}')
    print(f'Unknown types of files: {UNKNOWN}')
    print(FOLDERS[::-1])
