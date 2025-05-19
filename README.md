# 电费余额自动查询

本项目可实现**武汉理工大学马房山校区**定时查询电费余额，并发送余额不足预警通知，防止关键时候突然断电造成严重后果，适合宿舍使用**台式电脑**的同学

## 使用方法

使用前需更改`user_settings_example.yaml`为`user_settings.yaml`，并配置其中的参数：

USER_NAME: 智慧理工大账号 

PASSWORD: 智慧理工大密码 

FROM_EMAIL: 邮件发送方邮件地址

EMAIL_PASSWORD: 邮件发送方授权码

SMTP_SERVER: SMTP服务器地址

SMTP_PORT: SMTP服务器端口

TO_EMAIL: 邮件接受方邮件地址

EMAIL: 是否发送邮件

SYSTEM: 是否发送系统通知

THRESHOLD: 余额阈值

INTERVAL: 查询间隔（分钟）

## 邮件发送

需要两个邮箱，其中一个用来发送邮件（可使用qq小号）

发送方邮件需知道`SMTP服务器地址`，`SMTP服务器端口`，`邮件发送方授权码`，在`user_settings.yaml`中填写

## 运行方式

首先需要安装依赖：

```bash
pip install -r requirements.txt
```

### 静默运行

如需后台静默运行，填写好配置文件后，可直接双击运行`run.bat`，此时不会出现任何窗口；若需要停止，可双`击stop.bat`

注：第一次运行会弹出终端，填写宿舍信息，保存为`config.json`，后面每次运行都会保持静默。

### 终端运行

运行：`python main.py`

## 工作流程

启动时会查询一次电费余额，并发送通知

后台运行时每隔`INTERVAL`查询一次，若余额不低于阈值，则不会发送通知