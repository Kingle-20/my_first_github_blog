from datetime import date
import time
import struct
import socket
from multiprocessing import Pool
import subprocess
import sys
import site
import zlib
import shutil
import re
import os
version = "2026-02-06"


cv_installed = False
try:
    ###
    # pip install opencv-python
    # pip install numpy
    ###
    import cv2
    import numpy as np
    cv_installed = True
except:
    print("未安装CV2或numpy，无法转图片为RGB")

SYNC = b'\xfd\xfc\xfb\xfa'

AES_FLAG = b'\xfa\xfb\xfc\xfd'

IMG_DIR_LEN = 16
IMG_NAME_LEN = 80
MAX_IMG_LEN = 0x300000


def RenameCrypto():
    # 获取当前Python环境的所有site-packages路径
    site_packages_paths = site.getsitepackages()

    # 打印所有路径
    for path in site_packages_paths:
      # print(path)
        if os.path.exists(os.path.join(path, 'crypto')):
            os.rename(os.path.join(path, 'crypto'),
                      os.path.join(path, 'Crypto'))


def InstallCrypto() -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                          "pycryptodome", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])


try:
    from Crypto.Util.Padding import unpad
    from Crypto.Cipher import AES
except ImportError:
    InstallCrypto()
    RenameCrypto()
    from Crypto.Util.Padding import unpad
    from Crypto.Cipher import AES

# 获取imgs的密码，需要蓝网环境


class Enc():
    def __init__(self):
        pass

    def getPwd(self, _serialNo):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = ('10.1.128.1', 10001)
        try:
            self.s.connect(self.addr)
            count = 0
            while count < len(_serialNo):
                c = self.s.send(_serialNo[count:].encode(
                    'ascii'), socket.MSG_DONTROUTE)
                if c <= 0:
                    break
                count += c

            fileinfo_size = struct.calcsize(
                'IIIIIIBBBB24sB12sBBBB4s9sBBBBBBBBBBBBBBBBBBBB24s64sBBBBB53sII')
            buf = self.s.recv(fileinfo_size)
            if buf:
                fields = struct.unpack(
                    'IIIIIIBBBB24sB12sBBBB4s9sBBBBBBBBBBBBBBBBBBBB24s64sBBBBB53sII', buf)

                number = int(fields[48])

                for i in range(number):
                    plate_size = struct.calcsize('9s6s6s50sB')
                    count = 0
                    received_data = b""
                    while count < plate_size:
                        buff = self.s.recv(plate_size-count)
                        if not buff:
                            break
                        received_data += buff

                        count += len(buff)

                    if len(received_data) == plate_size:

                        try:
                            fields = struct.unpack('9s6s6s50sB', received_data)

                            if _serialNo.encode('ascii') == fields[0]:
                                random = fields[1].decode('ascii')
                                return random

                        except (struct.error, TypeError) as e:
                            print('解包错误：', e)

        except socket.error as e:
            print('Socket connection failed:', e)


def mkdir(path):
    if os.path.exists(path):
        return
    try:
        os.makedirs(path)
    except Exception as exc:
        print(f'WARNING :{exc}')


def FileFilterByStr(dirname, filter, ext):
    tmpList = []
    for i in range(len(filter)):
        tmpList.append([])

    for dirpath, dir, filenames in os.walk(dirname):
        for name in filenames:
            path = os.path.join(dirpath, name)
            for f in filter:
                if f in name and ('_decomp' not in path) and (ext == None or os.path.splitext(path)[1][1:] == ext):
                    index = filter.index(f)
                    tmpList[index].append(path)
    ret = []
    for fileList in tmpList:
        ret = ret + fileList
    return ret


def FileFilterByExt(dirname, ext):
    tmpList = []

    for dirpath, dir, filenames in os.walk(dirname):
        for name in filenames:
            path = os.path.join(dirpath, name)
            if os.path.splitext(path)[1][1:] == ext:
                tmpList.append(path)
    return tmpList

# 过滤文件，只留下以SAVE_SENSOR开头的文件


def FileFilterByStrSensorCSV(dir):
    for filename in os.listdir(dir):
        # 检查文件名是否以 'SAVE_SENSOR' 开头
        if filename.startswith('SAVE_SENSOR'):
            read_and_decompress_file(dir, filename)

# 读取压缩文件并解压


def read_and_decompress_file(dir, filename):
    # 设置输出文件名
    set_filename = f"decomp_{filename}"
    output_filename = os.path.join(dir, set_filename)
    with open(os.path.join(dir, filename), 'rb') as f:
        with open(output_filename, 'w', encoding='utf-8') as out_f:
            # 列标题未压缩，所以要先读取列标题
            line = f.readline()
            out_f.write(line.decode('utf-8').replace('\n', ''))
            while True:
                compressed_size_bytes = f.read(8)
                if not compressed_size_bytes:
                    break  # 文件结束
                compressed_size = int.from_bytes(
                    compressed_size_bytes, byteorder='little')
                try:
                    # 读取压缩数据
                    compressed_data = f.read(compressed_size)
                    if len(compressed_data) != compressed_size:
                        break  # 未读取到完整的数据
                    decompressed_data = zlib.decompress(compressed_data)
                    out_f.write(decompressed_data.decode(
                        'utf-8').replace('\n', ''))
                    # print(decompressed_data.decode('utf-8'))  # 解码为字符串
                except zlib.error as e:
                    print(f"解压发生错误: {e}")
                except Exception as e:
                    return


def debug_gray_2_rgb(img_in):
    try:
        img_out = cv2.cvtColor(img_in, cv2.COLOR_GRAY2BGR)
        img_out[img_in == 0] = [0, 0, 0]  # FREE_SPACE
        img_out[img_in == 1] = [0, 200, 0]  # DNCRGN
        img_out[img_in == 2] = [0, 50, 150]  # 门槛
        img_out[img_in == 3] = [0, 150, 50]  # 地毯
        img_out[img_in == 150] = [0, 0, 120]  # PATH
        img_out[img_in == 200] = [0, 0, 255]  # VIRTUAL
        img_out[img_in == 235] = [18, 105, 238]  # CHAIR
        img_out[img_in == 240] = [75, 25, 175]  # CV_OBSTACLE
        img_out[img_in == 241] = [25, 175, 75]  # DEPTH_OBSTACLE
        img_out[img_in == 245] = [175, 75, 25]  # SONIC_OBSTACLE
        img_out[img_in == 246] = [75, 25, 50]  # CLIFF_OBSTACLE
        img_out[img_in == 243] = [0, 150, 150]  # FVWALL_INFLATED_OBSTACLE
        img_out[img_in == 247] = [0, 50, 255]  # FVWALL_OBSTACLE
        img_out[img_in == 248] = [200, 255, 200]  # STATION_OBSTACLE
        img_out[img_in == 249] = [0, 165, 255]  # WALL_VIRTUAL_EXTEND
        img_out[img_in == 250] = [0, 165, 255]  # WALL_CONFUSION
        img_out[img_in == 251] = [0, 165, 255]  # WALL_EXACT
        img_out[img_in == 252] = [50, 50, 50]  # CIRCUMSRIBED_INFLATED_OBSTACLE
        img_out[img_in == 253] = [100, 100, 100]  # INSCRIBED_INFLATED_OBSTACLE
        img_out[img_in == 254] = [255, 255, 255]  # LETHAL_OBSTACLE
        img_out[img_in == 255] = [127, 127, 127]  # NO_INFORMATION
        return img_out
    except:
        return None


class LogDecomp():
    def __init__(self, file, delOrigFile=0, maxFileSize=0xf00000, processCb=None, type=0) -> None:
        self.file = file
        self.fileSize = os.path.getsize(file)
        self.fd = open(file, 'rb')
        ext = os.path.splitext(file)[1][1:]
        self.outFileFmt = file[:-1 * (len(ext) + 1)] + '_decomp_%02d.' + ext
        self.out = None
        self.outId = 0
        self.delOrig = delOrigFile
        self.maxFileSize = maxFileSize
        self.processCb = processCb
        self.type = type

    def DecompData(self, data):
        if self.out == None:
            if self.type:
                self.out = open(self.outFileFmt % self.outId, 'wb')
            else:
                self.out = open(self.outFileFmt %
                                self.outId, 'w', encoding='utf-8')
        try:
            decompressed_data = zlib.decompress(data)
            if self.type:
                if len(decompressed_data) + self.out.tell() > self.maxFileSize:
                    self.out.flush()
                    self.out.close()
                    self.outId += 1
                    self.out = open(self.outFileFmt % self.outId, 'wb')
                self.out.write(decompressed_data)
            else:
                str = decompressed_data.decode('utf-8',  errors='ignore')
                if len(str) + self.out.tell() > self.maxFileSize:
                    self.out.flush()
                    self.out.close()
                    self.outId += 1
                    self.out = open(self.outFileFmt %
                                    self.outId, 'w', encoding='utf-8')
                self.out.writelines(str)
        except zlib.error as e:
            print(f"Error during decompression: {e}")

    def Decomp(self):
        filename = os.path.basename(self.file)
        print(f'decoding: {filename}')
        while True:
            str = self.fd.read(4)
            if str == b'':
                break
            if str == SYNC:
                str = self.fd.read(4)
                len = int.from_bytes(str, byteorder='little')
                # print(len)
                str = self.fd.read(len)
                self.DecompData(str)
                if self.processCb != None:
                    self.processCb(filename, self.fd.tell(), self.fileSize)

    def Close(self):
        self.fd.close()
        if (self.delOrig):
            os.unlink(self.file)
        self.out.flush()
        self.out.close()


class LogsDecomp():
    def __init__(self, dir, filter, ext=None, delOrigFile=0, maxFileSize=0xf00000, processCb=None, type=0) -> None:
        self.dir = dir
        self.filter = filter
        self.logExt = ext
        self.delOrigFile = delOrigFile
        self.maxFileSize = maxFileSize
        self.processCb = processCb
        self.type = type

    def FilterLog(self) -> list:
        logs = FileFilterByStr(self.dir, self.filter, self.logExt)
        print(logs)
        return logs

    def DecompFile(self, f):
        de = LogDecomp(f, self.delOrigFile, self.maxFileSize,
                       processCb=self.processCb, type=self.type)
        de.Decomp()
        de.Close()

    def Decomp(self):
        logs = self.FilterLog()
        for log in logs:
            self.DecompFile(log)


def ProcessCb(file, bytes, total):
    p = bytes * 100 / total
    # print(f'\r{file} : {p:.01f}%',end='')


class Aes():
    def __init__(self, key) -> None:
        self.cipher = AES.new(key, AES.MODE_ECB)

    def encrypt(self, plain_text):
        encrypted = self.cipher.encrypt(plain_text)
        return encrypted

    def decrypt(self, cipher_text):
        decrypted = self.cipher.decrypt(cipher_text)
        return decrypted


class ImgsDecode():
    def __init__(self,  dir, cb=None, pw='') -> None:
        self.dir = dir
        self.cb = cb
        self.pw = pw.encode('utf-8').ljust(32, b'\x00')
        # print('pw: %sx' % self.pw )

    def SaveImg(self, dir, name, data):
        if dir != '':
            mkdir(f'{self.dir}/{dir}')
        dstFile = f'{self.dir}/{dir}/{name}'
        outfd = open(dstFile, 'wb')
        outfd.write(data)
        outfd.flush()
        outfd.close()

    def AesDec(self, data):
        aes = Aes(self.pw)
        return aes.decrypt(data)

    def SplitImgs(self, data, l, aesFlag):
        offset = 0
        predata = data
        if aesFlag and l >= 1024:
            try:
                dec = self.AesDec(data[:1024])
            except Exception as exc:
                print(f"Error during Aes dec:{exc}, 验证码错误? ")
                return -1
            predata = dec + data[1024:]

        try:
            decompressed_data = zlib.decompress(predata)
            decompressed_data.decode('utf-8',  errors='ignore')
        except zlib.error as e:
            if aesFlag:
                print(f"Error during decompression: {e}, 验证码错误?")
            else:
                print(f"Error during decompression: {e}")
            return -1

        while (offset < len(decompressed_data)):
            sync = decompressed_data[offset: offset + 4]
            if sync == b'':
                break
            if sync != SYNC:
                break
            offset += 4
            dir = decompressed_data[offset: offset + IMG_DIR_LEN].decode(
                'utf-8',  errors='ignore').split('\x00')[0]
            offset += IMG_DIR_LEN
            name = decompressed_data[offset: offset + IMG_NAME_LEN].decode(
                'utf-8',  errors='ignore').split('\x00')[0]
            offset += IMG_NAME_LEN
            # print(name)
            if dir == b'' or name == '':
                break

            l = int.from_bytes(
                decompressed_data[offset: offset + 4], byteorder='little')
            if (l > MAX_IMG_LEN):
                break
            offset += 4
            # print(len)
            self.SaveImg(dir, name, decompressed_data[offset: offset + l])
            offset += l
        return 0

    def DecodeFile(self, file) -> None:
        filename = os.path.basename(file)

        print(f'decoding: {filename}')
        fileSize = os.path.getsize(file)
        fd = open(file, 'rb')
        start = 1
        aesFlag = False
        while True:
            str = fd.read(4)
            if str == b'':
                break
            if str == AES_FLAG and start == 1:
                start = 0
                aesFlag = True
                str = fd.read(4)

            if str != SYNC:
                break

            str = fd.read(4)
            len = int.from_bytes(str, byteorder='little')
            # print(len)
            if (len > MAX_IMG_LEN):
                break
            str = fd.read(len)
            if self.SplitImgs(str, len, aesFlag) != 0:
                break
            if self.cb != None:
                self.cb(filename, fd.tell(), fileSize)
        fd.close()

    def Decode(self) -> None:
        files = FileFilterByExt(self.dir, 'img')
        files_2 = FileFilterByExt(self.dir, 'ex')
        
        for f in files:
            self.DecodeFile(f)
        for f in files_2:
            self.DecodeFile(f)


class LogAnalysis():
    def __init__(self, mapinfodatabase=None):
        self.cv2_included = False
        self.write_analysis = True
        self.compressedLog = True
        self.compressedImg = True
        self.compressedSensorCSV = True
        self.compressedCA7 = True
        self.includeDeviceCtrl = False
        self.includeAppInteract = False
        self.custom_patterns_kw = []
        
        # 线程数
        self.n_proc = 10
        self.vpn = False
        self.sn_pwd = {}
        if os.path.exists(mapinfodatabase):
            self.map_info_data_dir = mapinfodatabase
        else:
            self.map_info_data_dir = None

    def set_device_ctrl(self, flag):
        self.includeDeviceCtrl = flag

    def set_cv2(self, flag):
        self.cv2_included = flag

    def set_app_interact(self, flag):
        self.includeAppInteract = flag

    def set_custom_pattern(self, custom_patterns_kw = []):
        self.custom_patterns_kw = custom_patterns_kw

    def set_vpn(self, flag):
        self.vpn = flag

    def set_sn_pwd(self, sn_pwd):
        self.sn_pwd.update(sn_pwd)

    def process_astar_dict(self, astar_fp):
        dict_astar = {}
        with open(astar_fp, "r", encoding="utf8") as f:
            all_lines = f.readlines()
            for line in all_lines:
                line = line.rstrip()
                if len(line) > 10:
                    key = line[-23:]
                    dict_astar[key] = []
                elif len(line) > 2:
                    point = [int(s) for s in line.split(" ")]
                    dict_astar[key].append(point)
                else:
                    pass
            # for k, v in dict_astar.items():
            #   print(k, len(v))
        return dict_astar

    def pic_to_rgb(self, pic_path, pic_out_path, all_pic, k, v):
        if (all_pic is None) or (pic_path in all_pic):
            try:
                gray_pic = cv2.imdecode(
                    np.fromfile(pic_path, dtype=np.uint8), -1)
            except Exception as e:
                gray_pic = None
            rgb_pic = debug_gray_2_rgb(gray_pic)


            if v is None and rgb_pic is not None:
                cv2.imencode(".png", rgb_pic)[1].tofile(pic_out_path)
            if rgb_pic is not None:
                if v is None or v[0][0] < 0:
                    # 将图像数据转换为字节
                    data = gray_pic.tobytes()
                    
                    # 解析头部信息
                    head = data[16:20]
                    if head != b'PATH':
                        raise ValueError("无效的路径数据头部")
                    
                    # 解析路径点数量
                    path_pts_num = struct.unpack('<H', data[20:22])[0]  # little-endian uint16
                    # 解析路径点坐标
                    path_points = []
                    for i in range(path_pts_num):
                        offset = 22 + i * 4  # 6字节头部 + 每个点4字节(x,y)
                        x, y = struct.unpack('<HH', data[offset:offset+4])  # little-endian uint16
                        path_points.append((x, y))
                    v = path_points
                for p in v:
                    # pass
                    cv2.circle(rgb_pic, (p[0], p[1]), 0, [255, 0, 0])
                if (rgb_pic.shape[0] > 1000 or rgb_pic.shape[1] > 1000):
                    cv2.circle(rgb_pic, (v[0][0], v[0][1]), 2, [0, 0, 255], -1)
                    cv2.circle(rgb_pic, (v[-1][0], v[-1]
                               [1]), 2, [0, 255, 0], -1)
                else:
                    cv2.circle(rgb_pic, (v[0][0], v[0][1]), 0, [0, 0, 255], -1)
                    cv2.circle(rgb_pic, (v[-1][0], v[-1]
                               [1]), 0, [0, 255, 0], -1)
                cv2.imencode(".png", rgb_pic)[1].tofile(pic_out_path)
        return None

    def process_astar_pic(self, astar_dict={}, folder_in="", folder_out=""):
        if not os.path.exists(folder_in):
            return
        if not os.path.exists(folder_out):
            os.mkdir(folder_out)
        all_pic = [os.path.join(folder_in, png)
                   for png in os.listdir(folder_in)]
        for pic in all_pic:
            key = os.path.basename(pic).replace("_Astarplanmap.png", "")
            if (key not in astar_dict.keys()):
                astar_dict[key] = [[-1, -1], [-1, -1]]
        pool = Pool(processes=self.n_proc)
        result = []

        for k, v in astar_dict.items():
            pic_path = os.path.join(folder_in, k) + "_Astarplanmap.png"
            pic_out_path = os.path.join(folder_out, k) + "_AstarDebug.png"
            result.append(pool.apply_async(self.pic_to_rgb, args=(
                pic_path, pic_out_path, all_pic, k, v)))
            # pic_to_rgb(pic_path, pic_out_path, all_pic, k, v)
        pool.close()
        pool.join()

    def process_coverage_pic(self, folder_in="", folder_out=""):
        if not os.path.exists(folder_in):
            return
        if not os.path.exists(folder_out):
            os.mkdir(folder_out)
        all_pic = [png for png in os.listdir(
            folder_in) if png.endswith("_planMap.png")]
        pool = Pool(processes=self.n_proc)
        result = []
        for pic in all_pic:
            pic_path = os.path.join(folder_in, pic)
            pic_out_path = os.path.join(folder_out, pic)
            result.append(pool.apply_async(self.pic_to_rgb, args=(
                pic_path, pic_out_path, None, None, None)))
        pool.close()
        pool.join()

    def filter_log_ezdsp(self, log_fp, ifprint=True, ifwrite=False, i=0, total=0):
        if not os.path.exists(log_fp):
            print("{:s} not exist".format(log_fp))
            return
        else:
            print("{:02d}/{:02d} {:s}".format(i, total, log_fp))
        restart_pattern = re.compile(r'\bMediaModuleInit end\b')
        restart_pattern2 = re.compile(r'\b上报APP异常DECI_INIT\b')
        restart_pattern3 = re.compile(r'\b设置刚开机标志位\b')

        all_patterns_kw = []
        all_patterns_kw.append(r'MapCleanOp')
        all_patterns_kw.append(r'deciVersion')
        all_patterns_kw.append(r'Taskmanager from')
        all_patterns_kw.append(r'BaseStation from')
        all_patterns_kw.append(r'Routing from')
        all_patterns_kw.append(r'Mapping from')
        all_patterns_kw.append(r'Inspection from')
        all_patterns_kw.append(r'Relocation from')
        all_patterns_kw.append(r'RemoteControl from')
        all_patterns_kw.append(r'Coverage from')
        all_patterns_kw.append(r'污渍区域')
        all_patterns_kw.append(r'Coverage2 from')
        all_patterns_kw.append(r'CleanTest from')
        all_patterns_kw.append(r'Edgewise from')
        all_patterns_kw.append(r'Soil from')
        all_patterns_kw.append(r'Elevator from')
        all_patterns_kw.append(r'ElevatorAPP from')
        all_patterns_kw.append(r'now state : Relocalization')
        all_patterns_kw.append(r'IfNeedTakeElevator')
        all_patterns_kw.append(r'首次全屋清扫')
        all_patterns_kw.append(r'首次选区清扫')
        all_patterns_kw.append(r'自定义选区清扫')
        all_patterns_kw.append(r'首次临时划区清扫')
        all_patterns_kw.append(r'指定顺序清扫')
        all_patterns_kw.append(r'首次加扫清扫')
        all_patterns_kw.append(r'里程计')
        all_patterns_kw.append(r'清除APP异常')
        all_patterns_kw.append(r'发送重定位')
        all_patterns_kw.append(r'near by base or having base')
        all_patterns_kw.append(r'eReloState')
        all_patterns_kw.append(r'change room, old')
        all_patterns_kw.append(r'resume_data')
        all_patterns_kw.append(r'ResetRoommap')
        all_patterns_kw.append(r'RefreshCgMap')
        all_patterns_kw.append(r'清扫计数')
        all_patterns_kw.append(r'阻塞指令')
        all_patterns_kw.append(r'CleanSpeed')
        all_patterns_kw.append(r'cfg.mapParam.ptzCtrl.command')
        all_patterns_kw.append(r'Change slam map')
        # all_patterns_kw.append(r'UpdateCgMaps')
        all_patterns_kw.append(r'SwitchRoomSwitch')
        # all_patterns_kw.append(r'DoLocalPlan')
        # all_patterns_kw.append(r'UpdateTask')
        # all_patterns_kw.append(r'DP Status')
        all_patterns = re.compile("|".join(map(re.escape, all_patterns_kw)))

        # 自定义关键词
        if len(self.custom_patterns_kw) != 0:
            custom_patterns = re.compile("|".join(map(re.escape, self.custom_patterns_kw)))
        else:
            custom_patterns = re.compile("gaoboshun")


        warn_patterns_kw = []
        # warn_patterns_kw.append(r'cliff')
        warn_patterns_kw.append(r'abnhand from')
        warn_patterns_kw.append(r'StuckHandler from')
        warn_patterns_kw.append(r'ResetPoseMonitor')
        warn_patterns_kw.append(r'block_state is')
        warn_patterns_kw.append(r'CROOS from')
        warn_patterns_kw.append(r'WSOOS from')
        warn_patterns_kw.append(r'FROOS from')
        warn_patterns_kw.append(r'FROOSMat from')
        warn_patterns_kw.append(r'BACKOOS from')
        warn_patterns_kw.append(r'NARROWOOS from')
        warn_patterns_kw.append(r'STEPOOS from')
        warn_patterns_kw.append(r'm_ConnectToBase')
        warn_patterns_kw.append(r'不生效')
        warn_patterns_kw.append(r'快速排除')
        warn_patterns_kw.append(r'无法到达区域内部，跳过区域')
        warn_patterns_kw.append(r'任务有漏扫，对漏扫区域尝试一遍后再终止')
        # warn_patterns_kw.append(r'重定位')
        warn_patterns_kw.append(r'关闭深度图')
        warn_patterns_kw.append(r'EWOOS from')
        warn_patterns_kw.append(r'executeGridMapClear')
        warn_patterns_kw.append(r'set clearWaypoint!!!')
        warn_patterns_kw.append(r'零漂')
        warn_patterns_kw.append(r'PassedNarrowChannel')
        warn_patterns_kw.append(r'第一次开始，设置清扫参数')
        warn_patterns_kw.append(r'SaveResumeCoverageInfo')
        warn_patterns_kw.append(r'SetRCInterrupted')
        # warn_patterns_kw.append(r'setFakePoint globa')
        warn_patterns_kw.append(r'SetEnableSLAMFlag')
        warn_patterns_kw.append(r'set close slam flag')
        warn_patterns = re.compile("|".join(map(re.escape, warn_patterns_kw)))

        err_patterns_kw = []
        err_patterns_kw.append(r'\[ERR\]')
        err_patterns_kw.append(r'上报APP异常')
        err_patterns_kw.append(r'Dump stack')
        err_patterns_kw.append(r'ResetRoommap fail')
        err_patterns_kw.append(r'死循环')
        err_patterns_kw.append(r'段错误')
        err_patterns_kw.append(r'SetDebugLog')
        # err_patterns_kw.append(r'tPose: [')
        # err_patterns_kw.append(r'add_narrow')
        # err_patterns_kw.append(r'Decision abnormal')
        # err_patterns_kw.append(r'polyVirtualWalls')
        err_patterns = re.compile("|".join(map(re.escape, err_patterns_kw)))

        if self.includeDeviceCtrl:
            all_patterns_kw.append('SetCleanDeviceCtrl')
            all_patterns_kw.append('roller_ctrl_callback')
            all_patterns_kw.append('fan_duct_ctrl_callback')
            all_patterns_kw.append('lift_motor_ctrl_callback')
            all_patterns_kw.append('mop_lift_ctrl_callback')
            all_patterns_kw.append('mop_extend_ctrl_callback')
            all_patterns_kw.append('roller_mop_ctrl_callback')
            all_patterns_kw.append('roller_vacuum_ctrl_callback')
            all_patterns_kw.append('vacuum_lift_ctrl_callback')
            all_patterns_kw.append('edge_brush_ctrl_callback')
            all_patterns_kw.append('edge_brushr_ctrl_callback')
            all_patterns_kw.append('edge_brushre_ctrl_callback')
            all_patterns_kw.append('edge_brushl_ctrl_callback')
            all_patterns_kw.append('fan_ctrl_callback')
            all_patterns_kw.append('clean_pump_ctrl_callback')
            all_patterns_kw.append('dirty_pump_ctrl_callback')
            # all_patterns_kw.append('CloseWater')
            all_patterns_kw.append('device_index')
            all_patterns_kw.append('设置尘推')
            all_patterns_kw.append('设置前序清扫')
            all_patterns_kw.append('地毯上')
            all_patterns_kw.append('进脏污')
            all_patterns_kw.append('出脏污')
            all_patterns_kw.append('UpdateCleanPumpIntervalTiming')
            all_patterns_kw.append('IncreaseLiftMotor')
            all_patterns_kw.append('ResetLiftMotor')
            all_patterns = re.compile(
                "|".join(map(re.escape, all_patterns_kw)))

        app_patterns_kw = []
        app_patterns_kw.append(r'IS_NEW_MAP')
        app_patterns_kw.append(r'SendTakeGlobalOffsetInfo')
        app_patterns_kw.append(r'Static Map')
        app_patterns_kw.append(r'SendTakeElevatorInfo')
        app_patterns_kw.append(r'SendElevatorInfoToAPP')
        app_patterns_kw.append(r'SendAutoDoorOp')
        app_patterns_kw.append(r'SendGateOp')
        app_patterns_kw.append(r'iFC: 1')
        app_patterns_kw.append(r'全量压缩路径')
        app_patterns_kw.append(r'清除APP路径')
        app_patterns_kw.append(r'cleanArea:')
        app_patterns_kw.append(r'ifFinishedClean')
        app_patterns_kw.append(r'[MAPDATA_BUFFER] pose')
        app_patterns_kw.append(r'Path_num')
        app_patterns_kw.append(r'mappinginfo: area:')
        app_patterns_kw.append(r'inspectioninfo:')
        app_patterns_kw.append(r'SetSendCleanInfo')
        app_patterns_kw.append(r'charger')
        app_patterns = re.compile("|".join(map(re.escape, app_patterns_kw)))

        ign_patterns_kw = []
        ign_patterns_kw.append(r'MOTOR_LIFTING')
        ign_patterns_kw.append(r'MOTOR_DROPING')
        ign_patterns_kw.append(r'LIFT_MOTOR_UP_NOT_DETECTED')
        ign_patterns_kw.append(r'PATH_THROUGH_PEOPLE')
        ign_patterns = re.compile("|".join(map(re.escape, ign_patterns_kw)))

        f_out = []

        with open(log_fp, "r", encoding="utf-8") as f:
            if "ezdsp" in log_fp:
                time_key = os.path.basename(log_fp)[16:16+18]
                decomp_part = " " + os.path.basename(log_fp)[-6:-4]
            else:
                time_key = os.path.basename(log_fp)[18:18+18]
                decomp_part = ""

            for i, line in enumerate(f):
                if restart_pattern.search(line) or restart_pattern2.search(line) or restart_pattern3.search(line):
                    print("重启" + "=" * 100)
                    if (ifwrite):
                        f_out.append("{}\n".format("=" * 100))
                ignore_line = False
                if ign_patterns.search(line):
                    ignore_line = True
                if not ignore_line:
                    log_line = False
                    if all_patterns.search(line):
                        if (ifprint):
                            print(os.path.basename(log_fp),
                                  i + 1, line.rstrip())
                        if (ifwrite):
                            f_out.append("{}{} {} {}\n".format(time_key, decomp_part, i + 1, line.rstrip()))
                        log_line = True
                    if not log_line:
                        if warn_patterns.search(line):
                            if (ifprint):
                                print(os.path.basename(log_fp), i + 1,
                                      "\033[33m" + line.rstrip() + "\033[0m")
                            if (ifwrite):
                                f_out.append("{}{} {} {}\n".format(time_key, decomp_part, i + 1, line.rstrip()))
                            log_line = True
                    if not log_line:
                        if err_patterns.search(line):
                            if (ifprint or True):
                                print(os.path.basename(log_fp), i + 1,
                                      "\033[31m" + line.rstrip() + "\033[0m")
                            if (ifwrite):
                                f_out.append("{}{} {} {}\n".format(time_key, decomp_part, i + 1, line.rstrip()))
                            log_line = True
                    if not log_line:
                        if custom_patterns.search(line):
                            if (ifprint or True):
                                print(os.path.basename(log_fp), i + 1,
                                      "\033[31m" + line.rstrip() + "\033[0m")
                            if (ifwrite):
                                f_out.append("{}{} {} {}\n".format(time_key, decomp_part, i + 1, line.rstrip()))
                            log_line = True
                    if not log_line and self.includeAppInteract:
                        if app_patterns.search(line):
                            if (ifprint):
                                print(os.path.basename(log_fp),
                                      i + 1, line.rstrip())
                            if (ifwrite):
                                f_out.append("{}{} {} {}\n".format(time_key, decomp_part, i + 1, line.rstrip()))
                            log_line = True
        return f_out

    def filter_log_ezapp(self, log_fp, ifprint=True, ifwrite=False, i=0, total=0):
        if not os.path.exists(log_fp):
            print("{:s} not exist".format(log_fp))
            return
        else:
            print("{:02d}/{:02d} {:s}".format(i, total, log_fp))
        restart_pattern = re.compile(r'\b======= EZVIZ INIT FINISHED =======\b')
        restart_pattern2 = re.compile(r'\b上报APP异常DECI_INIT\b')
        restart_pattern3 = re.compile(r'\b设置刚开机标志位\b')
        
        all_patterns_kw = []
        all_patterns_kw.append(r'robot_ui_change_promptBox_info')
        all_patterns = re.compile("|".join(map(re.escape, all_patterns_kw)))

        f_out = []

        with open(log_fp, "r", encoding="utf-8") as f:
            try:
                for i, line in enumerate(f):
                    if restart_pattern.search(line) or restart_pattern2.search(line) or restart_pattern3.search(line):
                        print("重启" + "=" * 100)
                        if (ifwrite):
                            f_out.append("{}\n".format("=" * 100))
                    if all_patterns.search(line):
                        if (ifprint):
                            print(os.path.basename(log_fp),
                                  i + 1, line.rstrip())
                        if (ifwrite):
                            f_out.append("{} {} {}\n".format(os.path.basename(
                                log_fp)[11:11+14], i + 1, line.rstrip()))
            except Exception as e:
                f_out.append("{} encoding error!\n".format(
                    os.path.basename(log_fp)[11:11+14]))
                print(
                    "\033[31m" + "{:s} error".format(os.path.basename(log_fp)) + "\033[0m")
        return f_out

    # 负责解压和重命名ezdsp、img、ca7、sensorcsv
    def pre_process_log_dir(self, log_dir, pwd):
        if (not os.path.exists(log_dir)):
            print("{:s} 不存在,终止分析".format(log_dir))
            return False
        
        if self.compressedImg == True:
            l = ImgsDecode(log_dir, cb=ProcessCb, pw=pwd)
            l.Decode()
            
        if self.compressedLog == True:
            l = LogsDecomp(log_dir, ['ezdsp', 'ezdeci'], ext='log', processCb=ProcessCb)
            l.Decomp()
            
        if self.compressedSensorCSV == True:
            FileFilterByStrSensorCSV(os.path.join(log_dir))

        if self.compressedCA7 == True:
            l1 = LogsDecomp(log_dir, ['CA7_datalog', 'ca7_datalog'],
                            ext='log', processCb=ProcessCb, type=1)
            l1.Decomp()

        return True

    def save_mapinfo(self, log_dir):
        if self.map_info_data_dir is None:
            return
        src = ""
        if os.path.exists(os.path.join(log_dir, "mntdebug", "MapInfo")):
            src = os.path.join(log_dir, "mntdebug", "MapInfo")
        elif os.path.exists(os.path.join(log_dir, "mapinfo")):
            src = os.path.join(log_dir, "mapinfo")
        else:
            return

        if not os.path.exists(self.map_info_data_dir):
            os.mkdir(self.map_info_data_dir)
        # 将Mapping中的Background_Explored图片拷贝至src中
        if os.path.exists(os.path.join(log_dir, "Mapping")):
            png_list = [f for f in os.listdir(os.path.join(
                log_dir, "Mapping")) if "Background_Explored" in f]
            for f in png_list:
                print("Copy {:s} to MapInfo folder".format(f))
                shutil.copy(os.path.join(log_dir, "Mapping", f),
                            os.path.join(src, f))

        today = date.today()
        date_str = today.strftime("-%Y-%m-%d")
        dst = os.path.join(self.map_info_data_dir,
                           os.path.basename(log_dir) + date_str, "MapInfo")
        if not os.path.exists(dst):
            print("Copy Mapinfo from {:s} -> {:s}".format(src, dst))
            shutil.copytree(src, dst)
        else:
            print("MapInfo already backed up, {:s}".format(dst))

    def process_ezdsp_log_dir(self, log_dir):
        self.save_mapinfo(log_dir)

        if self.cv2_included:
            print("AstarDebug")
            astarFolder = os.path.join(log_dir, "Astar")
            astarDebugFolder = os.path.join(log_dir, "AstarDebug")
            if not os.path.exists(astarFolder):
              astarFolder = os.path.join(log_dir, "debug", "Astar")
              astarDebugFolder = os.path.join(log_dir, "debug", "AstarDebug")

            if (os.path.exists(astarFolder)):
                astar_txt_list = [os.path.join(astarFolder, p) for p in os.listdir(astarFolder) if p.endswith(".txt")]
                print(astar_txt_list)
                if len(astar_txt_list) == 0:
                    print("无AstarDebug.txt")
                    astar_dict = {}
                    self.process_astar_pic(astar_dict, astarFolder, astarDebugFolder)

                for astar_txt in astar_txt_list:
                    print(astar_txt)
                    astar_dict = self.process_astar_dict(astar_txt)
                    self.process_astar_pic(astar_dict, astarFolder, astarDebugFolder)
            else:
                print("Astar不存在\n")

        if self.cv2_included:
            print("CoverageDebug")
            coverageFolder = os.path.join(log_dir, "Coverage")
            coverageDebugFolder = os.path.join(log_dir, "CoverageDebug")
            if not os.path.exists(coverageFolder):
              coverageFolder = os.path.join(log_dir, "debug", "Coverage")
              coverageDebugFolder = os.path.join(log_dir, "debug", "CoverageDebug")
            if (os.path.exists(coverageFolder)):
                self.process_coverage_pic(coverageFolder, coverageDebugFolder)
            else:
                print("Coverage不存在\n")

        if not self.write_analysis:
            return
        print("Writing file")
        pool = Pool(processes=self.n_proc)
        result = []
        # 解压缩
        if self.compressedLog == True:
            log_list = self._filter_files(log_dir, ["ezdsp_", "ezdeci_"], [".bak"])

        for i, f in enumerate(log_list):
            result.append(pool.apply_async(self.filter_log_ezdsp,
                          args=(f, False, True, i + 1, len(log_list))))
        pool.close()
        pool.join()

        with open(os.path.join(log_dir, "e_log_analysis.log"), "w", encoding="utf-8") as log_out:
            for r in result:
                log_out.writelines(r.get())

    def _filter_and_move_files(self, log_dir, includes, excludes, new_folder_name):
        log_list= []
        for root, dirs, files in os.walk(log_dir):
            for file in files:
                # 检查文件名是否包含includes中任意一个，不包含exclude中任意一个
                in_list = any([i in file for i in includes]) and all([e not in file for e in excludes])
                if in_list:
                    # 获取文件的绝对路径并添加到结果列表
                    full_path = os.path.join(root, file)
                    log_list.append(full_path)
        print(new_folder_name, log_list)
        for log_path in log_list:
            parent = os.path.dirname(log_path)
            basename = os.path.basename(log_path)
            if not os.path.exists(os.path.join(parent, new_folder_name)):
                os.mkdir(os.path.join(parent, new_folder_name))
            shutil.move(log_path, os.path.join(parent, new_folder_name, basename + ".bak"))
            
    def _filter_files(self, log_dir, includes, excludes):
        log_list= []
        for root, dirs, files in os.walk(log_dir):
            for file in files:
                # 检查文件名是否包含includes中任意一个，不包含exclude中任意一个
                in_list = any([i in file for i in includes]) and all([e not in file for e in excludes])
                if in_list:
                    # 获取文件的绝对路径并添加到结果列表
                    full_path = os.path.join(root, file)
                    log_list.append(full_path)
        return log_list
    
    # 负责移动原始ezdsp、img、ca7、sensorcsv
    def rename_logs(self, log_dir):
        if self.compressedLog == True:
            self._filter_and_move_files(log_dir, ["ezdeci", "ezdsp"], [".bak", "decomp"], "compressedDeci")

        if self.compressedImg == True:
            self._filter_and_move_files(log_dir, [".img", ".ex"], [".bak"], "compressedImg")
            
        if self.compressedSensorCSV == True:
            self._filter_and_move_files(log_dir, ["SAVE_SENSOR", "sensor_csv"], ["decomp", ".bak"], "compressedCSV")

        if self.compressedCA7 == True:
            self._filter_and_move_files(log_dir, ["ca7", "CA7"], ["decomp", ".bak"], "compressedCA7")

        
    def process_ezapp_log_dir(self, log_dir):
        pool = Pool(processes=self.n_proc)
        result = []

        log_list = self._filter_files(log_dir, ["ezapp", "EZAPP"], [".bak", "e_log_analysis"])

        for i, f in enumerate(log_list):
            result.append(pool.apply_async(self.filter_log_ezapp,
                          args=(f, False, True, i + 1, len(log_list))))
        pool.close()
        pool.join()
        with open(os.path.join(log_dir, "e_log_analysis_ezapp.log"), "w", encoding="utf-8") as log_out:
            for r in result:
                log_out.writelines(r.get())

    def main(self, log_dirs):
        for log_dir in log_dirs:
            print(log_dir)
            pwd = ""
            sn = ""
            for root, dirs, files in os.walk(log_dir):
                for file in files:
                    if file.endswith(".img") or file.endswith(".ex"):
                        img = file.replace(".img", "").replace(".ex", "")
                        sn = img[-9:]
                        print(sn)
                        break
                        
            if sn != "":
                if not self.vpn:
                    enc = Enc()
                    pwd = enc.getPwd(sn)
                    print("{:s} -> {:s}".format(sn, pwd))
                else:
                    if sn in self.sn_pwd.keys():
                        pwd = self.sn_pwd[sn]
                    print("sn: {:s}, pwd: {:s}".format(sn, pwd))
            else:
                print("未获取序列号")
            if self.write_analysis and (not self.pre_process_log_dir(log_dir, pwd)):
                print("失败")
                return

        for log_dir in log_dirs:
            self.rename_logs(log_dir)

        for log_dir in log_dirs:
            self.process_ezdsp_log_dir(log_dir)
            self.process_ezapp_log_dir(log_dir)


if __name__ == "__main__":
    log_dirs = []
    map_info_data_dir = os.path.join("D:\\", "Log", "MapInfoDatabase")
    la = LogAnalysis(mapinfodatabase=map_info_data_dir)
    la.set_cv2(cv_installed)


    # 是否处于vpn环境（如果用VPN，无法解析imgs，除非知道密码，密码可以通过手动设置的方式设置给LogAnalysis，密码不正确的情况下无法解析imgs）
    # la.set_vpn(True)
    # sn_pwd = {"BE6788037": "QVWVHH",
    #          }
    # la.set_sn_pwd(sn_pwd)

    # 仅仅需要某台车的密码时，反注释以下几行内容
    # enc = Enc()
    # sn = "BG9853649"
    # pwd = enc.getPwd(sn)
    # print("{:s} - {:s}".format(sn, pwd))
    # exit(0)

    root_dir = os.path.join("C:\\", "Log")
    log_dirs.append(os.path.join(root_dir, "BE5795975"))
    # log_dirs.append(os.path.join(root_dir, "0219日志", "4957机器-0218-6-启动清洁出现一次机器一直暂停不能继续-CPU卡了"))
    # log_dirs.append(os.path.join(root_dir, "0219日志", "BF0738320-焦化食堂-一处backoos的轨迹不好"))

    # 日志分析中是否带上清洁机构
    # la.set_device_ctrl(True)
    # 日志分析中是否带上app交互
    # la.set_app_interact(True)

    custom_pattern_kw = []
    # custom_pattern_kw.append("SCPub")
    # custom_pattern_kw.append("SetSendCarpet")
    # custom_pattern_kw.append("charger(")
    # custom_pattern_kw.append("IsExistExploreData")
    # custom_pattern_kw.append("EZ_RESUME_MAPPING_NUM")
    la.set_custom_pattern(custom_pattern_kw)
    
    
    start_time = time.time()
    la.main(log_dirs)
    end_time = time.time()
    print("TotalTime: {:.2f}s".format(end_time - start_time))
