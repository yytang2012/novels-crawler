#!/usr/bin/env python3
# coding=utf-8

"""Upload the contents of your Downloads folder to Dropbox.

This is an example app for API v2.
"""

from __future__ import print_function

import datetime
import os
import time

import dropbox
from dropbox.files import FileMetadata

from libs.misc import stopwatch


class DropboxAPI:

    def __init__(self, token):
        self.dbx = dropbox.Dropbox(token)

    def list_folder(self, root_folder='', subfolder=''):
        """List a folder.

        Return a dict mapping unicode filenames to
        FileMetadata|FolderMetadata entries.
        """
        path = '/%s/%s' % (root_folder, subfolder.replace(os.path.sep, '/'))
        while '//' in path:
            path = path.replace('//', '/')
        path = path.rstrip('/')
        try:
            with stopwatch('list_folder'):
                res = self.dbx.files_list_folder(path)
        except dropbox.exceptions.ApiError as err:
            print('Folder listing failed for', path, '-- assumped empty:', err)
            return {}
        else:
            rv = {}
            for entry in res.entries:
                rv[entry.name] = entry
            return rv

    def download(self, root_folder, subfolder, name):
        """Download a file.

        Return the bytes of the file, or None if it doesn't exist.
        """
        path = '/%s/%s/%s' % (root_folder, subfolder.replace(os.path.sep, '/'), name)
        while '//' in path:
            path = path.replace('//', '/')
        with stopwatch('download'):
            try:
                md, res = self.dbx.files_download(path)
            except dropbox.exceptions.HttpError as err:
                print('*** HTTP error', err)
                return None
        data = res.content
        print(len(data), 'bytes; md:', md)
        return data

    def upload(self, local_fullname, root_folder, subfolder, name, overwrite=False):
        """Upload a file.

        Return the request response, or None in case of error.
        """
        path = '/%s/%s/%s' % (root_folder, subfolder.replace(os.path.sep, '/'), name)
        while '//' in path:
            path = path.replace('//', '/')
        mode = (dropbox.files.WriteMode.overwrite
                if overwrite
                else dropbox.files.WriteMode.add)
        mtime = os.path.getmtime(local_fullname)
        with open(local_fullname, 'rb') as f:
            data = f.read()
        with stopwatch('upload %d bytes' % len(data)):
            try:
                res = self.dbx.files_upload(
                    data, path, mode,
                    client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                    mute=True)
            except dropbox.exceptions.ApiError as err:
                print('*** API error', err)
                return None
        print('uploaded as', res.name)
        return res