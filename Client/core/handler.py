from conf import config_yml
from core import info_collection
import logging
import json
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


class Handler():
    @staticmethod
    def collect_data():
        """ 收集硬件信息 用于测试 """
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        logger.info('collect client info: {}'.format(asset_data))

    @staticmethod
    def report_data():
        """ 收集硬件信息 发送到服务器 """
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        data = {"asset_data": asset_data}
        url = config_yml['remote_report_server']['server_url']
        request_timeout = config_yml['remote_report_server']['request_timeout']
        logger.info('start to report data to server.')

        try:
            r = requests.post(url=url, json=data, timeout=request_timeout)
        except Exception as e:
            logger.exception('end report data to server error.')
        else:
            logger.info("end report data to server, get data: {}".format(r.content.decode('utf-8')))