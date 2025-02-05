import pytest
from django.utils import timezone
from iam.models import User, Workspace, WorkspaceTransferConfirmation, Role, Permission, Collaborator


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User",
        user_type="Other"
    )


@pytest.fixture
def test_user_collaborator(db):
    return User.objects.create_user(
        email="collaborator@example.com",
        password="password123",
        first_name="Collaborator",
        last_name="User",
        user_type="Other"
    )


@pytest.fixture
def test_user_limited(db):
    return User.objects.create_user(
        email="inactive@example.com",
        password="password123",
        first_name="Inactive",
        last_name="User",
        user_type="Other",
        is_ownership_allowed=False
    )


@pytest.fixture
def test_user_inactive(db):
    return User.objects.create_user(
        email="inactive@example.com",
        password="password123",
        first_name="Inactive",
        last_name="User",
        user_type="Other",
        is_active=False
    )


@pytest.fixture
def test_user_admin(db):
    return User.objects.create_superuser(
        email="admin@example.com",
        password="password123",
        first_name="Admin",
        last_name="User",
        user_type="Other"
    )


@pytest.fixture
def test_user_staff(db):
    return User.objects.create_user(
        email="admin@example.com",
        password="password123",
        first_name="Admin",
        last_name="User",
        user_type="Other",
        is_staff=True
    )


@pytest.fixture
def test_workspace_public(db, test_user):
    return Workspace.objects.create(
        name="Public",
        owner=test_user,
        private=False
    )


@pytest.fixture
def test_workspace_private(db, test_user):
    return Workspace.objects.create(
        name="Private",
        owner=test_user,
        private=True
    )


@pytest.fixture
def test_workspace_transfer(db, test_workspace_private, test_user_collaborator):
    return WorkspaceTransferConfirmation.objects.create(
        workspace=test_workspace_private,
        new_owner=test_user_collaborator,
        initiated=timezone.now()
    )


@pytest.fixture
def test_role_shared(db):
    return Role.objects.create(
        name="Shared",
        description="Shared",
        workspace=None
    )


@pytest.fixture
def test_role_editor(db, test_workspace_private):
    role = Role.objects.create(
        name="Editor",
        description="Editor",
        workspace=test_workspace_private
    )

    Permission.objects.create(
        role=role,
        permission_type="*",
        resource_type="*",
    )

    return role


@pytest.fixture
def test_role_viewer(db, test_workspace_private):
    role = Role.objects.create(
        name="Viewer",
        description="Viewer",
        workspace=test_workspace_private
    )

    Permission.objects.create(
        role=role,
        permission_type="view",
        resource_type="*",
    )

    return role


@pytest.fixture
def test_collaborator_shared(db, test_user_collaborator, test_role_shared):
    return Collaborator.objects.create(
        workspace=test_role_shared.workspace,
        role=test_role_shared,
        user=test_user_collaborator
    )


@pytest.fixture
def test_collaborator_editor(db, test_user_collaborator, test_role_editor):
    return Collaborator.objects.create(
        workspace=test_role_editor.workspace,
        role=test_role_editor,
        user=test_user_collaborator
    )


@pytest.fixture
def test_collaborator_viewer(db, test_user_collaborator, test_role_viewer):
    return Collaborator.objects.create(
        workspace=test_role_viewer.workspace,
        role=test_role_viewer,
        user=test_user_collaborator
    )
