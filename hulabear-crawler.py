#!/usr/bin/env python
# coding=utf-8

"""
# Note:
#   - Assuming no "Announcement"
#   - Assuming input parameters are correct
#   - You may need to install "pyte" or other libs
"""

import argparse
import telnetlib, pyte, getpass
import time
import uao_decode, codecs

# python 2/3 compatibility
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

    if args.board == 'anonymous':
        args.board = input('[INPUT] 請輸入看板名稱（預設%s）：' % args.board) or args.board

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

    print('[DOING] check duplicate connection')
    matchIdx, matchObj, text = tn.expect(['login'], timeout=1)  # secs
    print(text.decode(errors='ignore'))
    if matchIdx != -1:
        tn.write(big5('\r'))

    print('[DOING] enter main menu')
    tn.write(big5('\r\r\r'))  # skip to main menu
    print(tn.read_until(big5('【 再別熊窩 】')).decode(errors='ignore'))

    print('[DOING] enter board: ' + args.board)
    tn.write(big5('\r' + 's'))  # enter (B)oards && 's' to directly goto board
    tn.read_until(big5('請輸入看板名稱(按空白鍵自動搜尋)：'))
    tn.read_very_eager()  # used to clear buffer
    tn.write(big5(args.board + '\r'))

    # skip enter board screen
    print('[DOING] dump the 1st page of a post')
    matchIdx, matchObj, text = tn.expect([big5('▏▎▍▌▋▊▉\s\x1B\[1;37m請按任意鍵繼續\s\x1B\[1;33m▉\x1B\[m')], timeout=1)
    if (matchIdx != -1):
        tn.write('\r')
        time.sleep(1)
        content = tn.read_very_eager().decode('uao_decode', 'ignore')
    else:
        content = text.decode('uao_decode', 'ignore')

    for i in range(1, 3):
        tn.write(str(i) + '\r\n' * 2)
        # tn.read_very_eager() # used to clear buffer
        # tn.write('\r\n')
        time.sleep(1)
        content = tn.read_very_eager().decode('uao_decode', 'ignore')
        pos = content.find('\x1B[;H\x1B[2J\x1B[47;34m')
        if (pos != -1): content = content[pos:]
        with codecs.open(str(i) + '.txt', 'w', encoding='utf8') as fout:
            fout.write(content)
        tn.write('q')

    tn.close()


    print('[DOING] close connection')
    tn.close()
