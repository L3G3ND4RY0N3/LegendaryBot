import pytest
from pathlib import Path
from utils.structs.LinkedRoles import LinkedRoles
from constants.enums import LRRetCode


def test_len_of_empty_LinkedRoles():
    lr = LinkedRoles()
    assert lr.__len__() == 0


def test_get_from_empty_LinkedRoles():
    lr = LinkedRoles()
    expected = set()
    assert lr.get(1) == expected
    assert lr.get(100) == expected
    assert lr.get(200) == expected
    assert lr.get("7") == expected


def test_adding_single_link():
    lr = LinkedRoles()
    assert lr.add_link_to_target(1, 2) == LRRetCode.SUCCESS
    assert lr.add_link_to_target(2, 3) == LRRetCode.SUCCESS
    assert lr.add_link_to_target(4, 5) == LRRetCode.SUCCESS
    assert lr.add_link_to_target(2, 2) == LRRetCode.FAIL_CIRCULAR
    assert lr.add_link_to_target(3, 2) == LRRetCode.FAIL_CIRCULAR
    assert lr.add_link_to_target(3, 1) == LRRetCode.FAIL_CIRCULAR


def test_get_single_target_role():
    lr = LinkedRoles({1: [2, 3, 4]})
    expected = set([2, 3, 4])
    assert lr.get(1) == expected
    assert lr.get(2) == set()
    assert lr.get("3") == set()