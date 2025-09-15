# 项目：标准程序库
# 模块：发送电子邮件
# 作者：黄涛
# License:GPL
# Email:huangtao.sh@icloud.com
# 创建：2016-10-26 10:25
# 修改：2019-02-14 15:54 对部分代码进行修订
# 修改：2019-12-02 12:18 优化 Mail.post 功能，不送服务器也可以发送
# 修改：2025-03-22 11:09 从 charset 导入Charset


import io
import logging
import smtplib
from email import encoders
from email.charset import Charset
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, getaddresses
from typing import Callable

from orange.shell import Path
from orange.utils.click import arg

conf_path = Path("~/mail.conf")


def config(**conf):
    from json import dumps

    from orange import encrypt
    conf['port'] = int(conf['port']) if conf['port'] else 0
    sender = conf.get('user')
    if '@' not in sender:
        sender = conf.get('host').replace('smtp.', f'{sender}@')
    conf['sender'] = sender
    mail_config(**conf)
    MailClient()
    conf['passwd'] = encrypt(conf['passwd'])
    conf_path.text = dumps(conf, indent=4, sort_keys=True)


def get_conf():
    from json import loads

    from orange import decrypt
    try:
        conf = loads(conf_path.text)
        conf['passwd'] = decrypt(conf['passwd'])
        return conf
    except Exception:
        return {}


def combine(type_: str = 'mixed', *subparts):
    '''合并邮件的各个部分，
    type_可以为以下几个值：
    related:     合并正文和内嵌附件；
    alternative: 合并纯文本正文和超文本正文；
    mixed:       合并正文和附件
    '''
    return MIMEMultipart(type_, _subparts=subparts)


def encode(filename: str) -> str:
    '''对文件进行编码'''
    return Charset('utf8').header_encode(filename) \
        if any(map(lambda x: ord(x) > 127, filename)) else filename


def fmtaddr(addrs: str) -> str:
    '''格式化邮件地址'''
    return ';'.join(map(formataddr, getaddresses([addrs])))


def sendmail(*messages):
    '''发送邮件'''
    with MailClient() as client:
        for message in messages:
            message.post(client)


def tsendmail(*args):
    '''采用线程发送邮件'''
    from threading import Thread
    Thread(target=sendmail, args=args).start()


def mail_config(**conf):
    MailClient.config = conf.copy()


class MailClient(smtplib.SMTP):
    '''构造邮件客户端，使用方法如下：
       client=MailClient(host,user,passwd)
    '''
    config = {}  # 使用参数配置的

    def __init__(self, host=None, user=None, passwd=None, *args, **kw):
        self.config = self.config or get_conf()
        host = host or self.config.get('host')
        user = user or self.config.get('user')
        passwd = passwd or self.config.get('passwd')
        super().__init__(host, *args, **kw)
        self.login(user, passwd)

    def Mail(self, *args, **kw):
        m = Mail(*args, client=self, **kw)
        if m.Sender is None:
            m.Sender = self.config.get('sender')
        return m


# 常见附件类型
MIMETYPE = (
    ('.aiff', 'audio/x-aiff'),
    ('.asf', 'video/x-ms-asf'),
    ('.asr', 'video/x-ms-asf'),
    ('.asx', 'video/x-ms-asf'),
    ('.au', 'audio/basic'),
    ('.avi', 'video/x-msvideo'),
    ('.bas', 'text/plain'),
    ('.bin', 'application/octet-stream'),
    ('.bmp', 'image/bmp'),
    ('.c', 'text/plain'),
    ('.css', 'text/css'),
    ('.dotx',
     'application/vnd.openxmlformats-officedocument.wordprocessingml.template'
     ),
    ('.docx',
     'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
     ),
    ('.doc', 'application/msword'),
    ('.dot', 'application/msword'),
    ('.exe', 'application/octet-stream'),
    ('.gif', 'image/gif'),
    ('.gz', 'application/x-gzip'),
    ('.h', 'text/plain'),
    ('.htm', 'text/html'),
    ('.html', 'text/html'),
    ('.ico', 'image/x-icon'),
    ('.jfif', 'image/pipeg'),
    ('.jpe', 'image/jpeg'),
    ('.jpeg', 'image/jpeg'),
    ('.jpg', 'image/jpeg'),
    ('.js', 'application/x-javascript'),
    ('.latex', 'application/x-latex'),
    ('.lha', 'application/octet-stream'),
    ('.m3u', 'audio/x-mpegurl'),
    ('.mid', 'audio/mid'),
    ('.mov', 'video/quicktime'),
    ('.movie', 'video/x-sgi-movie'),
    ('.mp2', 'video/mpeg'),
    ('.mp3', 'audio/mpeg'),
    ('.mpa', 'video/mpeg'),
    ('.mpe', 'video/mpeg'),
    ('.mpeg', 'video/mpeg'),
    ('.mpg', 'video/mpeg'),
    ('.mpv2', 'video/mpeg'),
    ('.pdf', 'application/pdf'),
    ('.png', 'image/png'),
    ('.ppm', 'image/x-portable-pixmap'),
    ('.pps', 'application/vnd.ms-powerpoint'),
    ('.ppt', 'application/vnd.ms-powerpoint'),
    ('.pptx',
     'application/vnd.openxmlformats-officedocument.presentationml.presentation'
     ),
    ('.ps', 'application/postscript'),
    ('.pub', 'application/x-mspublisher'),
    ('.qt', 'video/quicktime'),
    ('.rtf', 'application/rtf'),
    ('.rtx', 'text/richtext'),
    ('.sh', 'application/x-sh'),
    ('.svg', 'image/svg+xml'),
    ('.tar', 'application/x-tar'),
    ('.tex', 'application/x-tex'),
    ('.tgz', 'application/x-compressed'),
    ('.tif', 'image/tiff'),
    ('.tiff', 'image/tiff'),
    ('.tr', 'application/x-troff'),
    ('.trm', 'application/x-msterminal'),
    ('.tsv', 'text/tab-separated-values'),
    ('.txt', 'text/plain'),
    ('.ustar', 'application/x-ustar'),
    ('.wav', 'audio/x-wav'),
    ('.xlm', 'application/vnd.ms-excel'),
    ('.xls', 'application/vnd.ms-excel'),
    ('.xlsx',
     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    ('.xlt', 'application/vnd.ms-excel'),
    ('.xlw', 'application/vnd.ms-excel'),
    ('.z', 'application/x-compress'),
    ('.zip', 'application/zip'),
)

MIMETYPES = {suffix: type_ for suffix, type_ in MIMETYPE}


class Mail:
    '''创建电子邮件，使用方法如下：
    mail=Mail(sender,to,subject,body,cc,bcc)
    添加附件：
    mail.attach(filename,cid=None,writer=None)
    发送邮件：
    mail.post(client)
    '''

    def __init__(self,
                 sender=None,
                 to=None,
                 subject=None,
                 body=None,
                 cc=None,
                 bcc=None,
                 client=None):
        '''初始化邮件'''
        self.attachments = []
        self.inline_attachments = []
        self.body = body
        self.Subject = subject
        self.To = to
        self.Sender = sender
        self.Cc = cc
        self.Bcc = bcc
        self.client = client

    @property
    def message(self):
        '''获取邮件的MESSAGE属性'''
        body = self.body
        subtype = 'html' if body.startswith('<html>') else 'plain'  # 设置正文类型
        msg = MIMEText(body, subtype, 'utf-8')  # 构建邮件正文
        if self.inline_attachments:  # 合并内嵌附件
            msg = combine('related', msg, *self.inline_attachments)
        if self.attachments:  # 合并附件
            msg = combine('mixed', msg, *self.attachments)
        msg.add_header('Subject', self.Subject)  # 设置标题
        for name in ('Sender', 'To', 'Cc', 'Bcc'):  # 设置收件人及发件人
            val = getattr(self, name)
            if val:
                msg.add_header(name, fmtaddr(val))
        return msg

    def __str__(self):
        return self.message.as_string()

    def add_fp(self, fp, filename):
        self.attach(filename, writer=fp)

    def attach(self, filename: str, cid: str = None, data: bytes = None, writer: Callable = None):  # 添加附件
        '''
        filename: 文件名
        cid：     内嵌资源编号，如设置则不出现在附件列表中
        writer:   内容生成，如设置，则通过 writer(fn)的形式来获取数据
        '''
        file = Path(filename)
        msg = MIMEBase(*MIMETYPES.get(file.suffix.lower(),
                                      'application/octet-stream').split('/'))
        if callable(writer):
            with io.BytesIO() as fp:
                writer(fp)
                fp.seek(0)
                data = fp.read()
        elif not data:
            data = file.read_bytes()
        msg.set_payload(data)
        encoders.encode_base64(msg)
        msg.add_header('Content-Disposition',
                       'inline' if cid else 'attachment',
                       filename=encode(file.name))
        if cid:
            msg.add_header('Content-ID', f'<{cid}>')
            msg.add_header('X-Attachment-Id', cid)
            self.inline_attachments.append(msg)
        else:
            self.attachments.append(msg)

    add_file = attach
    add_image = attach

    def post(self, mailclient=None):
        mailclient = mailclient or self.client
        if mailclient:
            mailclient.send_message(self.message)
        else:
            try:
                with MailClient() as client:
                    logging.info('连接服务器成功')
                    if not self.Sender:
                        self.Sender = client.config.get('sender')
                        logging.info('获取 sender 成功')
                    client.send_message(self.message)
            except Exception as e:
                logging.fatal(str(e))
                print('发送失败：', e)
            else:
                logging.info('发送邮件成功')
                print('发送邮件成功')


@arg('-c', '--config', dest='url', metavar='url', nargs='?', help='邮箱配置')
@arg('-s', '--show', action='store_true', help='显示配置')
@arg('-t', '--test', action='store_true', help='测试服务器连接')
def config_mail(**options):
    if options.get('show'):
        from orange import tprint
        con = get_conf()
        con['passwd'] = '*'*len(con['passwd'])
        print('当前邮箱配置')
        tprint(con.items(), format_spec='{:10} {}', print_rows=False)
    if url := options.get('url'):
        from orange import R
        pattern = R / \
            r'(?P<user>.*?):(?P<passwd>.*?)@(?P<host>.*?):?(?P<port>\d+)?'
        if m := pattern.fullmatch(url):
            try:
                config(**m.groupdict())
                print('配置邮箱成功')
            except Exception as e:
                print(e)
        else:
            print('邮箱配置不正确，应为：user:passwd@host:port')
    if options.get('test'):
        try:
            MailClient()
            print('连接成功')
        except Exception as e:
            print('连接失败:', e)
