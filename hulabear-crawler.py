# coding=utf8

"""
# Assumptions:
#   - python2.7 only
#   - No "Announcement"
#   - All input parameters are correct
#   - The entered account can read ALL the article in the specified range
"""

import argparse
import telnetlib
import getpass
import time
import codecs
import sys
import os
import uao_decode

# python 2/3 compatibility (this is better)
try:
    input = raw_input
except NameError:
    pass

if float(sys.version[0:3]) > 2.7:
    raise RuntimeError('only supports python 2.7')


def big5(in_str):
    return in_str.decode('utf8', errors='ignore').encode('big5', errors='ignore')


def strip_status_bar(in_str):  # 刪除底下瀏覽狀態列
    s_1st = big5('\x1B[23;1H')

    i_1st = in_str.find(s_1st)
    if i_1st == -1:  # TODO: this sucks
        i_1st = in_str.find(big5('\x1B[24;1H'))

    i_md1 = in_str.find(big5('\x1B[0;34;46m 瀏覽'))
    i_md2 = in_str.find(big5('\x1B[K\n\x1B[0;34;46m 瀏覽'))
    i_md3 = in_str.find(big5('\x1B[K\r\x1B[0;34;46m 瀏覽'))
    i_md4 = in_str.find(big5('\x1B[K\r\n\x1B[0;34;46m 瀏覽'))
    i_md5 = in_str.find(big5('\x1B[K\n\r\x1B[0;34;46m 瀏覽'))
    i_end = in_str.find(big5('結束 \x1B[m'))

    if i_1st != -1 and  i_end != -1 and i_md1 != -1:
        if i_md5 > 0:
            return in_str[:i_1st].strip() + in_str[i_1st + len(s_1st):i_md5] + '\n'
        if i_md4 > 0:
            return in_str[:i_1st].strip() + in_str[i_1st + len(s_1st):i_md4] + '\n'
        if i_md3 > 0:
            return in_str[:i_1st] + in_str[i_1st + len(s_1st):i_md3]
        if i_md2 > 0:
            return in_str[:i_1st] + in_str[i_1st + len(s_1st):i_md2]
        if i_md1 > 0:
            return in_str[:i_1st].strip() + in_str[i_1st + len(s_1st):i_md1]
    else:
        return in_str

if __name__ == '__main__':
    cmdline = argparse.ArgumentParser(description='Hulabear BBS crawler for ONE board')
    cmdline.add_argument('-u', '--username', help='Required (ask if missing). Default="guest"')
    cmdline.add_argument('-p', '--password', help='Required if username is not "guest"')
    cmdline.add_argument('-b', '--board', help='Required. Default="anonymous"')
    cmdline.add_argument('-o', '--outdir', help='Output folder for crawled articles. Default="crawled"', default='crawled')
    cmdline.add_argument('-s', '--start', help='Article start counter. Default=1', type=int, default=1)
    cmdline.add_argument('-e', '--end', help='Article end counter. Default=3', type=int, default=3)
    args = cmdline.parse_args()

    cmdline.print_help()
    print('[START]')
    print('output folder := ' + args.outdir)
    print('article start counter := ' + str(args.start))
    print('article end counter := ' + str(args.end))

    BBS_HOST = 'hulabear.twbbs.org'

    if args.username is None:
        args.username = 'guest'
        args.username = input('[INPUT] username (default={}):'.format(args.username)) or args.username

    if args.username != 'guest' and args.password is None:
        args.password = getpass.getpass('[INPUT] password:')

    if args.board is None:
        args.board = 'anonymous'
        args.board = input('[INPUT] board (default={}):'.format(args.board)) or args.board

    if not args.board:
        raise ValueError('board is empty')

    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)

    print('[DOING] connect to telnet://' + BBS_HOST)
    tn = telnetlib.Telnet(BBS_HOST)
    # tn.set_debuglevel(10)

    print('[DOING] login username: ' + args.username)
    tn.read_until(big5('請輸入代號：'))

    if args.username == 'guest':
        tn.write(args.username + '\r')
    else:
        tn.write(args.username + '\r')
        tn.read_until(big5('請輸入密碼：'))
        tn.write(args.password + '\r')

    print('[DOING] check duplicate connection')
    checkStrs = [big5('您想刪除其他重複的 login')]
    matchIdx, matchObj, text = tn.expect(checkStrs, timeout=1)  # secs
    if matchIdx != -1:
        tn.write('\r')  # just proceed

    print('[DOING] enter main menu')
    tn.write('\r\r\r')  # skip to main menu
    tn.read_until(big5('【 再別熊窩 】'))

    print('[DOING] enter board: ' + args.board)
    tn.write(big5('\r' + 's'))  # enter (B)oards && 's' to directly goto board
    tn.read_until(big5('請輸入看板名稱(按空白鍵自動搜尋)：'))
    tn.read_very_eager()  # clear buffer
    tn.write(args.board + '\r')

    print('[DOING] skip enter board screen')
    checkStrs = [big5('▏▎▍▌▋▊▉\s\x1B\[1;37m請按任意鍵繼續\s\x1B\[1;33m▉\x1B\[m')]
    matchIdx, matchObj, text = tn.expect(checkStrs, timeout=1)
    if matchIdx != -1:
        tn.write('\r')
        time.sleep(1)
        tn.read_very_eager()  # clear buffer

    articleEndStr = big5('搜尋作者')

    for i in range(args.start, args.end + 1):
        big5txt = ''
        print('[DOING] crawl article {}'.format(i))
        tn.write(str(i) + '\r\r')
        time.sleep(0.05)
        big5txt = tn.read_very_eager()

        # 刪除沒清乾淨的文章列表
        pos = big5txt.find(big5('\x1B[;H\x1B[2J\x1B[47;34m'))
        if pos != -1:
            big5txt = big5txt[pos:]

        utf8txt = strip_status_bar(big5txt).decode('uao_decode', errors='ignore')

        lineIdx = 24
        while articleEndStr not in big5txt:
            print ('[DOING] crawl article {}: read line {}'.format(i,lineIdx))
            tn.write('\x1B[B')  # down
            time.sleep(0.05)
            line = tn.read_very_eager()
            big5txt += line
            utf8txt += strip_status_bar(line).decode('uao_decode', errors='ignore').replace(big5('\x1B[23;1H'), '')
            lineIdx += 1

        utf8txt += '\n'.decode('uao_decode', errors='ignore')

        outpath = os.path.join(args.outdir, '{}-{:05}.big5.txt'.format(args.board, i))
        with open(outpath, 'wb') as big5file:
            big5file.write(big5txt)

        outpath = os.path.join(args.outdir, '{}-{:05}.utf8.txt'.format(args.board, i))
        with codecs.open(outpath, 'w', encoding='utf8') as utf8file:
            utf8file.write(utf8txt)

        tn.write(big5('q'))  # leave the board

    print('[DOING] close connection')
    tn.close()
