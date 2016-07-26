#!/usr/bin/env python
# coding=utf-8

"""
# Note:
#   - Assuming no "Announcement"
#   - Assuming input parameters are correct
#   - You may need to install "pyte" or other libs
"""

import argparse
import getpass
import pyte
import telnetlib

# fix python 2/3 compatibility
try:
    input = raw_input
except NameError:
    pass


def big5(str):
    try:  # python 3 behavior (default = unicode string)
        return str.encode('big5', errors='ignore')
    except UnicodeDecodeError:  # python 2 behavior
        return str.decode('utf8', errors='ignore').encode('big5', errors='ignore')


if __name__ == '__main__':
    cmdline = argparse.ArgumentParser(description='Hulabear BBS crawler for ONE board')
    cmdline.add_argument('-u', '--username', default='guest')
    cmdline.add_argument('-p', '--password', default='')
    cmdline.add_argument('-b', '--board', default='anonymous')
    args = cmdline.parse_args()

    BBS_HOST = 'hulabear.twbbs.org'

    if args.username == 'guest':
        args.username = input('[INPUT] 請輸入代號（預設%s）：' % args.username) or args.username

    if args.username != 'guest' and args.password == '':
        args.password = getpass.getpass('[INPUT] 請輸入密碼：')

    if args.board == '':
        args.board = input('[INPUT] 請輸入看板名稱：')

    if args.board == '':
        raise ValueError('看板名稱為空')

    # set up a terminal emulator
    screen = pyte.Screen(80, 24)
    stream = pyte.Stream()
    screen.mode.discard(pyte.modes.LNM)  # prevent '\r' -> '\r\n'
    stream.attach(screen)

    print('[DOING] connect to telnet://' + BBS_HOST)
    tn = telnetlib.Telnet(BBS_HOST)
    # tn.set_debuglevel(10)

    print('[DOING] login username: ' + args.username)
    print(tn.read_until(big5('請輸入代號：')).decode(errors='ignore'))

    if args.username == 'guest':
        tn.write(big5(args.username + '\r'))
    else:
        tn.write(big5(args.username + '\r'))
        print(tn.read_until(big5('請輸入密碼：')).decode(errors='ignore'))
        tn.write(big5(args.password + '\r'))

    print('[DOING] entering main menu')
    tn.write(big5('\r' * 3))  # skip to main menu
    print(tn.read_until(big5('【 再別熊窩 】')).decode(errors='ignore'))

    print('[DOING] entering board: ' + args.board)
    tn.write(big5('\rs'))  # enter (B)oards && 's' to directly goto board
    tn.read_until(big5('請輸入看板名稱(按空白鍵自動搜尋)：'))
    tn.write(big5(args.board + '\r'))
    # time.sleep(1)

    print('[DOING] dump all text display in this board')
    print(tn.read_very_eager().decode('uao_decode', errors='ignore'))
    # with codecs.open('test.txt', 'w', encoding='utf8') as fout:
    #     fout.write(content)

    print('[DOING] close connection')
    tn.close()
