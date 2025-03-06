from airflow import DAG
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pendulum
import json

# 设置为北京时间
local_tz = pendulum.timezone("Asia/Shanghai")

def get_weather_advice(weather_data):
    """获取天气建议"""
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-mtmzmksnwicnyptngiuiuxnfjgskdjzdeyfwnvlfydhbqxxt",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    根据以下武威天气数据，给出温馨的生活建议：
    - 白天天气：{weather_data['dayweather']}
    - 白天温度：{weather_data['daytemp']}℃
    - 白天风力：{weather_data['daypower']}
    - 夜间天气：{weather_data['nightweather']}
    - 夜间温度：{weather_data['nighttemp']}℃
    - 夜间风力：{weather_data['nightpower']}
    
    请从穿衣、出行、活动等方面给出贴心的建议，使用简短温暖的语气，并加入适当的emoji。
    """
    
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "response_format": {"type": "text"}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        advice = result['choices'][0]['message']['content']
    except Exception as e:
        advice = f"获取天气建议时发生错误: {str(e)}"
    
    return advice

def get_weather():
    """获取武威天气信息"""
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": "2d9086103ad488770bcab31c9344e2cd",
        "city": "620600",
        "extensions": "all"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "1":  # API调用成功
            forecasts = data["forecasts"][0]
            today_weather = forecasts['casts'][0]
            
            # 获取天气建议
            weather_advice = get_weather_advice(today_weather)
            
            weather_info = f"""
            <div class="weather-section">
                <h2>🌤️ 今日武威天气</h2>
                <div class="weather-details">
                    <p>📅 日期：{today_weather['date']}</p>
                    <p>🌞 白天天气：{today_weather['dayweather']}</p>
                    <p>🌡️ 白天温度：{today_weather['daytemp']}℃</p>
                    <p>🌬️ 白天风力：{today_weather['daypower']}</p>
                    <p>🌙 夜间天气：{today_weather['nightweather']}</p>
                    <p>🌡️ 夜间温度：{today_weather['nighttemp']}℃</p>
                    <p>🌬️ 夜间风力：{today_weather['nightpower']}</p>
                </div>
                <div class="weather-advice">
                    <h3>💝 贴心小建议</h3>
                    <p>{weather_advice}</p>
                </div>
            </div>
            """
        else:
            weather_info = "<p>抱歉，获取天气信息失败</p>"
            
    except Exception as e:
        weather_info = f"<p>获取天气信息时发生错误: {str(e)}</p>"
    
    return weather_info

def get_horoscope():
    """获取天秤座运势"""
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-", ##apikey——大语言模型，推荐硅基流动
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {
                "role": "user",
                "content": "请用简短优美的语言，为天秤座写一段今日运势，包括爱情、事业、财运等方面。分条列点，并适当加入emoji"
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "response_format": {"type": "text"}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        horoscope = result['choices'][0]['message']['content']
        # 将markdown格式的文本转换为HTML格式
        horoscope = horoscope.replace('\n', '<br>')  # 处理换行
        horoscope = horoscope.replace('**', '')      # 移除加粗标记
    except Exception as e:
        horoscope = f"获取星座运势时发生错误: {str(e)}"
    
    return horoscope

def get_combined_info():
    """获取天气和星座运势信息"""
    weather_info = get_weather()
    horoscope = get_horoscope()
    
    combined_info = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #333;">💌 亲爱的宝贝，这是你的专属日报 💌</h1>
        </div>
        
        <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            {weather_info}
        </div>
        
        <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px;">
            <h2 style="color: #666;">🌟 天秤座今日运势 🌟</h2>
            <div style="line-height: 1.6; color: #444;">{horoscope}</div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #888;">
            <p>愿你今天开心快乐！😊</p>
            <p>——来自你的专属小助手</p>
        </div>
    </div>
    """
    
    return combined_info

# DAG配置
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['liuzifeng_r@163.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'weather_horoscope_dag',
    default_args=default_args,
    description='天气预报和星座运势邮件',
    schedule_interval='0 10 * * *',  # 每天北京时间10点
    start_date=datetime(2024, 3, 5, tzinfo=local_tz),
    catchup=False,
) as dag:

    get_info_task = PythonOperator(
        task_id='get_combined_info',
        python_callable=get_combined_info,
    )

    send_email_task = EmailOperator(
        task_id='send_email',
        to='', ## 目标邮箱
        subject='你的专属日报 🌟',
        html_content="{{ task_instance.xcom_pull(task_ids='get_combined_info') }}",
    )

    get_info_task >> send_email_task 