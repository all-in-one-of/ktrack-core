"""
Module providing path <-> Context functionality.
Sometimes we need to get the context from a path, for example the project from the current working directory.
For this, every folder created and deleted needs to be registered/unregistered in the database.
We store the path in the database together with the given context and can get the original context back with context_from_path
"""
import ktrack_api
from kttk.context import Context


def register_path(path, context):
    # type: (str, Context) -> dict
    """
    registeres given context for given path in database, so we can later get the context back from the path
    :param path: path to register, None or "" not allowed!!!
    :param context: context to register
    :return: newly created path entry from database
    """
    # check if path is valid
    if not is_valid_path(path):
        raise ValueError(path)

    # make path beautifull
    path = __good_path(path)

    kt = ktrack_api.get_ktrack()

    path_entry_data = {}
    path_entry_data["path"] = path
    path_entry_data["context"] = context.as_dict()  # todo remove user information

    return kt.create("path_entry", path_entry_data)


def unregister_path(path):
    # type: (str) -> None
    """
    Unregisters a path from database
    :param path:
    :return: True if path was registered in database and deleted, False otherwise
    """
    # make path beautifull
    path = __good_path(path)

    kt = ktrack_api.get_ktrack()

    path_entries = kt.find("path_entry", [["path", "is", path]])

    entry_found = len(path_entries) > 0

    if entry_found:
        for path_entry in path_entries:
            kt.delete("path_entry", path_entry["id"])
        return True
    else:
        return False


def context_from_path(path):
    # type: (str) -> kttk.context.Context
    """
    Extracts context by path from database
    :param path: path for context
    :return: stored context if exists, else None
    """
    # make path beautifull
    path = __good_path(path)

    kt = ktrack_api.get_ktrack()

    context_dicts = kt.find("path_entry", [["path", "is", path]])
    context_found = len(context_dicts) > 0

    if context_found:
        context = Context.from_dict(context_dicts[0]["context"])
        return context
    else:
        return None


def is_valid_path(path):
    """
    Checks if the path can be registered in the database.
    Path is not allowed to be None or empty Strng
    :param path: path to check
    :return: True if path is valid, False otherwise
    """
    valid = False

    if path:
        if len(path) > 0:
            valid = True

    return valid


def __good_path(path):
    # type: (str) -> str
    """
    Makes os paths good, replace \\ with /
    :param path:
    :return:
    """
    path = path.replace("\\", "/")
    path = path.replace("//", "/")
    return path
