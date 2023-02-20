import win32serviceutil
import win32service
import win32event
import os
import time
import requests
import win32ts
import win32security
import win32timezone
import threading
import sys
import winerror
import servicemanager
from win32comext.shell import shell, shellcon

def notification(text, sleep_time = 3):
    os.system('shutdown -s -t 60 -c "{}"'.format(text))
    time.sleep(sleep_time)
    os.system('shutdown -a')

class clash(win32serviceutil.ServiceFramework):

    _svc_name_ = "clash_meta"
    _svc_display_name_ = "Clash Meta"
    _svc_description_ = """A clash service based on meta core
                    Author: MaoYihao"""


    def GetProfile(self):

        meta_config = os.path.join(self.user_path, ".config", "clash_meta")

        #创建下载线程
        core = download('https://maoyihao.site:5244/d/%E8%B5%84%E6%BA%90/clash/clash.meta-windows-amd64.exe', os.path.join(self.user_path, ".config", "clash.meta-windows-amd64.exe"))
        Country = download('https://maoyihao.site:5244/d/%E8%B5%84%E6%BA%90/clash/Country.mmdb', os.path.join(meta_config, "Country.mmdb"))
        GeoIP = download('https://maoyihao.site:5244/d/%E8%B5%84%E6%BA%90/clash/GeoIP.dat', os.path.join(meta_config, "GeoIP.dat"))
        GeoSite = download('https://maoyihao.site:5244/d/%E8%B5%84%E6%BA%90/clash/GeoSite.dat', os.path.join(meta_config, "GeoSite.dat"))
        config = download('https://maoyihao.site:5244/d/%E8%B5%84%E6%BA%90/clash/config.yaml', os.path.join(meta_config, "config.yaml"))

        #尝试启动下载线程
        try:
            core.start()
            Country.start()
            GeoIP.start()
            GeoSite.start()
            config.start()
        except:
            notification("未知错误！", 5)
            sys.exit()

        #等待下载完成
        core.join()
        Country.join()
        GeoIP.join()
        GeoSite.join()
        config.join()

        #通知主函数下载完成
        win32event.SetEvent(self.start_event)

    def __init__(self, args):

        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.start_event = win32event.CreateEvent(None, 0, 0, None)

        #获取用户路径
        console_session_id = win32ts.WTSGetActiveConsoleSessionId() 
        console_user_token = win32ts.WTSQueryUserToken(console_session_id)
        win32security.ImpersonateLoggedOnUser(console_user_token)
        self.user_path = shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, console_user_token, 0)
        win32security.RevertToSelf()

        #检测clash文件夹是否存在，若不存在则创建
        if not os.path.exists(os.path.join(self.user_path, ".config")):
            os.chdir(self.user_path)
            os.mkdir(".config")
            os.chdir(os.path.join(self.user_path, ".config"))
            os.mkdir("clash_meta")
        elif not os.path.exists(os.path.join(self.user_path, ".config", "clash_meta")):
            os.chdir(os.path.join(self.user_path, ".config"))
            os.mkdir("clash_meta")

    def SvcDoRun(self):
        #准备启动服务
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        #从服务端获取配置文件
        self.GetProfile()

        #等待获取配置文件
        win32event.WaitForSingleObject(self.start_event, win32event.INFINITE)  

        #检测是否存在Provider
        try:
            test = open(os.path.join(self.user_path, ".config", "clash_meta", "maoyihao.yaml"))
            test.close
        except IOError:
            notification("个人配置文件缺失！", 5)
            self.ReportServiceStatus(win32service.SERVICE_ERROR_NORMAL)
            sys.exit()

        start = running(self.user_path)

        try:
            start.start()
        except:
            notification("主程序启动失败！", 5)
            sys.exit()

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        start.join()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        os.system("taskkill /im clash.meta-windows-amd64.exe /f")
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

class running(threading.Thread):

    def __init__(self, user_path):
        threading.Thread.__init__(self)
        self.user_path = user_path

    def start_clash(self):
        config = os.path.join(self.user_path, ".config")
        start = os.path.join(config, "clash.meta-windows-amd64.exe") + ' -d ' + os.path.join(config, "clash_meta")
        os.system(start)

    def run(self):
        self.start_clash()

class download(threading.Thread):

    def __init__(self, url, path):
        threading.Thread.__init__(self)
        self.url = url
        self.path = path

    def download(self):
        url = self.url
        filename = self.path
        down_res = requests.get(url)
        with open(filename, 'wb') as file:
            file.write(down_res.content)

    def run(self):
        self.download()

if __name__ == '__main__':

    if len(sys.argv) == 1:

        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(clash)
            servicemanager.Initialize('clash', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()

    else:
        win32serviceutil.HandleCommandLine(clash)