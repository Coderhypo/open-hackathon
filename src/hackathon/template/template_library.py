# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
from flask import g
from werkzeug.exceptions import BadRequest, InternalServerError, Forbidden, NotFound
from mongoengine import Q

from hackathon import Component, RequiredFeature
from hackathon.constants import VirtualEnvProvider
from hackathon.db.models import Template, Experiment, NetworkConfigTemplate
from hackathon.hackathon_response import ok, internal_server_error, forbidden
from hackathon.constants import TemplateStatus
from hackathon.template.template_constants import TEMPLATE
from hackathon.template.template_content import TemplateContent

__all__ = ["TemplateLibrary"]


class TemplateLibrary(Component):
    """Component to manage templates"""

    storage = RequiredFeature("storage")
    user_manager = RequiredFeature("user_manager")

    def get_template_info_by_id(self, template_id):
        """Query template basic info from DB by its id

        :type template_id: int
        :param template_id: unique id of Template
        """
        return Template.objects(id=template_id).first()

    def get_template_info_by_name(self, template_name):
        """Query template basic info from DB by its id

        :type template_name: str|unicode
        :param template_name: unique name of Template
        """
        return Template.objects(name=template_name).first()

    def search_template(self, args):
        """Search template by status, name or description"""
        criterion = self.__generate_search_criterion(args)
        return [t.dic() for t in Template.objects(criterion)]

    @staticmethod
    def load_template(template):
        """load template content
        :param template:
        :return:
        """
        return TemplateContent.load_from_template(template)

    def create_template(self, args):
        """ Create template """
        template_content = self.__load_template_content(args)
        return self.__create_or_update_template(template_content)

    def update_template(self, args):
        """update a exist template

        The whole logic contains 3 main steps:
        1 : args validate for update operation
        2 : parse args and save to storage
        3 : save to database

        :type args: dict
        :param args: description of the template that you want to create

        :return:
        """
        template_content = self.__load_template_content(args)
        template = self.get_template_info_by_name(template_content.name)
        if template is not None:
            # user can only modify the template which created by himself except super admin
            if g.user.id != template.creator.id and not g.user.is_super:
                raise Forbidden()
        else:
            raise NotFound()

        return self.__create_or_update_template(template_content)

    def delete_template(self, template_id):
        self.log.debug("delete template [%s]" % template_id)
        try:
            template = self.get_template_info_by_id(template_id)
            if template is None:
                return ok("already removed")
            # user can only delete the template which created by himself except super admin
            if g.user.id != template.creator.id and not g.user.is_super:
                return forbidden()
            if Experiment.objects(template=template).count() > 0:
                return forbidden("template already in use")

            # remove record in DB
            # the Hackathon used this template will imply the mongoengine's PULL reverse_delete_rule
            self.log.debug("delete template {}".format(template.name))
            template.delete()

            return ok("delete template success")
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("delete template failed")

    def template_verified(self, template_id):
        Template.objects(id=template_id).update_one(status=TemplateStatus.CHECK_PASS)

    def __init__(self):
        pass

    def __create_or_update_template(self, template_content):
        """Internally create template

        Save template to storage and then insert into DB

        :type template_content: TemplateContent
        :param template_content: instance of TemplateContent that owns the full content of a template
        """
        if not template_content.is_valid():
            raise BadRequest("template content is illegal")
        return self.__save_template_to_database(template_content)

    def __save_template_to_database(self, template_content):
        """save template date to db

        According to the args , find out whether it is ought to insert or update a record

        :type template_content: TemplateContent
        :param template_content: instance of TemplateContent that owns the full content of a template

        :return: if raised exception return InternalServerError else return nothing

        """
        network_configs = [
            NetworkConfigTemplate(name=c.name, protocol=c.protocol, port=c.port)
            for c in template_content.network_configs]

        template = self.get_template_info_by_name(template_content.name)
        if template:
            if template.provider != template.provider:
                raise BadRequest(description="template provider cannot be modified")
            try:
                template.update(
                    update_time=self.util.get_now(),
                    description=template_content.description,
                    content=template_content.yml_template,
                    template_args=template_content.template_args,
                    docker_image=template_content.docker_image,
                    network_configs=network_configs,
                )
                return template.dic()
            except Exception as ex:
                self.log.error(ex)
                raise InternalServerError(description="update record in db failed")
        try:
            if template is None:
                template = Template.objects.create(
                    name=template_content.name,
                    provider=template_content.provider,
                    status=TemplateStatus.UNCHECKED,
                    content=template_content.yml_template,
                    description=template_content.description,
                    template_args=template_content.template_args,
                    docker_image=template_content.docker_image,
                    network_configs=network_configs,
                    creator=g.user,
                    virtual_environment_count=0)
            return template.dic()
        except Exception as ex:
            self.log.error(ex)
            raise InternalServerError(description="insert record in db failed")

    def __generate_search_criterion(self, args):
        """generate DB query criterion according to Querystring of request.

        The output will be MongoEngine understandable expressions.
        """
        criterion = Template.status != -1
        if 'status' in args and int(args["status"]) >= 0:
            criterion = Q(status=args["status"])
        else:
            criterion = Q(status__ne=-1)

        if 'name' in args and len(args["name"]) > 0:
            criterion &= Q(name__icontains=args["name"])

        if 'description' in args and len(args["description"]) > 0:
            criterion &= Q(description__icontains=args["description"])

        return criterion

    def __load_template_content(self, args):
        """ Convert dict of template content into TemplateContent object

        :type args: dict
        :param args: args to create a template

        :rtype: TemplateContent
        :return: instance of TemplateContent
        """
        self.__validate_template_content(args)
        name = args[TEMPLATE.TEMPLATE_NAME]
        description = args[TEMPLATE.DESCRIPTION]

        environment_config = args[TEMPLATE.VIRTUAL_ENVIRONMENT]

        tc = TemplateContent(name, description, environment_config)
        return tc

    @staticmethod
    def __validate_template_content(args):
        """ validate args when creating a template

        :type args: dict
        :param args: args to create a template

        :return: if validate passed return nothing else raised a BadRequest exception

        """
        if not args:
            raise BadRequest(description="template name invalid")

        if TEMPLATE.TEMPLATE_NAME not in args:
            raise BadRequest(description="template name invalid")

        if TEMPLATE.DESCRIPTION not in args:
            raise BadRequest(description="template description invalid")

        if TEMPLATE.VIRTUAL_ENVIRONMENT not in args:
            raise BadRequest(description="template virtual_environment invalid")

        if args[TEMPLATE.VIRTUAL_ENVIRONMENT][TEMPLATE.VIRTUAL_ENVIRONMENT_PROVIDER] not in (
                VirtualEnvProvider.DOCKER, VirtualEnvProvider.K8S):
            raise BadRequest(description="virtual_environment provider invalid")
