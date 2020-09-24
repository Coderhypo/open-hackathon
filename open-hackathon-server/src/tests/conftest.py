import pytest

from hackathon.constants import VE_PROVIDER, TEMPLATE_STATUS
from hackathon.hmongo.models import User, Template, UserHackathon, Hackathon


@pytest.fixture(scope="class")
def user1():
    # return new user named one
    one = User(
        name="test_one",
        nickname="test_one",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=False)
    one.set_password("test_password")
    one.save()
    return one


@pytest.fixture(scope="class")
def user2():
    # return new user named two
    two = User(
        name="test_two",
        nickname="test_two",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=False)
    two.set_password("test_password")
    two.save()
    return two


@pytest.fixture(scope="class")
def admin1():
    # return new admin named one
    admin_one = User(
        name="admin_one",
        nickname="admin_one",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=True)
    admin_one.set_password("test_password")
    admin_one.save()
    return admin_one


@pytest.fixture(scope="class")
def hackathon1(user1):
    new_hack = Hackathon(
        name="hackathon1",
        display_name="hackathon for test",
    )
    new_hack.save()

    admin = UserHackathon(user=user1,
                          hackathon=new_hack,
                          remark='creator')
    admin.save()
    return new_hack


@pytest.fixture(scope="class")
def default_template(user1):
    tmpl = Template(
        name="test_default_template",
        provider=VE_PROVIDER.DOCKER,
        status=TEMPLATE_STATUS.UNCHECKED,
        description="old_desc",
        content="",
        template_args={},
        docker_image="ubuntu",
        network_configs=[],
        virtual_environment_count=0,
        creator=user1,
    )
    tmpl.save()
    return tmpl
