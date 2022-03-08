#!usr/bin/env python
# -*- coding: utf-8 -*-

'''
    @author: khaosles
    @date: 2022/3/8  11:34
'''


from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client

class FDFSStorage(Storage):
    '''fdfs文件存储类'''

    def _open(self, name, mode='rb'):
        '''打开文件'''
        pass

    def _save(self, name, content):
        '''保存文件'''
        # name 文件名字
        # content file类对象

        # 创建fdfs_client对象
        client = Fdfs_client('./utils/fdfs/client.conf')

        # 上传文件到fdfs中
        res = client.upload_by_buffer(content.read())
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res is None or res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到fdfs失败')

        # 获取返回的文件id
        filename = res.get('Remote file_id')

        return filename


    def exists(self, name):
        '''django判断文件名是否可用'''
        return False