
def readFrom(file_path: str):
    try:
        # 打开二进制文件
        with open(file_path, 'rb') as file:
            # 读取文件内容
            data = file.read()

        # 计算文件长度
        length = len(data)

        return data, length
    except Exception as e:
        print(repr(e))


def readFromEx(file_path: str):
    try:
        # 打开二进制文件
        with open(file_path, 'rb') as file:
            # 读取文件内容
            data = file.read()

        # 计算文件长度
        length = len(data)

        return length > 0, data
    except Exception as e:
        print(repr(e))
        return False, bytes()