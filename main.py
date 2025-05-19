from re import A
import requests
import os
import json
from get_cookie import get_jsessionid
from send_email import send_email
import yaml
import time

def get_reserve(first_time=False):
    if not os.path.exists('config.json'):
        
        print('选择校区：\n0001（马区东院）\n0002（马区西院）\n0003（南湖南院）\n0004（南湖北院）')
        area_dict={
            '0001':'马区东院',
            '0002':'马区西院',
            '0003':'南湖南院',
            '0004':'南湖北院'
        }
        areaid=input('请输入校区编号：')
        build_url='http://cwsf.whut.edu.cn/queryBuildList'
        build_data={
            'areaid':areaid,
            'factorycode':'E035'
        }
        build_rsp=requests.post(build_url,data=build_data,headers=headers)
        try:
            build_json=build_rsp.json()
        except:
            print('cookie失效，正在重新获取')
            jsessionid=get_jsessionid()
            headers['cookie']=f'JSESSIONID={jsessionid}'
            print('cookie获取成功')
            build_rsp=requests.post(build_url,data=build_data,headers=headers)
            build_json=build_rsp.json()
        os.system('cls')

        print('选择楼号：')
        build_dict={_.split('@')[0]:_.split('@')[1] for _ in build_json['buildList']}
        print('\n'.join([_.replace('@','（')+'）' for _ in build_json['buildList']]))
        buildid=input('请输入楼号：')
        floor_url='http://cwsf.whut.edu.cn/queryFloorList'
        floor_data={
            'areaid':areaid,
            'buildid':buildid,
            'factorycode':'E035'
        }
        floor_rsp=requests.post(floor_url,data=floor_data,headers=headers)
        floor_json=floor_rsp.json()
        os.system('cls')


        print('选择楼层：')
        print('\n'.join([str(_) for _ in floor_json['floorList']]))
        floorid=input('请输入楼层：')
        room_url='http://cwsf.whut.edu.cn/getRoomInfo'
        room_data={
            'buildid':buildid,
            'floorid':floorid,
            'factorycode':'E035'
        }
        room_rsp=requests.post(room_url,data=room_data,headers=headers)
        room_json=room_rsp.json()
        os.system('cls')

        print('选择房间号：')
        room_dict={_.split('-')[-1]:_.split('@')[0] for _ in room_json['roomList']}
        room_num=input('请输入房间号：')
        roomid=room_dict[room_num]
        room_info_url='http://cwsf.whut.edu.cn/queryRoomElec'
        room_info_data={
            'roomid':roomid,
            'factorycode':'E035'
        }
        room_info_rsp=requests.post(room_info_url,data=room_info_data,headers=headers)
        room_info_json=room_info_rsp.json()
        os.system('cls')

        metaid=room_info_json['meterId']
        reserve_url='http://cwsf.whut.edu.cn/queryReserve'
        reserve_data={
            'meterId':metaid,
        'factorycode':'E035'
        }
        reserve_rsp=requests.post(reserve_url,data=reserve_data,headers=headers)
        reserve_json=reserve_rsp.json()
        config={
            'areaid':areaid,
            'buildid':buildid,
            'roomid':roomid,
            'roomnum':room_num,
            'metaid':metaid,
            'floorid':floorid,
            'area_dict':area_dict,
            'build_dict':build_dict,
            'room_dict':room_dict
        }
        
        with open('config.json','w',encoding='utf-8') as f:
            json.dump(config,f,ensure_ascii=False)
    else:
        print('检测到配置文件，自动加载')
        with open('config.json','r',encoding='utf-8') as f:
            config=json.load(f)
            metaid=config['metaid']
            area_dict=config['area_dict']
            build_dict=config['build_dict']
            room_dict=config['room_dict']
            areaid=config['areaid']
            buildid=config['buildid']
            roomid=config['roomid']
            floorid=config['floorid']
            room_num=config['roomnum']
        reserve_url='http://cwsf.whut.edu.cn/queryReserve'
        reserve_data={
            'meterId':metaid,
            'factorycode':'E035'
        }
        reserve_rsp=requests.post(reserve_url,data=reserve_data,headers=headers)
        # print(reserve_rsp.status_code)
        try:
            reserve_json=reserve_rsp.json()
        except:
            print('cookie失效，正在重新获取')
            jsessionid=get_jsessionid()
            headers['cookie']=f'JSESSIONID={jsessionid}'
            reserve_json=reserve_rsp.json()

    print(area_dict[areaid],build_dict[buildid],room_num)
    print('剩余用量：'+reserve_json['remainPower']+'度')
    print('表码示数：'+reserve_json['ZVlaue']+'度')
    print('剩余金额：'+reserve_json['meterOverdue']+'元')
    

    if settings['EMAIL'] and (first_time or float(reserve_json['meterOverdue'])<settings['THRESHOLD']):
        if float(reserve_json['meterOverdue'])<settings['THRESHOLD']:
            color='red'
        else:
            color='green'
        content=f"""
        <html>
            <body>
                <p style="color: black; font-weight: bold; font-size: 25px;">
                <span>{area_dict[areaid]}{build_dict[buildid]}{room_num}</span>
                <span style="color: {color};">余额为{reserve_json['meterOverdue']}元</span>
                </p>
                <br><br>
                <ul style=" font-size: 20px">
                    <li>剩余用量：{reserve_json['remainPower']}度</li>
                    <li>表码示数：{reserve_json['ZVlaue']}度</li>
                    <li>剩余金额：{reserve_json['meterOverdue']}元</li>
                </ul>
            </body>
        </html>
        """
        if send_email(content,is_html=True):
            print("邮件发送成功")
        else:   
            print("邮件发送失败")
    if settings['SYSTEM'] and (first_time or float(reserve_json['meterOverdue'])<settings['THRESHOLD']):
        from winotify import Notification, audio
        
        # 创建通知对象
        toast = Notification(
            app_id="电费查询",
            title="电费查询结果",
            msg=f"{area_dict[areaid]}{build_dict[buildid]}{room_num}\n"
                f"剩余用量：{reserve_json['remainPower']}度\n"
                f"表码示数：{reserve_json['ZVlaue']}度\n"
                f"剩余金额：{reserve_json['meterOverdue']}元",
            duration="short"  # 可选 "short" 或 "long"
        )
        # 设置通知声音（可选）
        toast.set_audio(audio.Default, loop=False)
        toast.show()
        if float(reserve_json['meterOverdue'])<settings['THRESHOLD']:
            toast = Notification(
            app_id="电费查询",
            title="警告",
            msg=f"余额不足{settings['THRESHOLD']}元，请充值",
            duration="short"  # 可选 "short" 或 "long"
            )
            toast.show()
if __name__ == "__main__":
    with open('user_settings.yaml', 'r', encoding='utf-8') as file:
        settings = yaml.safe_load(file)
    print('正在获取cookie')
    jsessionid=get_jsessionid()
    print('获取cookie成功')
    headers={
            'cookie':f'JSESSIONID={jsessionid}',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'
        }
    get_reserve(first_time=True)
    while True:
        time.sleep(settings['INTERVAL']*60)
        get_reserve(first_time=False)
