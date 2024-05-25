from collections import defaultdict, deque
from constants.enums import LRRetCode

class LinkedRoles():
    def __init__(self, linked_roles_dict: None | dict[int, list[int]] = None) -> None:
        if linked_roles_dict == None:
            linked_roles_dict = {}
        self._linked_roles: dict[int, set[int]] = {
            int(target): set(int(r) for r in req) for target, req in linked_roles_dict.items()
            }
        self.update_reverse_linked_roles()

    
    def __contains__(self, other) -> bool:
        return other in self._linked_roles

    def __len__(self) -> int:
        return len(self._linked_roles)


    def get(self, tarrget_id) -> set[int]:
        return self._linked_roles.get(tarrget_id, set())

    
    def update_reverse_linked_roles(self) -> None:
        """Sets the reverse Version of the linkedroles as a dictionary, where each key is a req and the values are sets of target roles
        """
        tmp = defaultdict(set)
        for target, req in self._linked_roles.items():
            for r in req:
                tmp[r].add(target)
        self._reverse_linked_roles: dict[int, set[int]] = tmp

    
    def get_targets_for_req(self, req_id: int) -> set[int]:
        return self._reverse_linked_roles.get(req_id, set())
    

    def get_all_targets_for_reqs(self, *req_ids: int) -> set[int]:
        """Returns a set with all roles a user should have for given roles

        Returns:
            set[int]: The set with all ids for roles the user should have
        """
        if not req_ids:
            return set()
        roles_to_check = set(req_ids) - set(self._linked_roles) #remove all targets from reqs, as reqs could be missing
        all_roles = roles_to_check.copy()

        while roles_to_check:
            new_roles = set()
            for role in roles_to_check:
                new_roles |= self.get_targets_for_req(role)
            roles_to_check = new_roles - all_roles
            all_roles |= roles_to_check
        return all_roles
    
    
    def is_circular(self, target_id: int, *req_ids: int) -> bool:
        roles = set(req_ids)
        if target_id in roles:
            return True
        
        # if the new target is no req and the new reqs are not yet reqs for other targets -> not circular
        if target_id not in self._reverse_linked_roles and not roles.intersection(set(self._linked_roles)):
            return False
        
        all_reqs = roles | self._linked_roles.get(target_id, set()) # all reqs, new and old
        MAX_ITERATION = 1000
        current_it = 0
        visited_roles = set()
        roles_to_check = deque([target_id])
        while roles_to_check:
            if current_it > MAX_ITERATION:
                return True # if too many iteration -> circular
            current_it += 1
            role = roles_to_check.pop()
            visited_roles.add(role)
            new_roles = self._reverse_linked_roles[role] - visited_roles
            if new_roles.intersection(all_reqs):
                return True
            roles_to_check.extendleft(new_roles)

        return False

    
    def add_link_to_target(self, target_id: int, *req_ids: int) -> LRRetCode:
        if self.is_circular(target_id, *req_ids):
            return LRRetCode.FAIL_CIRCULAR 
        new_reqs = set(req_ids)
        if target_id in self._linked_roles:
            self._linked_roles[target_id] |= new_reqs
        else:
            self._linked_roles[target_id] = new_reqs
        self.update_reverse_linked_roles()
        return LRRetCode.SUCCESS
    

    def remove_link_from_target(self, target_id: int, *req_ids: int, update_reverse: bool = True) -> None:
        """Removes link(s) from a target role, if no links specified, remove target

        Args:
            target_id (int): The target to remove or remove links
            req_ids (int): The link(s) that should be removed
            update_reverse (bool, optional): If the reverse_lr should be updated after. Defaults to True.
        """
        if target_id not in self._linked_roles:
            return
        
        if not req_ids:
            self._linked_roles.pop(target_id, set())

        else:
            roles_to_remove = set(req_ids)
            self._linked_roles[target_id] -= roles_to_remove
            if not self._linked_roles[target_id]:
                self._linked_roles.pop(target_id, set())

        if update_reverse:
            self.update_reverse_linked_roles()

    
    def remove_role(self, role_id: int) -> None:
        """Called when a role gets deleted to remove all links for that role, if any

        Args:
            role_id (int): The deleted role
        """
        self.remove_link_from_target(role_id, update_reverse=False)

        for target in self._reverse_linked_roles.get(role_id, set()):
            self.remove_link_from_target(target, role_id, update_reverse=False)

        self.update_reverse_linked_roles()


    # The JSON format for the linked roles object
    def serialize(self) -> dict[int, list[int]]:
        return {target: list(reqs) for target, reqs in self._linked_roles.items()}