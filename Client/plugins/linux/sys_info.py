import subprocess
import logging
import json
import copy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

sudo_password = 'sxl'


def collect():
    info_data = dict(
        asset_type='server'
    )

    info_data.update(get_sys_info())
    info_data.update(get_os_type_info())
    info_data.update(get_os_cpu_info())
    info_data.update(get_os_ram_info())
    info_data.update(get_os_disk_info())

    logger.info(json.dumps(info_data, indent=4))
    return info_data


def get_subprocess_res(cmd):
    res = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    return [x.decode() for x in res.stdout.readlines()]


def get_raw_data(filter_keys, ready_clean_data):
    raw_data = {}
    raw_data = raw_data.fromkeys(filter_keys, None)
    for i in ready_clean_data:
        i = i.strip().split(':')
        if len(i) > 1 and i[0].strip() in filter_keys:
            raw_data.update({i[0].strip(): i[1].strip()})

    logger.info(raw_data)
    return raw_data


def get_os_cpu_raw_data(ready_clean_data):
    raw_data = dict(
        cpu_count=0,
        cpu_model=None,
        cpu_core_count=0
    )

    for i in ready_clean_data:
        i = i.strip().split(':')
        if len(i) > 1:
            key = i[0].strip()
            value = i[1].strip()
            if key == 'processor':
                raw_data['cpu_count'] += 1
            elif key == 'model name':
                raw_data['cpu_model'] = value
            elif key == 'cpu cores':
                raw_data['cpu_core_count'] += int(value)

    logger.info(raw_data)
    return raw_data


def get_os_ram_raw_data(ready_clean_data):
    raw_data = dict(
        ram=[],
        ram_size=0
    )

    ram = {}
    for i in ready_clean_data:
        k = i.strip()
        if k == 'Memory Device':
            if ram:
                raw_data['ram'].append(copy.deepcopy(ram))
            ram.clear()
        else:
            k = k.split(':')
            if len(k) > 1:
                if k[0].strip() == 'Type':
                    ram['model'] = k[1].strip()
                elif k[0].strip() == 'Manufacturer':
                    ram['Manufacturer'] = k[1].strip()
                elif k[0].strip() == 'Serial Number':
                    ram['sn'] = k[1].strip()
                elif k[0].strip() == 'Asset Tag':
                    ram['asset_tag'] = k[1].strip()
                elif k[0].strip() == 'Locator':
                    ram['slot'] = k[1].strip()
                elif k[0].strip() == 'Size':
                    raw_data['ram_size'] += int(k[1].strip().split()[0]) / 1024
    if ram:
        raw_data['ram'].append(ram)

    logger.info(raw_data)
    return raw_data


def get_os_nic_raw_data(ready_clean_data):
    return dict(
        nic=[]
    )


def get_sys_info():
    filter_keys = ['Manufacturer', 'Serial Number', 'Product Name', 'UUID', 'Wake-up Type']
    cmd = 'echo {} | sudo -S dmidecode -t system'.format(sudo_password)
    system_info = get_subprocess_res(cmd)
    raw_data = get_raw_data(filter_keys, system_info)

    return {'manufacturer': raw_data['Manufacturer'], 'sn': raw_data['Serial Number'],
            'model': raw_data['Product Name'], 'uuid': raw_data['UUID'], 'wake_up_type': raw_data['Wake-up Type']}


def get_os_type_info():
    filter_keys = ['Distributor ID', 'Release']
    cmd = 'echo {} | sudo -S lsb_release -a'.format(sudo_password)
    system_info = get_subprocess_res(cmd)
    raw_data = get_raw_data(filter_keys, system_info)
    return dict(
        os_distribution=raw_data['Distributor ID'],
        os_release=raw_data['Release'],
        os_type='Linux'
    )


def get_os_cpu_info():
    # cmd = 'cat /proc/cupinfo' subprocess.Popen not working.. so use read
    with open('/proc/cpuinfo', encoding='utf-8') as f:
        cpu_infos = f.readlines()
    raw_data = get_os_cpu_raw_data(cpu_infos)
    return raw_data


def get_os_ram_info():
    cmd = 'echo {}|sudo -S dmidecode -t memory'.format(sudo_password)
    ram_info = get_subprocess_res(cmd)
    return get_os_ram_raw_data(ram_info)


def get_os_nic_info():
    cmd = 'echo {}|sudo -S ifconfig -a'.format(sudo_password)
    nic_info = get_subprocess_res(cmd)
    return get_os_nic_raw_data(nic_info)


def get_os_disk_info():
    cmd1 = 'echo {} | sudo -S hdparm -i {} | grep Model'.format(sudo_password, '/dev/sda')
    cmd2 = 'echo {} | sudo -S fdisk -l {} | head -1'.format(sudo_password, '/dev/sda')
    disk_basic_info = get_subprocess_res(cmd1)
    disk_size_info = get_subprocess_res(cmd2)

    disk_basic_info = disk_basic_info[0].split(',')
    model = disk_basic_info[0].split('=')[1].strip()
    sn = disk_basic_info[2].split('=')[1].strip()

    disk_size_info = disk_size_info[0].split(',')
    size = disk_size_info[0].split(':')[1].strip().split()[0]

    result = {'physical_disk_driver': []}
    result['physical_disk_driver'].append(dict(
        model=model,
        sn=sn,
        size=size
    ))
    return result


if __name__ == '__main__':
    collect()
    # res = subprocess.Popen('cat /proc/cpuinfo', stdout=subprocess.PIPE, shell=True)
    # print([x.decode() for x in res.stdout.readlines()])
