import pytest
from utils.structs.LinkedRoles import LinkedRoles
from constants.enums import LRRetCode
import json


@pytest.fixture()
def json_file() -> dict[int, list[int]]:
    with open("tests/json/LinkedRoleTest.json", "r") as file:
        lr_dict = json.load(file)
    return lr_dict


def test_len_of_empty_LinkedRoles() -> None:
    lr = LinkedRoles()
    assert lr.__len__() == 0


def test_get_from_empty_LinkedRoles() -> None:
    lr = LinkedRoles()
    expected = set()
    assert lr.get(1) == expected
    assert lr.get(100) == expected
    assert lr.get(200) == expected
    assert lr.get("7") == expected


def test_adding_single_link() -> None:
    lr = LinkedRoles()
    assert lr.add_link_to_target(1, 2) == LRRetCode.SUCCESS
    assert lr.add_link_to_target(2, 3) == LRRetCode.SUCCESS
    assert lr.add_link_to_target(4, 5) == LRRetCode.SUCCESS
    assert lr.add_link_to_target(2, 2) == LRRetCode.FAIL_CIRCULAR
    assert lr.add_link_to_target(3, 2) == LRRetCode.FAIL_CIRCULAR
    assert lr.add_link_to_target(3, 1) == LRRetCode.FAIL_CIRCULAR


def test_get_single_target_role() -> None:
    lr = LinkedRoles({1: [2, 3, 4]})
    expected = set([2, 3, 4])
    assert lr.get(1) == expected
    assert lr.get(2) == set()
    assert lr.get("3") == set()


def test_get_targets_for_req() -> None:
    lr = LinkedRoles({1: [2, 3], 5: [2, 6], 9: [2, 4], 12: [6, 11]})
    assert lr.get_targets_for_req(2) == set([1, 5, 9])
    assert lr.get_targets_for_req(6) == set([5, 12])
    assert lr.get_targets_for_req(4) == set([9])
    assert lr.get_targets_for_req(15) == set()


def test_get_all_targets() -> None:
    lr = LinkedRoles({1: [2], 3: [1], 5: [3], 7: [5], 12: {10, 11}})
    assert lr.get_all_targets_for_reqs(2) == set([1, 2, 3, 5, 7])
    assert lr.get_all_targets_for_reqs(5) == set() #since requirement for 5 is missing
    assert lr.get_all_targets_for_reqs(3) == set() #since requirement for 3 is missing
    assert lr.get_all_targets_for_reqs(2, 3) == set([1, 2, 3, 5, 7])
    assert lr.get_all_targets_for_reqs(999) == set([999]) #since it is not a linked role
    assert lr.get_all_targets_for_reqs() == set()
    assert lr.get_all_targets_for_reqs(10, 11) == set([10, 11, 12])
    assert lr.get_all_targets_for_reqs(2, 10) == set([1, 2, 3, 5, 7, 10, 12])


def test_linked_roles_from_json(json_file) -> None:
    lr = LinkedRoles(json_file)
    assert lr.get(9) == set([8])
    assert lr.get(2) == set([5, 7])
    assert lr.get(1) == set([2, 3, 4])
    assert lr.get_all_targets_for_reqs(5) == set([1, 2, 5])
    assert lr.get_all_targets_for_reqs(7) == set([1, 2, 7])
    assert lr.get_all_targets_for_reqs(5, 7, 8) == set([1, 2, 5, 7, 8, 9])