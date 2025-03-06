import smtplib
from email.mime.text import MIMEText
from email.header import Header

def test_email_connection():
    # 邮箱配置
    smtp_server = "smtp.163.com" ##smtp服务器
    smtp_port = 465 ##smtp端口
    sender = "" ##发出邮箱
    password = "" ##pop3/smtp密钥
    receiver = "" ##目标邮箱

    # 创建邮件内容
    message = MIMEText('Test Email Content', 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = 'Test Email'

    try:
        # 创建SSL连接
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        # 显示调试信息
        server.set_debuglevel(1)
        # 登录
        server.login(sender, password)
        # 发送邮件
        server.sendmail(sender, [receiver], message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"发送失败: {str(e)}")
    finally:
        server.quit()

if __name__ == "__main__":
    test_email_connection()