import pytest

from kttk.context import Context


@pytest.fixture
def populated_context():
    return Context(project={'name': 'my_project'},
                   entity={'type': 'asset', 'code': 'my_entity', 'asset_type': 'prop'},
                   step={'name': 'step'},
                   task={'name': 'task'},
                   workfile={'name': 'workfile', 'path': 'some_path', 'comment': 'awesome', 'version_number': 1},
                   user={'name': 'user'})


def test_creation(populated_context):
    # type: (Context) -> None
    assert populated_context.project['name'] == 'my_project'
    assert populated_context.entity['code'] == 'my_entity'
    assert populated_context.step['name'] == 'step'
    assert populated_context.task['name'] == 'task'
    assert populated_context.workfile['name'] == 'workfile'
    assert populated_context.user['name'] == 'user'


def test_context_as_dict(populated_context):
    # type: (Context) -> None

    context_dict = populated_context.as_dict()

    assert context_dict['project'] == populated_context.project
    assert context_dict['entity'] == populated_context.entity
    assert context_dict['step'] == populated_context.step
    assert context_dict['task'] == populated_context.task
    assert context_dict['workfile'] == populated_context.workfile
    assert context_dict['user'] == populated_context.user


def test_context_from_dict():
    context_dict = {}
    context_dict['project'] = {'name': 'project'}
    context_dict['entity'] = {'code': 'my_entity'}
    context_dict['step'] = {'name': 'step'}
    context_dict['task'] = {'name': 'task'}
    context_dict['workfile'] = {'name': 'workfile'}
    context_dict['user'] = {'name': 'user'}

    context = Context.from_dict(context_dict)

    assert context.project == {'name': 'project'}
    assert context.entity == {'code': 'my_entity'}
    assert context.step == {'name': 'step'}
    assert context.task == {'name': 'task'}
    assert context.workfile == {'name': 'workfile'}
    assert context.user == {'name': 'user'}


def test_serialize_deserialize(populated_context):
    # type: (Context) -> None

    context_serialized = populated_context.serialize()

    context = Context.deserialize(context_serialized)

    assert context.project == populated_context.project
    assert context.entity == populated_context.entity
    assert context.step == populated_context.step
    assert context.task == populated_context.task
    assert context.workfile == populated_context.workfile
    assert context.user == populated_context.user


def test_repesentation(populated_context):
    # type: (Context) -> None

    representation = populated_context.__repr__()


def test_get_avaible_tokens(populated_context):
    # type: (Context) -> None
    tokens = populated_context.get_avaible_tokens()

    assert tokens['project_name'] == 'my_project'
    assert tokens['code'] == 'my_entity'
    assert tokens['asset_type'] == 'prop'
    assert tokens['step'] == 'step'
    assert tokens['task_name'] == 'task'
    assert tokens['user_name'] == 'user'
    assert tokens['version'] == 'v001'
