import stat
import re
from datetime import datetime
from functools import cached_property

import exifread

EXTENSIONS = {
    'image': (
        '.jpeg',
        '.jpg',
    ),
    'video': ('.mp4',),
}


class BaseFilesystemObject:
    def __init__(self, path):
        self.path = path

    @property
    def name(self):
        return self.path.name

    @cached_property
    def stat(self):
        return self.path.stat()

    @property
    def modification_date(self):
        return datetime.fromtimestamp(self.stat.st_mtime).replace(microsecond=0)

    @property
    def owner(self):
        return 'user'

    @property
    def group(self):
        return 'group'

    @property
    def permissions(self):
        return stat.filemode(self.stat.st_mode)

    @property
    def file_size(self):
        return "-"


class File(BaseFilesystemObject):
    @cached_property
    def exif_tags(self):
        if self.base_type == "image":
            with open(self.path, "rb") as image_stream:
                return exifread.process_file(image_stream, details=False)

    def _has_exif_tags(self, *required_tags):
        return bool(self.exif_tags) and set(required_tags).issubset(set(self.exif_tags.keys()))

    @cached_property
    def base_type(self):
        suffix = self.path.suffix.lower()
        for t, extensions in EXTENSIONS.items():
            if suffix in extensions:
                return t
        return "other"

    @property
    def taken_date(self):
        return self._read_exif_value('EXIF DateTimeOriginal', expected_type=datetime) or self._read_exif_value('Image DateTime', expected_type=datetime)

    @property
    def resolution(self):
        if self._has_exif_tags('Image ImageWidth', 'Image ImageLength'):
            return f'{self._read_exif_value("Image ImageWidth", expected_type=int)} x {self._read_exif_value("Image ImageLength", expected_type=int)}'
        elif self._has_exif_tags("EXIF ExifImageWidth", "EXIF ExifImageLength"):
            return f'{self._read_exif_value("EXIF ExifImageWidth", expected_type=int)} x {self._read_exif_value("EXIF ExifImageLength", expected_type=int)}'
            # return f'{width} x {height}'.format(width=tags['EXIF ExifImageWidth'], height=tags['EXIF ExifImageLength'])
        else:
            # WARN: raise Exception('Could not find a sufficient set of resolution tags in {tags}'.format(tags=tags.keys()))
            return

    @property
    def camera(self):
        if self._has_exif_tags('Image Make', 'Image Model'):
            make = self._read_exif_value('Image Make')
            model = self._read_exif_value('Image Model')
            if model.lower().startswith(make.lower()):   # examples from the wild: Canon / Canon IXUS 105, HTC / HTC Hero
                return model
            else:
                return f'{make} {model}'

    @property
    def file_size(self):
        return self.stat.st_size

    def _parse_exif_date_strings(self, exif_date_string):
        # taken inspiration from TheLastGimbus: https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/cf2c6d478afd400ddda66168d8e07d9ce5edb261/google_photos_takeout_helper/__main__.py#L398
        # Quote:
        #    > Turns out exif can have different formats - YYYY:MM:DD, YYYY/..., YYYY-... etc
        #    > God wish that americans won't have something like MM-DD-YYYY
        #    > The replace ': ' to ':0' fixes issues when it reads the string as 2006:11:09 10:54: 1.
        #    > It replaces the extra whitespace with a 0 for proper parsing
        cleaned_date_string = exif_date_string.replace('/', '-',).replace(':', '-').replace('.', '-').replace('\\', '-').replace(': ', ':0')[:19]
        return datetime.strptime(cleaned_date_string, '%Y-%m-%d %H-%M-%S')

    def _read_exif_value(self, tag_name, expected_type=str):
        EXIF_DATE_FORMATS = re.compile(r'\d{4}[/:]\d{2}[/:]\d{2} \d{2}:\d{2}:\d{2}')
        if self._has_exif_tags(tag_name):
            tag = self.exif_tags[tag_name]
            if tag.field_type == 2:
                assert type(tag.values) == str
                if EXIF_DATE_FORMATS.match(tag.values):
                    assert expected_type == datetime, f'Expected {expected_type}, got datetime: {tag.values}'
                    return self._parse_exif_date_strings(tag.values)
                #assert expected_type == str, f'Expected {expected_type}, got str: {tag.values}'
                if expected_type == datetime:
                    print(f'Expected {expected_type}, got str: {tag.values}')
                    return datetime.now()
                return tag.values
            elif tag.field_type in (
                3,
                4,
            ):
                assert expected_type == int, f'Expected {expected_type}, got int: {tag.values}'
                return tag.values[0]
            else:
                raise Exception(f'Unsupported type: {tag.field_type}')
        return None

    def __lt__(self, other):
        if type(other) == File:
            return self.name < other.name
        elif type(other) == Directory:
            return False


class Directory(BaseFilesystemObject):
    @property
    def base_type(self):
        return '<DIR>'

    def __lt__(self, other):
        if type(other) == Directory:
            return self.name < other.name
        elif type(other) == File:
            return True
