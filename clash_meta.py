import win32serviceutil
import win32service
import win32event
import os
import time
import requests
import win32ts
import win32security
import win32timezone
import sys
import winerror
import servicemanager
from win32comext.shell import shell, shellcon
class clash(win32serviceutil.ServiceFramework):
    _svc_name_ = "clash_meta"
    _svc_display_name_ = "Clash Meta"
    _svc_description_ = "A clash service based on meta core"

    def GetProfile(self):

        def download(url, filename=None):
            down_res = requests.get(url)
            with open(filename, 'wb') as file:
                file.write(down_res.content)

        core = os.path.join(self.user_path, ".config", "clash.meta-windows-amd64.exe")
        config = os.path.join(self.user_path, ".config", "clash_meta")
        download('', core)
        download('', os.path.join(config, "Country.mmdb"))
        download('', os.path.join(config, "GeoIP.dat"))
        download('', os.path.join(config, "GeoSite.dat"))
        download('', os.path.join(config, "config.yaml"))

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
            os.system('shutdown -s -t 60 -c "个人配置文件缺失！"')
            time.sleep(5)
            os.system('shutdown -a')
            self.ReportServiceStatus(win32service.SERVICE_ERROR_NORMAL)
            return 0

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        config = os.path.join(self.user_path, ".config")
        start = os.path.join(config, "clash.meta-windows-amd64.exe") + ' -d ' + os.path.join(config, "clash_meta")
        os.system(start)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        os.system("taskkill /im clash.meta-windows-amd64.exe /f")
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

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