import json
from datetime import date, datetime, timedelta
from lunardate import LunarDate
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests

# 直接在代码中设置变量
start_date = "2024-03-16"  # 在一起的日期，格式为 YYYY-MM-DD
appKey = "3916230e1ae941b2850105605426ba03"
birthday = "01-11"  # 生日，格式为 MM-DD
app_id = "wx9f6877be1a669d38"
app_secret = "4a818ff79930d450960d648a328a37ca"
user_ids = ["ol4Xp6_3ZaiHwk3lOTr6ehfPEBRk"]  # 多个用户用列表存储
template_id_day = "白天模板的 template_id"
template_id_night = "晚上模板的 template_id"
name = "ye"
city = "南充"

# 当前时间
today = datetime.now()
today_date = today.strftime("%Y年%m月%d日")

# 构建请求体
headers = {"Content-Type": "application/x-www-form-urlencoded"}
params = {"key": appKey, "location": city}

# 获取天气数据
def get_weather_data(url, params, headers):
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("code") != "200":
            raise ValueError(f"API 请求失败: {data.get('message')}")
        return data
    except requests.exceptions.RequestException as e:
        raise ValueError(f"网络请求失败: {e}")

# 获取城市 ID
city_data = get_weather_data("https://geoapi.qweather.com/v2/city/lookup", params, headers)
city_id = city_data["location"][0]["id"]
params["location"] = city_id

# 获取实时天气
realtime_data = get_weather_data("https://devapi.qweather.com/v7/weather/now", params, headers)
realtime = realtime_data["now"]
now_temperature = realtime["temp"] + "℃" + realtime["text"]

# 获取 3 天天气预报
forecast_data = get_weather_data("https://devapi.qweather.com/v7/weather/3d", params, headers)
day_forecast_today = forecast_data["daily"][0]
day_forecast_tomorrow = forecast_data["daily"][1]

# 距离春节还有多少天
def days_until_spring_festival(year=None):
    if year is None:
        year = datetime.now().year
    spring_festival_lunar = LunarDate(year, 1, 1)
    spring_festival_solar = spring_festival_lunar.toSolarDate()
    today = datetime.now().date()
    days_until = (spring_festival_solar - today).days
    if days_until <= 0:
        days_until = days_until_spring_festival(year + 1)
    return days_until

# 在一起多天计算
def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days + 1

# 生日计算
def get_birthday():
    next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next < datetime.now():
        next = next.replace(year=next.year + 1)
    return (next - today).days

# 彩虹屁接口
def get_words():
    try:
        response = requests.get("https://api.shadiao.pro/chp")
        response.raise_for_status()
        text = response.json()['data']['text']
        chunk_size = 20
        split_notes = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        return (split_notes + [""] * 5)[:5]
    except requests.exceptions.RequestException as e:
        print(f"获取彩虹屁失败: {e}")
        return ["", "", "", "", ""]

if __name__ == '__main__':
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)
    note1, note2, note3, note4, note5 = get_words()

    now_utc = datetime.utcnow()
    beijing_time = now_utc + timedelta(hours=8)
    hour_of_day = beijing_time.hour
    strDay = "today"
    if hour_of_day > 15:
        strDay = "tomorrow"
        template_id_day = template_id_night

    print("当前时间：" + str(beijing_time) + "即将推送：" + strDay + "信息")

    data = {
        "name": {"value": name},
        "today": {"value": today_date},
        "city": {"value": city},
        "weather": {"value": globals()[f'day_forecast_{strDay}_weather']},
        "now_temperature": {"value": now_temperature},
        "min_temperature": {"value": globals()[f'day_forecast_{strDay}_temperature_min']},
        "max_temperature": {"value": globals()[f'day_forecast_{strDay}_temperature_max']},
        "love_date": {"value": get_count()},
        "birthday": {"value": get_birthday()},
        "diff_date1": {"value": days_until_spring_festival()},
        "sunrise": {"value": globals()[f'day_forecast_{strDay}_sunrise']},
        "sunset": {"value": globals()[f'day_forecast_{strDay}_sunset']},
        "textNight": {"value": globals()[f'day_forecast_{strDay}_night']},
        "windDirDay": {"value": globals()[f'day_forecast_{strDay}_windDirDay']},
        "windDirNight": {"value": globals()[f'day_forecast_{strDay}_windDirNight']},
        "windScaleDay": {"value": globals()[f'day_forecast_{strDay}_windScaleDay']},
        "note1": {"value": note1},
        "note2": {"value": note2},
        "note3": {"value": note3},
        "note4": {"value": note4},
        "note5": {"value": note5}
    }

    for user_id in user_ids:
        try:
            res = wm.send_template(user_id, template_id_day, data)
            print(f"发送消息给 {user_id} 成功: {res}")
        except Exception as e:
            print(f"发送消息给 {user_id} 失败: {e}")
