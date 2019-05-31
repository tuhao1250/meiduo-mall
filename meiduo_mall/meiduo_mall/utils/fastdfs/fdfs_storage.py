from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.conf import settings
from fdfs_client.client import Fdfs_client


@deconstructible
class FastDFSSTORAGE(Storage):
    """
    自定义fastdfs文件存储类
    """

    def __init__(self, client_conf=None, base_url=None):
        """
        初始化
        :param client_conf:fdfs客户端使用的配置文件路径
        :param base_url:用于构造文件完整路径
        """
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf
        if base_url is None:
            base_url = settings.FDFS_BASE_URL
        self.base_url = base_url

    def _save(self, name, content):
        """
        将文件保存到fastdfs中
        :param name:前端传递的文件名
        :param content:django传递的文件内容数据
        :return:返回值会被django存储到数据库中
        """
        client = Fdfs_client(self.client_conf)
        # 注意django传递的文件内容数据需要执行read方法才可以存储,可以理解为是一个文件对象,执行read方法获取真实文件数据
        ret = client.upload_by_buffer(content.read())
        if ret.get('Status') != 'Upload successed.':
            # 文件上传失败
            raise Exception("upload file failed")
        # 文件上传成功
        file_name = ret.get('Remote file_id')
        return file_name

    def _open(self, name, mode='rb'):
        pass

    def exists(self, name):
        return False

    def url(self, name):
        """
        获取ImageField字段数据的url属性时,django会调用url方法获取文件的完整路径
        :param name: 从数据库中读取到的值,也就是在_save()方法中保存的file_name 也就是 Remote file_id
        :return:
        """
        return self.base_url + name