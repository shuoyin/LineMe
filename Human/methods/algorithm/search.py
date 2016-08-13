#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/8/12
# Time: 23:06
from django.db.models import Q

from Human.methods.session import get_session_id
from Human.methods.utils import logger_join, input_filter
from Human.models import GroupMember, Group
from LineMe.settings import logger


# Todo: private group no result but i am in the list
class SearchEngine:
    def __init__(self, request):
        self.request = request
        self.user = request.user

    def search(self, limit=-1):

        kw = input_filter(self.request.GET.get('kw'))
        groupid = self.request.GET.get('gid')

        logger.info(logger_join('Search', get_session_id(self.request), kw=kw))

        if kw == '':
            return []

        if groupid:
            return self.__group_search(groupid, kw, limit)

        else:
            return self.__member_search(kw, limit)

    def __group_search(self, groupid, kw, limit):
        res = []
        gms = GroupMember.objects.filter(Q(member_name__istartswith=kw) |
                                         Q(member_name__icontains=kw),
                                         group__id=groupid).order_by('member_name')[0:limit]
        for gm in gms:
            if gm.is_joined:
                res.append({"mid": gm.id, "uid": gm.user.id, "mname": gm.member_name})
            else:
                res.append({"mid": gm.id, "uid": 0, "mname": gm.member_name})

        return res

    def __member_search(self, kw, limit):
        res = []

        gs = Group.objects.filter(group_name__istartswith=kw).order_by('group_name')
        gs1 = gs.filter(creator=self.user)
        gs2 = gs.exclude(creator=self.user).filter(type=0)

        for g in (gs1 | gs2)[0:limit]:
            res.append({"cid": g.creator.id, "gid": g.id, "name": g.group_name})

        return res

