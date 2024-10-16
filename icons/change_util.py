import cv2

def change():
    ico_names_fmt = ["start_%d.png", "stop_%d.png", "quit_%d.png", "file_%d.png", "admin_%d.png"]
    cnt = len(ico_names_fmt)
    for i in range(cnt):
        tmpFile = "./src/" + ico_names_fmt[i] % (0)
        srcImg = cv2.imread(tmpFile, cv2.IMREAD_UNCHANGED)

        # 改变尺寸
        srcImgOut = cv2.resize(srcImg, (50, 50))
        saveFile = "./out/" + ico_names_fmt[i] % (0)
        cv2.imwrite(saveFile, srcImgOut)

        # 置灰
        grayImgOut = cv2.cvtColor(srcImgOut, cv2.COLOR_BGR2GRAY)
        saveGrayFile = "./out/" + ico_names_fmt[i] % (1)
        cv2.imwrite(saveGrayFile, grayImgOut)

def change_2():
    ico_names_file = ["ico-help.png","ico-version.png", "main_logo.png"]
    cnt = len(ico_names_file)
    for i in range(cnt):
        tmpFile = "./src/" + ico_names_file[i]
        srcImg = cv2.imread(tmpFile, cv2.IMREAD_UNCHANGED)

        # 改变尺寸
        srcImgOut = cv2.resize(srcImg, (64, 64))
        saveFile = "./out/" + ico_names_file[i]
        cv2.imwrite(saveFile, srcImgOut)

if __name__ == "__main__":
    change_2()