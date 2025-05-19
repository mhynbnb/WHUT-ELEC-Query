from email.mime.text import MIMEText
import yaml
import smtplib

def send_email(content,is_html=False):
    """
    发送邮件函数
    Args:
        content: 要发送的邮件内容
    Returns:
        bool: 发送成功返回True，失败返回False
    """
    try:
        # 读取配置文件
        with open('user_settings.yaml', 'r', encoding='utf-8') as file:
            settings = yaml.safe_load(file)

        # 获取配置信息
        from_addr = settings['FROM_EMAIL']
        password = settings['EMAIL_PASSWORD']  
        to_addr = settings['TO_EMAIL']
        smtp_server = settings['SMTP_SERVER']  
        smtp_port = settings['SMTP_PORT']  

        # 创建邮件对象
        content_type = 'html' if is_html else 'plain'
        msg = MIMEText(content, content_type, 'utf-8')
        # msg = MIMEText(content, 'html', 'utf-8')
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = '电费查询结果'

        # 连接服务器并发送邮件
        server = smtplib.SMTP(smtp_server, smtp_port) 
        server.starttls()  # 使用TLS加密连接
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"发送邮件时出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 测试代码
    test_content = """
    <html>
        <body>
            <p style="color: black; font-weight: bold; font-size: 25px;">
            <span>马区西院</span>
            <span style="color: green;">余额充足</span>
            </p>
            <br><br>
            <ul style=" font-size: 20px">
                <li>剩余用量：12度</li>
                <li>表码示数：15度</li>
                <li>剩余金额：72.56元</li>
            </ul>
        </body>
    </html>
    """
    if send_email(test_content ,is_html=True):
        print("邮件发送成功")
    else:
        print("邮件发送失败")
