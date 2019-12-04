import json
import pickle

import six
from frozendict import frozendict

import ktrack_api
from kttk import template_manager, utils


class Context(object):
    """
    Context is an immutable object of the current project/entity/task/workfile combination, example:
    Project: Finding_Dory
    Entity: Hank (Asset)
    Task: modelling
    workfile: Hank_modelling_modelling_v001.mb
    Context only contains id and type for each entity. If you need a context with fully populated entities, use PopulatedContext
    """

    # todo make sure project, entity whatever can only be populated with correct entity types
    def __init__(self, project=None, entity=None, step=None, task=None, workfile=None, user=None):
        # project
        self._validate_entity_dict(project)
        self._project = utils.frozen_entity_id_dict(project)

        # entity
        self._validate_entity_dict(entity)
        if entity:
            assert entity['type'] != 'project'
        self._entity = utils.frozen_entity_id_dict(entity)

        # step
        self._validate_step(step)
        self._step = step

        # task
        self._validate_entity_dict(task)
        self._task = utils.frozen_entity_id_dict(task)

        # workfile
        self._validate_entity_dict(workfile)
        self._workfile = utils.frozen_entity_id_dict(workfile)

        # user
        self._validate_entity_dict(user)
        self._user = utils.frozen_entity_id_dict(user)

    @property
    def project(self):
        # type: () -> frozendict
        return self._project

    @property
    def entity(self):
        # type: () -> frozendict
        return self._entity

    @property
    def step(self):
        # type: () -> str
        return self._step

    @property
    def task(self):
        # type: () -> frozendict
        return self._task

    @property
    def workfile(self):
        # type: () -> frozendict
        return self._workfile

    @property
    def user(self):
        # type: () -> frozendict
        return self._user

    @staticmethod
    def _validate_step(step):
        # type: (str) -> bool
        """
        Validates the given step. A step can be null or string or unicode, but not empty string
        :param step: step to validate
        :return: True if step is valid, raises ValueError if not
        """
        if step is not None:
            if isinstance(step, six.string_types):
                if len(step) > 0:
                    return True
            raise ValueError("Invalid step, {} is not a non-empty string, its {}!".format(step, type(step)))
        else:
            return True

    @staticmethod
    def _validate_entity_dict(entity_dict):
        # type: (dict) -> bool
        """
        Validates the given entity dict. Should have at least a type and a id and they are not None
        :param dic:
        :return: true if entity has type and id, otherwise invalid entity Exception is thrown
        """
        if entity_dict is not None:
            has_type = entity_dict.get("type")
            has_id = entity_dict.get("id")

            if has_type and has_id:
                return True
            else:
                raise ValueError("Entity is invalid: type missing: {}, id missing: {}".format(not has_type, not has_id))
        else:
            return True

    def __repr__(self):
        # type: () -> str
        # multi line repr
        msg = []
        msg.append("  Project: %s" % str(self.project))
        msg.append("  Entity: %s" % str(self.entity))
        msg.append("  Step: %s" % str(self.step))
        msg.append("  Task: %s" % str(self.task))
        msg.append("  User: %s" % str(self.user))

        return "<kttk Context: \n%s>" % ("\n".join(msg))

    def _entity_dicts_equal(self, left, right):
        # type: (dict, dict) -> bool
        """
        Tests if two entity dicts are equal. They are equal if both type and id match or both are None
        :param left:
        :param right:
        :return:
        """
        if left == right == None:
            return True
        if left == None or right == None:
            return False
        return left["type"] == right["type"] and left["id"] == right["id"]

    def __eq__(self, other):
        # type: (Context) -> bool
        """
        Tests if two context are equal. Contexts are considered equal, if both type and id attributes of containing entities
        match and step string matches
        :param other:
        :return:
        """

        if not isinstance(other, Context):
            return NotImplemented

        # test project
        if not self._entity_dicts_equal(self.project, other.project):
            return False

        # test entity
        if not self._entity_dicts_equal(self.entity, other.entity):
            return False

        # test step
        if not self.step == other.step:
            return False

        # test task
        if not self._entity_dicts_equal(self.task, other.task):
            return False

        # test workfile
        if not self._entity_dicts_equal(self.workfile, other.workfile):
            return False

        # test user
        if not self._entity_dicts_equal(self.user, other.user):
            return False

        return True

    def __ne__(self, other):
        # type: (Context) -> bool
        """
        Test if this Context instance is not equal to the other Context instance

        :param other:   The other Context instance to compare with
        :returns:       True if self != other, False otherwise
        """
        is_equal = self.__eq__(other)
        if is_equal is NotImplemented:
            return NotImplemented
        return not is_equal

    def as_dict(self):
        # type: () -> dict
        """
        Converts this context into a dictionary
        :return: this context as dict
        """
        context_dict = {}
        context_dict['project'] = self.project
        context_dict['entity'] = self.entity
        context_dict['step'] = self.step
        context_dict['task'] = self.task
        context_dict['workfile'] = self.workfile
        context_dict['user'] = self.user

        return context_dict

    @classmethod
    def from_dict(cls, context_dict):
        # type: (dict) -> Context
        """
        Constructs a new Context from given dictionary
        :param context_dict:
        :return: a new Context object
        """
        return Context(project=context_dict.get('project'),
                       entity=context_dict.get('entity'),
                       step=context_dict.get('step'),
                       task=context_dict.get('task'),
                       workfile=context_dict.get('workfile'),
                       user=context_dict.get('user'))

    def serialize(self):
        # type: () -> str
        """
        Serializes this context to a pickle string
        :return:
        """
        return json.dumps(self.as_dict())

    @classmethod
    def deserialize(cls, string):
        # type: (str) -> Context
        return cls.from_dict(json.loads(string))

    def get_avaible_tokens(self):
        # type: () -> dict
        avaible_tokens = {}

        kt = ktrack_api.get_ktrack()

        if self.project:
            project = kt.find_one('project', self.project['id'])
            avaible_tokens['project_name'] = project['name']

        # make sure to query all fields from ktrack, because we might only have id and type

        if self.entity:
            entity = kt.find_one(self.entity['type'], self.entity['id'])
            avaible_tokens['code'] = entity['code']

            if entity['type'] == 'asset':
                avaible_tokens['asset_type'] = entity['asset_type']

        if self.step:
            avaible_tokens['step'] = self.step

        if self.task:
            task = kt.find_one('task', self.task['id'])
            avaible_tokens['task_name'] = task['name']

        if self.workfile:
            workfile = kt.find_one('workfile', self.workfile['id'])

            avaible_tokens['work_file_name'] = workfile['name']
            avaible_tokens['work_file_path'] = workfile['path']
            avaible_tokens['work_file_comment'] = workfile['comment']
            avaible_tokens['version'] = "v{}".format("{}".format(workfile['version_number']).zfill(3))

        if self.user:
            user = kt.find_one('user', self.user['id'])
            avaible_tokens['user_name'] = user['name']

        avaible_tokens['project_root'] = template_manager.get_route_template('project_root')

        return avaible_tokens

    def copy_context(self, project=0, entity=0, step=0, task=0, workfile=0, user=0):
        # type: (dict, dict, str, dict, dict, dict) -> Context
        """
        Copy util. Returns a new context instance, will contain values from this context if not overriden by keyword args
        Note: We use 0 here instead of None, so we can override with None
        :param self:
        :param project: project to override on new Context
        :param entity: entity to override on new Context
        :param step: step to override on new Context
        :param task: task to override on new Context
        :param workfile: workfile to override on new Context
        :param user: user to override on new Context
        :return: Context, values not overriden are the same as in this instance
        """
        _project = self.project
        if project != 0:
            _project = project

        _entity = self.entity
        if entity != 0:
            _entity = entity

        _step = self.step
        if step != 0:
            _step = step

        _task = self.task
        if task != 0:
            _task = task

        _workfile = self.workfile
        if workfile != 0:
            _workfile = workfile

        _user = self.user
        if user != 0:
            _user = user

        return Context(_project, _entity, _step, _task, _workfile, _user)

    def populate_context(self):
        """
        Returns a PopulatedContext context instance based on this context
        :return:
        """
        return PopulatedContext(project=self.project,
                                entity=self.entity,
                                step=self.step,
                                task=self.task,
                                workfile=self.workfile,
                                user=self.user)


class PopulatedContext(Context):
    """
    Same as Context, but with fully populated entities instead of only type and id
    """

    def __init__(self, project=None, entity=None, step=None, task=None, workfile=None, user=None):
        """
        Guarantes that provided entites are fully populated from database
        :param project:
        :param entity:
        :param step:
        :param task:
        :param workfile:
        :param user:
        """
        kt = ktrack_api.get_ktrack()
        # project
        self._validate_entity_dict(project)
        if project:
            self._project = kt.find_one('project', project['id'])
        else:
            self._project = None

        # entity
        self._validate_entity_dict(entity)
        if entity:
            self._entity = kt.find_one(entity['type'], entity['id'])
        else:
            self._entity = None

        # step
        self._validate_step(step)
        self._step = step

        # task
        self._validate_entity_dict(task)
        if task:
            self._task = kt.find_one('task', task['id'])
        else:
            self._task = None

        # workfile
        self._validate_entity_dict(workfile)
        if workfile:
            self._workfile = kt.find_one('workfile', workfile['id'])
        else:
            self._workfile = None

        # user
        self._validate_entity_dict(user)
        if user:
            self._user = kt.find_one('user', user['id'])
        else:
            self._user = None
