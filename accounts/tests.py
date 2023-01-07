from django.test import TestCase


# Testing GitHub Actions
class GitHubActionsGoodCase(TestCase):
    def test_account(self):
        str1 = "good"
        self.assertEqual(str1, "good")


class GitHubActionsBadCase(TestCase):
    def test_account(self):
        str1 = "fixed"
        self.assertEqual(str1, "fixed")

