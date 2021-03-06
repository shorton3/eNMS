from requests import get
from requests.auth import HTTPBasicAuth

from tests.test_base import check_blueprints


@check_blueprints('/automation')
def payload_transfer_workflow(user_client):
    result = get(
        'http://192.168.105.2:5000/rest/run_job/payload_transfer_workflow',
        headers={'Accept': 'application/json'},
        auth=HTTPBasicAuth('admin', 'admin')
    ).json()['results']
    assert result['success'] and len(result) == 9


@check_blueprints('/automation')
def netmiko_workflow(user_client):
    result = get(
        'http://192.168.105.2:5000/rest/run_job/Netmiko_VRF_workflow',
        headers={'Accept': 'application/json'},
        auth=HTTPBasicAuth('admin', 'admin')
    ).json()['results']
    assert not result['success'] and len(result) == 7


@check_blueprints('/automation')
def napalm_workflow(user_client):
    result = get(
        'http://192.168.105.2:5000/rest/run_job/Napalm_VRF_workflow',
        headers={'Accept': 'application/json'},
        auth=HTTPBasicAuth('admin', 'admin')
    ).json()['results']
    assert not result['success'] and len(result) == 7
