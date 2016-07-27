# hulabear-crawler
rescue our NTHU CS memories

## Usage
    usage: hulabear-crawler.py [-h] [-u USERNAME] [-p PASSWORD] [-b BOARD]
                               [-o OUTDIR] [-s START] [-e END]
    
    Hulabear BBS crawler for ONE board
    
    optional arguments:
      -h, --help            show this help message and exit
      -u USERNAME, --username USERNAME
                            Required (ask if missing). Default="guest"
      -p PASSWORD, --password PASSWORD
                            Required if username is not "guest"
      -b BOARD, --board BOARD
                            Required. Default="anonymous"
      -o OUTDIR, --outdir OUTDIR
                            Output folder for crawled articles. Default="crawled"
      -s START, --start START
                            Article start counter. Default=1
      -e END, --end END     Article end counter. Default=3

## Credits
- "簡易版 PTT 爬蟲", http://mhwong2007.logdown.com/posts/314403
- "uao_decode", https://gist.github.com/andycjw/5617496
- "BBS Crawler 筆記", http://blog.changyy.org/2010/08/python-bbs-crawler.html
- "naive PTT gossiping crawler", http://daat-blog.logdown.com/posts/181159-naive-ptt-gossiping-crawler
- "輔仁大學搶課系統-by YunChen", https://github.com/chenyunchen/FJUSYSTEM/blob/master/fjusystem.py
- "交大BS2 BBS 爬蟲", https://github.com/iblis17/bs2-crawler/blob/master/crawler.py
- "龜/geniusturtle6174", https://github.com/geniusturtle6174/hulabearCrawler

## todo
- list board, check board exists
- better status report
- [bsdconv](http://www.slideshare.net/Buganini/bbs-crawler-for-taiwan)
