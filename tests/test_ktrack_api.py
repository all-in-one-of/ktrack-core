import pytest
from ktrack_api.Exceptions import EntityMissing, EntityNotFoundException
from ktrack_api.mongo_impl.entities import Project
from ktrack_api.mongo_impl.ktrack_mongo_impl import KtrackMongoImpl

SOME_OTHER_OBJECT_ID = "507f1f77bcf86cd799439011"

SOME_OBJECT_ID = "507f1f77bcf86cd799439012"


@pytest.fixture
def ktrack_instance():
    return KtrackMongoImpl('mongomock://localhost')


def test_create(ktrack_instance):
    # type: (KtrackMongoImpl) -> None

    # create not existing entity
    with pytest.raises(EntityMissing):
        entity = ktrack_instance.create('projectaersrdtz')

    # test create existing entity
    entity = ktrack_instance.create('project')

    assert entity is not None

    assert type(entity) == dict

    assert entity['type'] == 'project'

    assert 'id' in entity.keys()

    entity_in_db = len(Project.objects(id=entity['id']))

    assert entity_in_db


def test_update(ktrack_instance):
    # type: (KtrackMongoImpl) -> None

    # update not existing entity type
    with pytest.raises(EntityMissing):
        entity = ktrack_instance.update("projectaser", "aaaaaaaa", {})

    # update entity with useless id

    with pytest.raises(EntityNotFoundException):
        entity = ktrack_instance.update("project", SOME_OTHER_OBJECT_ID, {})

    # now test real update
    entity = ktrack_instance.create("project")

    thumbnail_dict = {'type': 'thumbnail', 'id': SOME_OBJECT_ID}

    ktrack_instance.update("project", entity['id'], {'thumbnail': thumbnail_dict})

    # now check if update was correct
    # get entity from db
    entity_in_db = Project.objects(id=entity['id'])

    # check that we have at least one entity
    assert len(entity_in_db) > 0

    entity = entity_in_db[0]

    # now check if values are correctly updated
    assert entity.thumbnail['type'] == 'thumbnail'
    assert entity.thumbnail['id'] == SOME_OBJECT_ID


def test_delete(ktrack_instance):
    # type: (KtrackMongoImpl) -> None

    # test to delete not existing entity type
    with pytest.raises(EntityMissing):
        ktrack_instance.delete("<agt<eydrzuyaerz", SOME_OBJECT_ID)

    # test delete with not existing entity id
    with pytest.raises(EntityNotFoundException):
        ktrack_instance.delete('project', SOME_OBJECT_ID)

    # create entity to delete
    entity = ktrack_instance.create("project")

    entity_in_db = Project.objects(id=entity['id'])
    assert len(entity_in_db) > 0

    ktrack_instance.delete('project', entity['id'])

    # now check if object was deleted
    entity_in_db = Project.objects(id=entity['id'])
    assert len(entity_in_db) == 0


def test_find(ktrack_instance):
    # type: (KtrackMongoImpl) -> None

    # test to find not existing entity type
    with pytest.raises(EntityMissing):
        ktrack_instance.find("<agt<eydrzuyaerz", SOME_OBJECT_ID)

    ktrack_instance.create("shot", {'project': {'type': 'project', 'id': SOME_OBJECT_ID}})

    entities = ktrack_instance.find('shot', [['project', 'is', {'type': 'project', 'id': SOME_OBJECT_ID}]])

    assert len(entities) == 1


def test_find_one(ktrack_instance):
    # type: (KtrackMongoImpl) -> None

    # test to delete not existing entity type
    with pytest.raises(EntityMissing):
        ktrack_instance.find_one("<agt<eydrzuyaerz", SOME_OBJECT_ID)

    # test delete with not existing entity id
    with pytest.raises(EntityNotFoundException):
        ktrack_instance.find_one('project', SOME_OBJECT_ID)

    # create one object

    entity = ktrack_instance.create('project')

    _entity = ktrack_instance.find_one('project', entity['id'])

    assert entity['id'] == _entity['id']
