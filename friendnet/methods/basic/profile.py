#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/11
# Time: 13:38
import datetime

import re

from friendnet.methods.session import get_session_id
from friendnet.methods.utils import logger_join
from friendnet.models import Extra
from LineMe.constants import CITIES_TABLE
from LineMe.settings import logger


class Profile:
    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.first_name = request.POST.get('firstname')
        self.last_name = request.POST.get('lastname')
        self.birth = request.POST.get('birth')
        self.gender = int(request.POST.get('gender'))
        self.country = request.POST.get('country')
        self.city = request.POST.get('city')
        self.institution = request.POST.get('institution')

        self.country, self.city = self.country.replace('-', ' '), self.city.replace('-', ' ')

    def update(self):
        try:
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name

            ue = Extra.objects.get(user=self.user)
            ue.gender = self.gender
            ue.birth = datetime.datetime.strptime(self.birth, '%Y/%m/%d').date()
            ue.location = self.country + '-' + self.city
            ue.institution = self.institution
            self.user.save()
            ue.save()

        except Exception, e:
            # print 'Profile update failed: ', e
            logger.error(logger_join('Update', get_session_id(self.request), 'failed', e=e))
            return -1

        logger.info(logger_join('Update', get_session_id(self.request)))
        return 0

    def is_valid(self):
        if re.match(u"^[A-Za-z]{0,30}[\u4e00-\u9fa5]{0,10}$", self.first_name) and \
                re.match(u"^[A-Za-z]{0,30}[\u4e00-\u9fa5]{0,10}$", self.last_name):
            if self.gender == 0 or self.gender == 1:
                if re.match("^(?:(?!0000)[0-9]{4}/(?:(?:0[1-9]|1[0-2])/(?:0[1-9]|1[0-9]|2[0-8])|"
                            "(?:0[13-9]|1[0-2])/(?:29|30)|(?:0[13578]|1[02])-31)|(?:[0-9]{2}(?:0[48]|"
                            "[2468][048]|[13579][26])|(?:0[48]|[2468][048]|[13579][26])00)/02/29)$", self.birth):
                    if re.match(u"^[A-Za-z0-9\u4e00-\u9fa5\s.!@#&\\\/\|:{}()';\"]{0,100}$", self.institution):
                        if self.country in CITIES_TABLE and self.city in CITIES_TABLE[self.country]:
                            return True
        return False
