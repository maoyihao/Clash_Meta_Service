import os
import time
import requests
import subprocess
import sys

#获取用户路径
user_path = os.path.expanduser("~")

def notification(text, sleep_time = 3):
    os.system('shutdown -s -t 60 -c "{}"'.format(text))
    time.sleep(sleep_time)
    os.system('shutdown -a')

def download(url, filename=None):
    down_res = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(down_res.content)

def finish():
    os.system('cls')
    continues = input('安装完成，是否启动服务？(Y/N)：')
    if continues == 'Y' or continues == 'y':
        os.system('cls')
        subprocess.Popen(os.path.join(user_path, "clash.exe") + ' start', shell=True)
        notification('正在启动', 3)
        sys.exit()
    elif continues == 'N' or continues == 'n':
        sys.exit()
    else:
        print('你输入了个啥？')
        time.sleep(3)
        finish()
        
def install():
    os.system('cls')
    print('从服务器下载文件……\n')

    try:
        download('https://maoyihao.site:5244/d/%E8%B5%84%E6%BA%90/clash/clash.exe', os.path.join(user_path, "clash.exe"))
    except PermissionError:
        notification('没有文件读写权限，也许是软件未以管理员身份运行或服务已在运行', 8)
        sys.exit()

    os.system('cls')
    print('下载完成，开始安装\n')
    os.system(os.path.join(user_path, "clash.exe") + ' --startup auto install')
    time.sleep(1)
    finish()

def uninstall():
    os.system('cls')
    print('开始卸载\n')

    try:
        os.system(os.path.join(user_path, "clash.exe") + ' stop')
        os.system(os.path.join(user_path, "clash.exe") + ' remove')
        os.remove(os.path.join(user_path, "clash.exe"))
        notification('卸载完成', 3)
        sys.exit()
    except FileNotFoundError:
        notification('啥也没有，卸载了个寂寞', 5)
        sys.exit()

def pstart():
    os.system('cls')
    start = input('请选择安装(1)或卸载(2)：')
    if start=='1':
        install()
    elif start=='2':
        uninstall()
    else:
        print('你输入了个啥？')
        time.sleep(3)
        pstart()

pstart()