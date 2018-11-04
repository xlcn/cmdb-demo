import sys
import platform
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


def linux_sys_info():
    from plugins.linux import sys_info
    return sys_info.collect()

def windows_sys_info():
    from plugins.windows import sys_info as win_sys_info
    return win_sys_info.collect()


class InfoCollection():
    def collect(self):
        try:
            func = getattr(self, platform.system())
            info_data = func()
            formatted_data = self.build_report_data(info_data)
            return formatted_data
        except AttributeError as e:
            logger.exception('not support this operating system: {}.'.format(platform.system()))
        except Exception as e:
            logger.exception('info collect error.')

    def Windows(self):
        return windows_sys_info()

    def Linux(self):
        return linux_sys_info()

    def build_report_data(self, info_data):
        # format data
        return info_data
