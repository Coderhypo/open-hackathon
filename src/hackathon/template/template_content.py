# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from collections import defaultdict

from hackathon.constants import VirtualEnvProvider
from hackathon.template.template_constants import TEMPLATE
from hackathon.template.docker_template_unit import DockerTemplateUnit
from hackathon.template.k8s_template_unit import K8STemplateUnit

__all__ = ["TemplateContent"]


class TemplateContent:
    """The content of a template in dict format

    It's the only type that for template saving and loading.
    """

    def __init__(self, name, description, environment_config):
        self.name = name
        self.description = description
        self.environment = self.__load_environment(environment_config)

        self.provider = self.environment.provider

        # TODO delete
        self.resource = defaultdict(list)
        self.cluster_info = None
        self.units = []

    @classmethod
    def load_from_template(cls, template):
        env_cfg = template.unit_config()
        return TemplateContent(template.name, template.description, env_cfg)

    @property
    def docker_image(self):
        if self.provider != VirtualEnvProvider.DOCKER:
            return ""
        return self.environment.image

    @property
    def network_configs(self):
        if self.provider != VirtualEnvProvider.DOCKER:
            return []
        return self.environment.network_configs

    @property
    def yml_template(self):
        if self.provider != VirtualEnvProvider.K8S:
            return ""
        return self.environment.yml_template

    @property
    def template_args(self):
        if self.provider != VirtualEnvProvider.K8S:
            return {}
        return self.environment.template_args

    def is_valid(self):
        if self.provider is None:
            return False

        if self.provider == VirtualEnvProvider.DOCKER:
            return True

        if self.provider == VirtualEnvProvider.K8S:
            return self.environment.is_valid() is True

    @classmethod
    def __load_environment(cls, environment_config):
        provider = int(environment_config[TEMPLATE.VIRTUAL_ENVIRONMENT_PROVIDER])
        if provider == VirtualEnvProvider.DOCKER:
            return DockerTemplateUnit(environment_config)
        elif provider == VirtualEnvProvider.K8S:
            return K8STemplateUnit(environment_config)
        else:
            raise Exception("unsupported virtual environment provider")

    # todo delete
    def get_resource(self, resource_type):
        # always return a list of resource desc dict or empty
        return self.resource[resource_type]

    # FIXME deprecated this when support K8s ONLY
    def to_dict(self):
        dic = {
            TEMPLATE.TEMPLATE_NAME: self.name,
            TEMPLATE.DESCRIPTION: self.description
        }

        def convert_to_dict(unit):
            if unit.provider == VirtualEnvProvider.DOCKER:
                return unit.dic
            elif unit.provider == VirtualEnvProvider.AZURE:
                raise NotImplementedError()
            return unit

        dic[TEMPLATE.VIRTUAL_ENVIRONMENTS] = list(map(convert_to_dict, self.units))
        return dic
