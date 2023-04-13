import random
import time
from multiprocessing import Process

from src import common
from src.config import config
from src.util import adbCmd


ORI_SCREEN_WIDTH = 2700
ORI_SCREEN_HEIGHT = 1224


class MobileController(Process):
    def __init__(self, serial, package, activity, channel):
        super(MobileController, self).__init__()
        self.serial = serial
        self.package = package
        self.activity = activity
        self.proportion_width = 1.0
        self.proportion_height = 1.0
        self.can_process = True
        self.channel = channel
        self.init()
        self.prepare()

    def accept_one_friend(self):

        useless_pages = [
            {
                "operate_type": "click",   # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",   # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/首页关闭.jpg"),   # 从截屏匹配的图像
                "once": True   # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",   # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",   # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("friends/好友入口.jpg"),   # 从截屏匹配的图像
                "once": True   # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("friends/游戏好友.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ]
        target_pages = [
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("friends/申请列表.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ]
        # 进入到好友申请列表窗口页
        result = common.execute(self.serial, useless_pages, target_pages, retry_times=3)
        if not result:
            return False

        target_pages = [
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("friends/通过申请.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ]
        # 在好友申请列表页通过一个申请
        accepted = common.execute(self.serial, [], target_pages, retry_times=2)

        useless_pages = [
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("friends/窗口关闭.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ]
        target_pages = [
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("friends/返回.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ]
        # 依次点击按钮，返回首页
        result = common.execute(self.serial, useless_pages, target_pages, retry_times=3)
        return accepted

    def send_messages(self):
        texts = config["friend_chat"]
        return common.send_messages(self.serial, 3, texts)

    def check(self):
        self.can_process = False
        count = 0
        while count < 2:
            # 进入好友申请列表, 通过一个好友申请, 并返回主界面
            accepted = self.accept_one_friend()
            if accepted:
                # 在好友聊天频道发送消息
                self.send_messages()
            else:
                time.sleep(random.randint(10, 20))
                count += 1

        self.can_process = True

    def init(self):
        h, w = adbCmd.get_wm_size(self.serial)
        if h == 0 or w == 0:
            return False
        self.proportion_width = float(w) / float(ORI_SCREEN_WIDTH)
        self.proportion_height = float(h) / float(ORI_SCREEN_HEIGHT)

    def step_into_main_page(self):
        useless_pages = [
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/同意协议.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/选择qq授权.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/授权同意.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/家长模式.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/信息授权.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/开始游戏.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/首页关闭.jpg"),  # 从截屏匹配的图像
                "once": False  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/活动关闭.jpg"),  # 从截屏匹配的图像
                "once": False  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ]
        target_pages = [
            {
                "operate_type": "check",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": common.build_target_image("login/首页标识.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ]
        return common.execute(self.serial, useless_pages, target_pages)

    def prepare(self):
        # 先创建临时目录
        common.mkdir("../temp/" + self.serial)

        # 先启用输入法插件
        apks = config["apks"]
        for apk in apks:
            apk_file = apk["apk"]
            package = apk["package"]
            activity = apk["activity"]
            result, error = common.install_and_enable_apk(apk_file, package, activity, activity, self.serial)
            if not result:
                print(error)

        # 根据手机屏幕尺寸自适应
        common.set_resize_proportion(self.serial, ORI_SCREEN_WIDTH, ORI_SCREEN_HEIGHT)

        # 启动app
        result, error = adbCmd.start_app(self.package, self.activity, self.serial)
        if not result:
            print(error)
            return False

        # 进入首页，包括登录/去除活动等窗口
        return self.step_into_main_page()

    def run(self) -> None:
        while True:
            # 随机时间执行随机操作
            messages = config["world_chat"]
            message = messages[random.randint(0, len(messages) - 1)]
            common.send_messages(self.serial, self.channel, [message])

            time.sleep(random.randint(5, 20))
            self.check()

            time.sleep(random.randint(180, 240))


