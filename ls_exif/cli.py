from rich.markup import escape
from rich.table import Table

from .filesystem import Directory, File

# desired_tags = ['make', 'model', 'x_resolution', 'y_resolution', 'datetime_digitized']
desired_tags = ["Image Make", "Image Model", "EXIF ExifImageWidth", "EXIF ExifImageLength", "Image DateTime"]
headers = (
    "Name",
    "Base Type",
    "Size",
    "Modification Date",
    "Taken Date",
    "Resolution",
    "Camera",
)


#def colorize(color, text):
#    return f"{color}{text}{Style.RESET_ALL}"


def print_tabular_listing(console, base_dir, dirs, files):
    from rich.console import Console

    render_directory = lambda d: (
        escape(d.name),
        d.base_type,
        str(d.file_size),
        d.modification_date and d.modification_date.isoformat(),
    )
    render_file = lambda f: (
        escape(f.name),
        f.base_type,
        str(f.file_size),
        f.modification_date and f.modification_date.isoformat(),
        f.taken_date and f.taken_date.isoformat(),
        f.resolution,
        f.camera and escape(f.camera),
    )

    title = escape(str(base_dir.resolve()))
    table = Table(show_header=True, title=title, header_style="bold magenta", title_justify="left")
    # , row_styles=['dim', '']
    table.add_column("Name")
    table.add_column("Base Type")
    table.add_column("Size", justify="right")
    table.add_column("Modification Date")
    table.add_column("Taken Date", style="green")
    table.add_column("Resolution", style="yellow")
    table.add_column("Camera", style="magenta")

    for d in dirs:
        table.add_row(*render_directory(d))
    for f in files:
        table.add_row(*render_file(f))

    console.print(table)
    print()


#def print_directory_listing(base_dir, dirs, files, format="table"):
#    # directory header
#    print()
#    print(f"{Fore.MAGENTA}{base_dir}{Style.RESET_ALL}:")
#    # list files and directories combined
#    for f in sorted(files + dirs):
#        if isinstance(f, File):
#            print(
#                f"{f.permissions}\t{f.owner}\t{f.group}\t{f.file_size}\t{f.modification_date}\t{colorize(Fore.GREEN, f.name)}\t"
#                f"{colorize(Fore.YELLOW, f.resolution)}\t{colorize(Fore.MAGENTA, f.camera)}\t{f.taken_date}"
#            )
#        else:
#            print(
#                f"{f.permissions}\t{f.owner}\t{f.group}\t{f.file_size}\t{f.modification_date}\t{colorize(Fore.BLUE, f.name)}"
#            )


def walk_directory(start_path, path, callback, recurse=True):
    files = []
    dirs = []
    for f in path.iterdir():
        if f.is_dir():
            dirs.append(Directory(f))
        elif f.is_file():
            files.append(File(f))
        else:
            raise Exception("huh!?")

    callback(path.relative_to(start_path), dirs, files)

    if recurse:
        for d in dirs:
            walk_directory(start_path, d.path, callback, recurse)
