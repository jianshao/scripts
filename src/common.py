import os
import time
import aircv as ac
from PIL import Image

from src.util import adbCmd

screen_proportion = {}


def build_screen_filename(serial):
    return "../temp/" + serial + "/curr_screen.jpg"


def build_target_image(filename):
    return "../images/wangzherongyao/" + filename


def resize_image(serial, image):
    img = Image.open(image)

    # 将按钮图片适应手机尺寸
    w, h = img.size
    proportion_w = screen_proportion[serial]["w"]
    proportion_h = screen_proportion[serial]['h']
    new_img = img.resize((int(w * proportion_w), int(h * proportion_h)))

    # 保存成临时文件
    new_img = new_img.convert("RGB")
    filename = "../temp/" + serial + "/target.jpg"
    new_img.save(filename)
    new_img.close()
    img.close()
    return filename


def install_and_enable_apk(apk, package, activity, setting, serial):
    result, error = adbCmd.install_apk(serial, apk, package)
    if not result:
        return result, error

    if activity:
        result, error = adbCmd.enable_apk(serial, package + "/" + activity)
        if not result:
            return result, error

    if setting:
        result, error = adbCmd.setting_apk(serial, package + "/" + setting)
        if not result:
            return result, error

    return True, ''


def set_resize_proportion(serial, ori_w, ori_h):
    h, w = adbCmd.get_wm_size(serial)
    if h == 0 or w == 0:
        return False

    screen_proportion[serial] = {
        "h": float(h) / float(ori_h),
        "w": float(w) / float(ori_w)
    }
    return True


def resize(serial, x1, x2, y1, y2):
    proportion_w = screen_proportion[serial]["w"]
    proportion_h = screen_proportion[serial]["h"]
    x1 = int(x1 * proportion_w)
    x2 = int(x2 * proportion_w)
    y1 = int(y1 * proportion_h)
    y2 = int(y2 * proportion_h)
    return x1, x2, y1, y2


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def search_image(serial, target):
    new_target = resize_image(serial, target)
    imgtarget = ac.imread(new_target)

    filename = build_screen_filename(serial)
    # adbCmd.screenshot(serial, filename)
    imgsrc = ac.imread(filename)
    pos = ac.find_template(imgsrc, imgtarget, rgb=True, bgremove=False)
    x1, x2, y1, y2 = 0, 0, 0, 0
    if pos and pos.get("confidence", 0) > 0.85:
        rectangle = pos["rectangle"]
        x1, x2, y1, y2 = rectangle[0][0], rectangle[2][0], rectangle[0][1], rectangle[1][1]
    return x1, x2, y1, y2


def execute_one_step(serial, operate_info):

    result = False
    # 具体操作的前置步骤，如检查等
    before = operate_info.get("before", None)
    if before:
        result = before()
        if not result:
            return False

    operate_type = operate_info.get("operate_type", '')
    if operate_type == "text":
        text = operate_info.get("text", '')
        result = adbCmd.input_text(serial, text)
    elif operate_type in ["click", "check"]:
        # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
        position_src = operate_info.get("position_src", '')
        if position_src == "match":
            target_image = operate_info.get("target_image", '')
            x1, x2, y1, y2 = search_image(serial, target_image)
        else:
            locations = operate_info.get("locations", [0, 0, 0, 0])
            x1, x2, y1, y2 = resize(serial, locations[0], locations[1], locations[2], locations[3])

        # 坐标不正确说明匹配失败，或配置坐标值错误
        if x1 == 0 or x2 == 0 or y1 == 0 or y2 == 0:
            result = False
        else:
            if operate_type == "click":
                result = adbCmd.click_button(serial, x1, x2, y1, y2)
            else:
                result = True

    if not result:
        return False

    after = operate_info.get("after", None)
    if after:
        result = after()

    return result


def execute(serial, useless_pages, target_pages, retry_times=30):
    filename = build_screen_filename(serial)
    for i in range(1, retry_times):

        adbCmd.screenshot(serial, filename)
        index = 0
        # 如果有中间页面，先点击去除，如首页活动弹窗页面
        while index < len(useless_pages):
            result = execute_one_step(serial, useless_pages[index])
            if result:
                adbCmd.screenshot(serial, filename)
                if useless_pages[index].get("once"):
                    list.remove(useless_pages, useless_pages[index])
                index = 0
            else:
                index += 1

        # 如果出现目标页面，说明等待完成
        for target in target_pages:
            if execute_one_step(serial, target):
                return True

        # 当前页面既不是中间页，也不是目标页，可能是中间的载入画面，等待2s再次处理
        time.sleep(2)
    return False


def build_one_text_operators(text):
    return [
        # 点击输入框
        {
            "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
            # "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            # "target_image": build_target_image("message/输入框.jpg"),  # 从截屏匹配的图像
            "position_src": "value",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            "locations": [275, 686, 1111, 1165],
            "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        },
        # 输入消息
        {
            "operate_type": "text",  # 操作类型，click-点击，check-检查，text-文本输入
            "text": text,
            "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        },
        # adbkeyboard崩溃窗口
        {
            "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
            "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            "target_image": build_target_image("message/键盘崩溃取消上报.jpg"),  # 从截屏匹配的图像
            # "position_src": "value",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            # "locations": [275, 686, 1111, 1165],
            "once": False  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        },
        # 点击确定
        {
            "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
            # "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            # "target_image": build_target_image("message/消息确定.jpg"),  # 从截屏匹配的图像
            "position_src": "value",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            "locations": [1200, 1400, 577, 800],
            "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        },
        # 点击发送
        {
            "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
            # "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            # "target_image": build_target_image("message/消息发送.jpg"),  # 从截屏匹配的图像
            "position_src": "value",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            "locations": [1294, 1486, 1107, 1171],
            "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        }
    ]


def send_messages(serial, channel, texts):
    open_chat = [
        # 关闭游戏邀请窗
        {
            "operate_type": "click",   # 操作类型，click-点击，check-检查，text-文本输入
            "position_src": "match",   # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            "target_image": build_target_image("friends/游戏邀请关闭.jpg"),   # 从截屏匹配的图像
            "once": False   # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        },
        # 关闭聊天提示窗
        {
            "operate_type": "click",   # 操作类型，click-点击，check-检查，text-文本输入
            "position_src": "match",   # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            "target_image": build_target_image("message/聊天提示关闭.jpg"),   # 从截屏匹配的图像
            "once": False   # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        },
        # 从首页点开聊天窗
        {
            "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
            "position_src": "value",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            "locations": [370, 726, 1036, 1074],
            "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        }
    ]

    channels = {
        "world": [
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": build_target_image("message/综合频道.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ],
        "city": [
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": build_target_image("message/输入框.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ],
        "friends": [
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "target_image": build_target_image("message/好友频道.jpg"),  # 从截屏匹配的图像
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            },
            {
                "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
                "position_src": "value",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
                "locations": [153, 480, 288, 384],
                "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
            }
        ]
    }

    close_chat = [
        {
            "operate_type": "click",  # 操作类型，click-点击，check-检查，text-文本输入
            "position_src": "match",  # 坐标来源，match-从截屏中匹配，value-直接提供坐标点
            "target_image": build_target_image("message/聊天窗关闭.jpg"),  # 从截屏匹配的图像
            "once": True  # 只匹配一次，部分图像可以匹配多次，如首页活动页面不确定有多少个
        }
    ]

    # 打开聊天窗
    useless_pages = open_chat

    # 选择频道
    if channel == 1:
        # 综合频道
        useless_pages.extend(channels["world"])
    elif channel == 3:
        # 好友频道
        useless_pages.extend(channels["friends"])
    else:
        # 同城频道
        useless_pages.extend(channels["city"])

    # 根据消息组装发送动作
    for text in texts:
        useless_pages.extend(build_one_text_operators(text))

    # 以关闭聊天窗作为收尾
    return execute(serial, useless_pages, close_chat, retry_times=2)
