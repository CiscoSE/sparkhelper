from unittest import TestCase
import sparkhelper
import json

class MembershipTestCases(TestCase):
    def test_get_membership_org_id_list_a_value(self):
        with open('membership_true.json') as json_data:
            d = json.load(json_data)
        result = sparkhelper.get_membership_org_id_list(d)

        self.assertIsNotNone(d,'test_get_membership_org_id_list_a_value should return a value')

    def test_get_membership_org_id_list(self):
        with open('membership_true.json') as json_data:
            d = json.load(json_data)
        membership_items = sparkhelper.get_membership_org_id_list(d)
        org_list = ["orgID123",
                    "orgID123"]

        self.assertTrue(set(membership_items)==set(org_list),'TestGet_membership_org_id_list should return correct list')

    def test_orgs_are_in_allowed_org_list_returns_a_value(self):
        with open('membership_true.json') as json_data:
            d = json.load(json_data)

        result = sparkhelper.orgs_are_in_allowed_org_list(["orgID123","orgID124"],d)

        self.assertIsNotNone(result,'test_orgs_are_in_allowed_org_list_returns_a_value should return a value')

    def test_orgs_are_in_allowed_org_list_returns_true(self):
        with open('membership_true.json') as json_data:
            d = json.load(json_data)

        membership_items = sparkhelper.get_membership_org_id_list(d)
        result = sparkhelper.orgs_are_in_allowed_org_list(["orgID123", "orgID123"], d)
        self.assertTrue(result,
                        'test_orgs_are_in_allowed_org_list_returns_true should return True')

    def test_orgs_are_in_allowed_org_list_returns_false(self):
        with open('membership_false.json') as json_data:
            d = json.load(json_data)

        result = sparkhelper.orgs_are_in_allowed_org_list(["orgID123", "orgID123"], d)
        self.assertFalse(result,
                        'test_orgs_are_in_allowed_org_list_returns_false should return False')


    def test_orgs_are_in_allowed_list_works_with_string(self):
        with open('membership_true.json') as json_data:
            d = json.load(json_data)

        membership_items = sparkhelper.get_membership_org_id_list(d)
        result = sparkhelper.orgs_are_in_allowed_org_list("orgID123", d)
        self.assertTrue(result,
                        'test_orgs_are_in_allowed_list_works_with_string should work when a string is passed rather than a list')