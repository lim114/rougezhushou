"""Install a first record without replacing an entry hidden by metadata APIs."""
import os
import errno
from contextlib import contextmanager
from pathlib import Path
import tempfile


@contextmanager
def record_save_lock(destination):
    """Reject overlapping publishers without entering an existing lock entry.

    The atomic directory claim spans writing, archival and publication. A
    concurrent or interrupted owner remains a reported IO failure; it is never
    removed or taken over automatically. Only this call's empty claim is removed.
    """
    destination = Path(destination)
    claim = destination.with_name(destination.name + '.saving')
    os.mkdir(claim)
    try:
        yield
    finally:
        os.rmdir(claim)


@contextmanager
def _open_claimed_temporary(path, mode, *args, **kwargs):
    """Claim the name by hard link and write only our already-open descriptor.

    Wine can follow a dangling host link even with Python's exclusive open.
    Linking an owned same-directory file refuses that directory entry atomically.
    Keep the descriptor until writing completes, retaining the diagnostic link
    on errors and removing only our private anchor after the descriptor closes.
    """
    # The anchor itself must never be opened at a pre-existing file entry.
    # Allocate a fresh directory atomically, then create the owned descriptor
    # inside that new empty namespace. A random file name alone is insufficient.
    with tempfile.TemporaryDirectory(prefix='.rouge-record-', dir=path.parent) as folder:
        descriptor, anchor = tempfile.mkstemp(prefix='record-', dir=folder)
        try:
            try:
                os.link(anchor, path)
            except FileExistsError as error:
                raise FileExistsError(error.errno, error.strerror, os.fspath(path)) from error
            with os.fdopen(descriptor, mode, *args, **kwargs) as stream:
                descriptor = None
                yield stream
        finally:
            if descriptor is not None:
                os.close(descriptor)


class _ExclusiveTemporaryPath(type(Path())):
    """Keep Path's text encoding/newlines, but create temporary bytes once.

    Opening a pre-existing .tmp with mode='w' could follow a link or truncate
    retained failure evidence. Hard-link claiming also handles directory entries
    hidden from the compatibility metadata and exclusive-open APIs.
    """

    def open(self, mode='r', *args, **kwargs):
        if mode.startswith('w'):
            return _open_claimed_temporary(self, mode, *args, **kwargs)
        return super().open(mode, *args, **kwargs)


def write_temporary_record(destination, text):
    """Write complete new bytes while retaining every older temporary entry.

    Keep the usual diagnostic name when it can be exclusively claimed. An
    actual atomic name conflict uses a separate exclusive file, so an older
    interrupted write cannot block a user's explicit new run or be truncated.
    Other IO failures retain their original failure/stop contract. The caller
    must hold record_save_lock through publication to protect an in-flight name.
    """
    import uuid
    destination = Path(destination)
    temporary = _ExclusiveTemporaryPath(destination).with_suffix('.tmp')
    if temporary != destination:
        try:
            temporary.write_text(text, encoding='utf-8')
            return temporary
        except FileExistsError as error:
            if (error.errno != errno.EEXIST or error.filename is None
                    or Path(error.filename) != temporary or temporary.is_dir()):
                raise
            # Consume the usual temporary name without consuming its bytes.
            # Known entries move atomically to a no-replace retained original;
            # the next hard-link claim still refuses a racing replacement.
            try:
                archive_unreadable_record(temporary)
            except FileNotFoundError:
                # Wine may hide a dangling host link from lstat. Do not guess
                # its kind or remove it; use an independently claimed name.
                pass
            else:
                temporary.write_text(text, encoding='utf-8')
                return temporary
    temporary = _ExclusiveTemporaryPath(destination.with_name(
        destination.name + '.' + uuid.uuid4().hex + '.tmp'))
    temporary.write_text(text, encoding='utf-8')
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
