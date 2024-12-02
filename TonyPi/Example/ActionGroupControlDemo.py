import time
import threading
import hiwonder.ActionGroupControl as AGC

'''
    程序功能：动作组调用例程

    运行效果：先执行stand动作组立正，再执行2次go_forward动作组往前走，最后执行循环执行go_forward动作组往前走3秒后停止
    
    对应教程文档路径：  TonyPi智能视觉人形机器人\4.拓展课程学习\3.TonyPi上位机及动作编辑教学\第5课 通过命令行的形式调用动作组
'''


# 动作组需要保存在路径/home/pi/tony_pi/action_groups下
AGC.runActionGroup('stand')                                                        # 参数为动作组的名称，不包含后缀，以字符形式传入
AGC.runActionGroup('go_forward', times=2, with_stand=True)                         # 第二个参数为运行动作次数，默认1, 当为0时表示循环运行， 第三个参数表示最后是否以立正姿态收步

threading.Thread(target=AGC.runActionGroup, args=('go_forward', 0, True)).start()  # 运行动作函数是阻塞式的，如果要循环运行一段时间后停止，请用线程来开启
time.sleep(3)
AGC.stopActionGroup()                                                              # 前进3秒后停止
