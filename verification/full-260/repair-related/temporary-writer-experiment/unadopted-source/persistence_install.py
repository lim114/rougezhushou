"""Install a first record without replacing an entry hidden by metadata APIs."""
import os


def write_temporary_record(text, destination):
    """Create private complete bytes without following a shared .tmp entry."""
    import tempfile
    from pathlib import Path
    destination = Path(destination)
    descriptor, name = tempfile.mkstemp(prefix=destination.name + '.', suffix='.tmp', dir=destination.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(text)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def install_initial_record(temporary, destination):
    """Publish complete bytes atomically, refusing any existing destination.

    A load-time ENOENT is not authority to overwrite a later entry. Wine also
    hides dangling host Unix links from lstat and directory enumeration. The
    hard-link operation checks the destination directory entry atomically and
    rejects both cases; unsupported hard links remain a reported save failure.
    """
    os.link(temporary, destination)
    temporary.unlink()


def archive_unreadable_record(source):
    """Move the original entry to a unique same-directory name, without replacing.

    Windows rename refuses existing destinations and moves the reparse object.
    Linux renameat2 supplies the same no-replace contract for ordinary entries
    and symbolic links. No unlink/copy fallback weakens that guarantee.
    """
    import ctypes
    import errno
    import sys
    import uuid
    from pathlib import Path

    source = Path(source)
    import stat
    kind = source.lstat().st_mode
    if not (stat.S_ISREG(kind) or stat.S_ISLNK(kind)):
        raise OSError(errno.EINVAL, 'The original record is not a file or symbolic link')
    archive = source.with_name(source.name + '.preserved-' + uuid.uuid4().hex)
    if os.name == 'nt':
        source.rename(archive)
    elif sys.platform.startswith('linux'):
        libc = ctypes.CDLL(None, use_errno=True)
        try:
            renameat2 = libc.renameat2
        except AttributeError as error:
            raise OSError(errno.ENOTSUP, 'Atomic no-replace archive is unavailable') from error
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        renameat2.restype = ctypes.c_int
        # AT_FDCWD=-100, RENAME_NOREPLACE=1; source and destination share parent.
        if renameat2(-100, os.fsencode(source), -100, os.fsencode(archive), 1):
            code = ctypes.get_errno()
            raise OSError(code, os.strerror(code), str(source))
    else:
        raise OSError(errno.ENOTSUP, 'Atomic no-replace archive is unavailable')
    return archive


def preserved_original_paths(source):
    """Find this file's retained originals for interrupted-reset notice only."""
    from pathlib import Path
    source = Path(source)
    prefix = source.name + '.preserved-'
    try:
        entries = tuple(source.parent.iterdir())
    except FileNotFoundError:
        return ()
    return tuple(sorted((entry for entry in entries
        if entry.name.startswith(prefix)
        and len(entry.name[len(prefix):]) == 32
        and all(char in '0123456789abcdef' for char in entry.name[len(prefix):])), key=lambda entry: entry.name))
