# -*- coding: UTF-8 -*-
# @Time    : 2024/10/1210:50
# @Author  : xielunguo
# @Email   : xielunguo@cosonic.com
# @File    : device_csv_util.py
# @IDE     : PyCharm
import csv
import os.path


class Device_Csv_Util:
    FILENAME_PREFIX = "devices"

    FILENAME = FILENAME_PREFIX + ".csv"

    # 定义字段名
    FIELDNAMES = ["Mac", "Version", "BT", "Voice", "Demo"]

    # 文件记录大于指定行数后,需要开始新的文件记录(提高写入效率)
    MAX_RECORDS = 500

    BURN_STATE_PASS = "Pass"
    BURN_STATE_FAIL = "Fail"
    BURN_STATE_NONE = "None"

    @classmethod
    def getFilePathByVersion(cls, ver: str):
        """
        根据版本号,得到目录
        :param ver:
            设备版本号
        :return:
            目录路径(如果目录不存在,则创建目录)
        """
        curPath = os.getcwd()
        tmpPath = curPath + f"\\log\\{ver}\\"
        if not os.path.exists(tmpPath):
            os.makedirs(tmpPath)
        return tmpPath

    @classmethod
    def getFileNameByVersion(cls, ver: str):
        """
        根据版本号,得到csv文件路径
        :param ver:
            设备版本号
        :return:
            csv文件路径(如果文件不存在,则创建文件,并写入表头)
        """
        parentPath = cls.getFilePathByVersion(ver)
        tmpCsvFile = parentPath + cls.FILENAME

        # 初始化文件, 写入表头（如果文件不存在）
        if not os.path.exists(tmpCsvFile):
            with open(tmpCsvFile, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=cls.FIELDNAMES)
                writer.writeheader()
        return tmpCsvFile

    @classmethod
    def add_or_update_record(cls, csvFile: str, mac:str, version: str, bt: str, voice:str, demo:str):
        """
        添加或更新记录
        :param csvFile:
            csvFile 文件路径
        :param mac:
            设备Mac地址
        :param version:
            设备版本号
        :param bt:
            BinPath#Pass  bt类型文件路径#状态(成功)
            BinPath#Fail  bt类型文件路径#状态(失败)
            BinPath#None  bt类型文件路径#状态(未操作)
        :param voice:
            BinPath#Pass  Voice类型文件路径#状态(成功)
            BinPath#Fail  Voice类型文件路径#状态(失败)
            BinPath#None  Voice类型文件路径#状态(未操作)
        :param demo:
            BinPath#Pass  Demo类型文件路径#状态(成功)
            BinPath#Fail  Demo类型文件路径#状态(失败)
            BinPath#None  Demo类型文件路径#状态(未操作)
        :return:
        """
        updated = False
        records = []

        # 读取CSV文件内容
        with open(csvFile, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Mac"] == mac:
                    # 更新现有记录
                    row["Version"] = version
                    row["BT"] = bt
                    row["Voice"] = voice
                    row["Demo"] = demo
                    updated = True
                records.append(row)

        # 如果没有找到Mac，添加新记录
        if not updated:
            new_record = {
                "Mac": mac,
                "Version": version,
                "BT": bt,
                "Voice": voice,
                "Demo": demo
            }

            # 如果记录数大于指定文件,则需要将当前文件数据复制到新文件中,并重新创建新的文件记录
            tmpRecordCnt = len(records)
            if tmpRecordCnt + 1 > cls.MAX_RECORDS:
                tmpParentPath = os.path.dirname(csvFile)
                tmpFiles = os.listdir(tmpParentPath)
                tmpCsvFileCnt = 0
                for tmpFileName in tmpFiles:
                    if tmpFileName.startswith(cls.FILENAME_PREFIX):
                        tmpCsvFileCnt += 1
                tmpBakCsvFile = tmpParentPath + "/" + "%s-%d.csv" % (cls.FILENAME_PREFIX, tmpCsvFileCnt)
                with open(tmpBakCsvFile, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=cls.FIELDNAMES)
                    writer.writeheader()  # 写入表头
                    writer.writerows(records)  # 写入所有记录
                # 清除已保存的所有记录
                records.clear()

            records.append(new_record)

        # 将数据写回文件
        with open(csvFile, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=cls.FIELDNAMES)
            writer.writeheader()  # 写入表头
            writer.writerows(records)  # 写入所有记录

    @classmethod
    def find_record_by_mac(cls, csvFile: str, mac: str):
        """
        查询记录是否存在
        :param csvFile:
            csvFile 文件路径
        :param mac:
            设备Mac地址
        :return:
            csv文件对应的mac行记录
        """
        with open(csvFile, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Mac"] == mac:
                    return row  # 返回找到的记录
        # 如果没有找到，返回None
        return None

    @classmethod
    def delete_record_by_mac(cls, csvFile: str, mac: str):
        """
        删除记录
        :param csvFile:
            csvFile 文件路径
        :param mac:
            设备Mac地址
        :return:
        """
        records = []

        # 读取CSV文件内容
        with open(csvFile, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Mac"] != mac:
                    records.append(row)  # 只保留不匹配的记录

        # 将数据写回文件
        with open(csvFile, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=cls.FIELDNAMES)
            writer.writeheader()  # 写入表头
            writer.writerows(records)  # 写入所有保留的记录

    @classmethod
    def get_all_records(cls, csvFile: str):
        """
        得到文件所有记录
        :param csvFile:
            csvFile文件名
        :return:
            记录列表
        """
        records = []

        # 读取CSV文件内容
        with open(csvFile, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                records.append(row)

        return records

