# -*- coding: UTF-8 -*-
# @Time    : 2024/10/1010:45
# @Author  : xielunguo
# @Email   : xielunguo@cosonic.com
# @File    : test_csv_file.py
# @IDE     : PyCharm

import csv
import os

FILENAME = 'devices.csv'

# 定义字段名
FIELDNAMES = ["Mac", "Version", "Voice", "BT", "Demo"]

# 初始化文件，写入表头（如果文件不存在）
if not os.path.exists(FILENAME):
    with open(FILENAME, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()

# 添加或更新记录
def add_or_update_record(mac, version, voice, bt, demo):
    updated = False
    records = []

    # 读取CSV文件内容
    with open(FILENAME, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Mac"] == mac:
                # 更新现有记录
                row["Version"] = version
                row["Voice"] = voice
                row["BT"] = bt
                row["Demo"] = demo
                updated = True
            records.append(row)

    # 如果没有找到Mac，添加新记录
    if not updated:
        new_record = {
            "Mac": mac,
            "Version": version,
            "Voice": voice,
            "BT": bt,
            "Demo": demo
        }
        records.append(new_record)

    # 将数据写回文件
    with open(FILENAME, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()  # 写入表头
        writer.writerows(records)  # 写入所有记录

# 查询记录是否存在
def find_record_by_mac(mac):
    with open(FILENAME, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Mac"] == mac:
                return row  # 返回找到的记录
    return None  # 如果没有找到，返回None

# 删除记录
def delete_record_by_mac(mac):
    records = []

    # 读取CSV文件内容
    with open(FILENAME, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Mac"] != mac:
                records.append(row)  # 只保留不匹配的记录

    # 将数据写回文件
    with open(FILENAME, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()  # 写入表头
        writer.writerows(records)  # 写入所有保留的记录

# 测试功能
if __name__ == "__main__":
    # 添加或更新记录
    add_or_update_record("00000000FFFF", "V1.0", "False", "True", "None")
    add_or_update_record("00000000AAAA", "V1.1", "True", "False", "Active")

    # 查询记录
    mac_address = "00000000FFFF"
    record = find_record_by_mac(mac_address)
    print(f"Record found: {record}" if record else f"No record found for Mac: {mac_address}")

    # 更新记录
    add_or_update_record("00000000FFFF", "V1.2", "True", "True", "Updated")

    # 删除记录
    delete_record_by_mac("00000000AAAA")
    print(f"Record with Mac 00000000AAAA has been deleted.")

    # 再次验证
    record = find_record_by_mac("00000000AAAA")
    print(f"Record still exists: {record}" if record else "No record found for Mac: 00000000AAAA")