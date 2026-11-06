"""API keys live in Windows Credential Manager, never in project settings."""
import pywintypes
import win32cred
import winerror

TARGET = 'RougeBlackflowHelper/provider/'

def save_key(profile, key):
    if not profile or not key:
        raise ValueError('名称和 API Key 不能为空。')
    win32cred.CredWrite({'Type': win32cred.CRED_TYPE_GENERIC, 'TargetName': TARGET + profile,
                        'UserName': 'api', 'CredentialBlob': key.encode('utf-16-le'),
                        'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE}, 0)

def read_key(profile):
    try:
        record = win32cred.CredRead(TARGET + profile, win32cred.CRED_TYPE_GENERIC)
    except pywintypes.error as error:
        if error.winerror == winerror.ERROR_NOT_FOUND:
            return ''
        raise
    blob = record['CredentialBlob']
    return blob.decode('utf-16-le') if isinstance(blob, bytes) else blob
