#!/usr/bin/env python
# coding: utf-8
# created by hevlhayt@foxmail.com 
# Date: 2016/7/9
# Time: 13:50
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from friendnet.methods.basic.user import get_user_name
from friendnet.methods.session import get_session_id
from friendnet.methods.utils import logger_join
from friendnet.models import GroupMember, MemberRequest
from LineMe.constants import GROUP_MAXSIZE
from LineMe.settings import logger


# Todo: check member duplicate
def create_group_member(request, group, name, identifier, user=None, is_creator=False, is_joined=False):
    now = timezone.now()

    if user is not None and \
            GroupMember.objects.filter(
                group=group,
                user=user
            ).exists():

        return -1

    elif GroupMember.objects.filter(group=group).count() >= GROUP_MAXSIZE:
        return -3

    try:

        m = GroupMember(group=group,
                        user=user,
                        member_name=name,
                        token=identifier,
                        is_creator=is_creator,
                        is_joined=is_joined,
                        created_time=now)

        if is_joined:
            m.joined_time = now

        m.save()

    except Exception, e:
        # print 'Group member create: ', e
        logger.error(logger_join('Create', get_session_id(request), 'failed', e=e))
        return -4

    logger.info(logger_join('Create', get_session_id(request), mid=m.id))
    return 0


def create_group_member_from_file(request, group):
    members = []
    with request.FILES.get('members') as f:
        for l in f:
            kv = l.strip().split(',')

            if len(kv) != 2:
                return -1
            else:
                members.append(kv)

    for m in members:
        if create_group_member(request, group, m[0], m[1]) != 0:
            logger.error(logger_join('File', get_session_id(request), 'failed', gid=group.id))
            return m[0]

    logger.info(logger_join('File', get_session_id(request), gid=group.id))
    return 0


# Todo: fix the func
def follow(request, user, group, identifier):
    """

    :param request:
    :param user:
    :param group:
    :param identifier:
    :return:
    """
    if not GroupMember.objects.filter(
            member_name=get_user_name(user),
            group=group,
            token=identifier,
            is_joined=False
    ).exists():

        return -1

    now = timezone.now()
    try:
        m = GroupMember.objects.filter(
            member_name=get_user_name(user),
            group=group,
            token=identifier,
            is_joined=False,
        )[0]

        m.is_joined = True
        m.user = user
        m.joined_time = now
        m.save()
    except Exception, e:
        logger.error(logger_join('Join', get_session_id(request), 'failed', e=e))
        return -4

    logger.info(logger_join('Join', get_session_id(request), mid=m.id))
    return 0


def myself_member(user, groupid):
    return get_object_or_404(GroupMember,
                             user=user,
                             group__id=groupid,
                             is_joined=True)


def create_request(request, user, group, msg):
    try:
        if MemberRequest.objects.filter(
                user=user,
                group=group
        ).exists():

            mr = get_object_or_404(MemberRequest,
                                   user=user,
                                   group=group)
            mr.message = msg

        else:
            mr = MemberRequest(user=user,
                               group=group,
                               message=msg,
                               created_time=timezone.now(),
                               is_valid=True)
        mr.save()
    except Exception, e:
        logger.error(logger_join('Request', get_session_id(request), 'failed', e=e))
        return -4

    logger.info(logger_join('Request', get_session_id(request), rid=mr.id))
    return 0



