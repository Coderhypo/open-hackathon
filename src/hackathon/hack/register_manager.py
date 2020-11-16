# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")

from flask import g

from hackathon import Component, RequiredFeature
from hackathon.db.models import UserHackathon, Experiment
from hackathon.hackathon_response import bad_request, precondition_failed, internal_server_error, not_found, ok, \
    login_provider_error
from hackathon.constants import ExprStatus, HackathonPlayerStatus, HackathonConfig, HackathonStat, LoginProvider, \
    HackathonPlayerType, HackathonNotifyCategory, HackathonNotifyEvent

__all__ = ["RegisterManager"]


class RegisterManager(Component):
    """Component to manage registered users of a hackathon"""
    hackathon_manager = RequiredFeature("hackathon_manager")
    user_manager = RequiredFeature("user_manager")
    admin_manager = RequiredFeature("admin_manager")
    team_manager = RequiredFeature("team_manager")

    def get_hackathon_registration_list(self, hackathon_id, num=None):
        """Get registered users list

        :rtype: list
        :return all registered usrs if num is None else return the specific number of users order by create_time desc
        """
        registers = UserHackathon.objects(hackathon=hackathon_id,
                                          role=HackathonPlayerType.COMPETITOR).order_by('-create_time')[:num]

        return [self.__get_registration_with_profile(x) for x in registers]

    def get_registration_by_id(self, registration_id):
        return UserHackathon.objects(id=registration_id).first()

    def get_registration_by_user_and_hackathon(self, user_id, hackathon_id):
        return UserHackathon.objects(user=user_id, hackathon=hackathon_id, role=HackathonPlayerType.COMPETITOR).first()

    def create_registration(self, hackathon, user, args):
        """Register hackathon for user

        Will add a new record in table UserRegistrationRel if precondition fulfilled
        """
        self.log.debug("create_register: %r" % args)
        user_id = args['user_id']

        check_login_provider = self.__is_user_hackathon_login_provider(user, hackathon)
        if check_login_provider["fail"]:
            return login_provider_error(
                "hackathon registration not login provider",
                friendly_message="当前黑客松活动只是使用" + ",".join(check_login_provider["provides"]) + "账户才能报名",
                provides=",".join(check_login_provider["provides"]))

        if self.is_user_registered(user.id, hackathon):
            self.log.debug("user %s already registered on hackathon %s" % (user_id, hackathon.id))
            return self.get_registration_detail(user, hackathon)

        if self.admin_manager.is_hackathon_admin(hackathon.id, user.id):
            return precondition_failed("administrator cannot register the hackathon", friendly_message="管理员或裁判不能报名")

        if hackathon.registration_start_time and hackathon.registration_start_time > self.util.get_now():
            return precondition_failed("hackathon registration not opened", friendly_message="报名尚未开始")

        if hackathon.registration_end_time and hackathon.registration_end_time < self.util.get_now():
            return precondition_failed("hackathon registration has ended", friendly_message="报名已经结束")

        if self.__is_hackathon_filled_up(hackathon):
            return precondition_failed("hackathon registers reach the upper threshold",
                                       friendly_message="报名人数已满")

        try:
            is_auto_approve = hackathon.config.get(HackathonConfig.AUTO_APPROVE, True)
            status = HackathonPlayerStatus.AUTO_PASSED if is_auto_approve else HackathonPlayerStatus.UNAUDIT
            args.pop("user_id")
            args.pop("hackathon_id")

            user_hackathon = UserHackathon.objects(user=user, hackathon=hackathon).first()
            if not user_hackathon:
                user_hackathon = UserHackathon.objects.create(
                    user=user,
                    hackathon=hackathon,
                    status=status,
                    **args)
            else:  # visitor -> competitor
                user_hackathon.role = HackathonPlayerType.COMPETITOR
                user_hackathon.status = status
                user_hackathon.save()

            # create a team as soon as user registration approved(auto or manually)
            if is_auto_approve:
                self.team_manager.create_default_team(hackathon, user)
                self.__ask_for_dev_plan(hackathon, user)

            self.__update_register_stat(hackathon)
            return user_hackathon.dic()
        except Exception as e:
            self.log.error(e)
            return internal_server_error("fail to create register")

    def __ask_for_dev_plan(self, hackathon, user):
        # push notice if dev plan required
        if hackathon.config.get(HackathonConfig.DEV_PLAN_REQUIRED, False):
            self.hackathon_manager.create_hackathon_notice(hackathon.id, HackathonNotifyEvent.HACK_PLAN,
                                                           HackathonNotifyCategory.HACKATHON, {'receiver': user})

    def update_registration(self, context):
        try:
            registration_id = context.id
            register = self.get_registration_by_id(registration_id)
            if register is None or register.hackathon.id != g.hackathon.id:
                # we can also create a new object here.
                return not_found("registration not found")

            register.update_time = self.util.get_now()
            register.status = context.status
            register.save()

            if register.status == HackathonPlayerStatus.AUDIT_PASSED:
                self.team_manager.create_default_team(register.hackathon, register.user)
                self.__ask_for_dev_plan(register.hackathon, register.user)

            hackathon = self.hackathon_manager.get_hackathon_by_id(register.hackathon.id)
            self.__update_register_stat(hackathon)

            return register.dic()
        except Exception as e:
            self.log.error(e)
            return internal_server_error("fail to update register")

    def delete_registration(self, args):
        """
        Delete the registration of a user in a hackathon, also do operation on the user's team.
        """
        if "id" not in args:
            return bad_request("id not invalid")
        try:
            register = self.get_registration_by_id(args["id"])
            if register is not None:
                register.delete()
                hackathon = register.hackathon
                self.__update_register_stat(hackathon)

                team = self.team_manager.get_team_by_user_and_hackathon(register.user, hackathon)
                if not team:
                    self.log.warn("team of this registered user is not found!")
                    return ok()
                self.team_manager.quit_team_forcedly(team, register.user)

            return ok()
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("failed in delete register: %s" % args["id"])

    def get_registration_detail(self, user, hackathon, registration=None):
        detail = {
            "hackathon": hackathon.dic(),
            "user": self.user_manager.user_display_info(user)}

        if not registration:
            registration = registration or self.get_registration_by_user_and_hackathon(user.id, hackathon.id)

        if not registration:
            return detail

        # "asset" is alreay in registration
        detail["registration"] = registration.dic()
        # experiment if any
        try:
            exp = Experiment.objects(
                user=user.id,
                hackathon=hackathon.id,
                status__in=[ExprStatus.STARTING, ExprStatus.RUNNING]).first()

            if exp:
                detail["experiment"] = exp.dic()
        except Exception as e:
            self.log.error(e)

        return detail

    def __update_register_stat(self, hackathon):
        count = UserHackathon.objects(
            hackathon=hackathon.id,
            status__in=[HackathonPlayerStatus.AUDIT_PASSED, HackathonPlayerStatus.AUTO_PASSED],
            role=HackathonPlayerType.COMPETITOR,
            # TODO
            deleted=False).count()

        self.hackathon_manager.update_hackathon_stat(hackathon, HackathonStat.REGISTER, count)

    def is_user_registered(self, user_id, hackathon):
        """Check whether use registered certain hackathon"""
        register = self.get_registration_by_user_and_hackathon(user_id, hackathon.id)
        return register is not None and register.role == HackathonPlayerType.COMPETITOR

    def __get_registration_with_profile(self, registration):
        """Return user display info as well as the registration detail in dict

        :type registration: UserHackathonRel
        :param registration: the detail of the user registration

        :rtype: dict
        :return the detail of registration as well as user display info
        """
        register_dic = registration.dic()
        register_dic['user'] = self.user_manager.user_display_info(registration.user)
        return register_dic

    def __is_hackathon_filled_up(self, hackathon):
        """Check whether all seats are occupied or not

        :return False if not all seats occupied or hackathon has no limit at all otherwise True
        """
        # TODO
        maximum = self.hackathon_manager.get_basic_property(hackathon, HackathonConfig.MAX_ENROLLMENT, 0)

        if maximum == 0:  # means no limit
            return False
        else:
            # count of audited users
            current_num = UserHackathon.objects(
                hackathon=hackathon.id,
                status__in=[HackathonPlayerStatus.AUDIT_PASSED, HackathonPlayerStatus.AUTO_PASSED],
                role=HackathonPlayerType.COMPETITOR).count()

            return current_num >= maximum

    def __is_user_hackathon_login_provider(self, user, hackathon):
        """Check whether login provider

        :return False if not all seats occupied or hackathon has no limit at all otherwise True
        """
        login_provider = hackathon.config.get("login_provider")
        data = {"fail": False, "provides": []}

        if login_provider:
            hackathon_login_provider = int(login_provider)

            for mask, provide in (
                    (LoginProvider.LIVE, "live"),
                    (LoginProvider.GITHUB, "github"),
                    (LoginProvider.QQ, "qq"),
                    (LoginProvider.WECHAT, "wechat"),
                    (LoginProvider.WEIBO, "weibo")):
                if (hackathon_login_provider & mask) > 0:
                    data["provides"].append(provide)

            data["fail"] = user.provider not in data["provides"]

        return data
