import datetime
import os
import shutil
import urlparse

from fxapom.fxapom import DEV_URL, PROD_URL, FxATestAccount
from mozdownload import FactoryScraper
import mozinstall
import jwt
import pytest
import requests


@pytest.fixture
def capabilities(request, capabilities):
    driver = request.config.getoption('driver')
    if capabilities.get('browserName', driver).lower() == 'firefox':
        # In order to run these tests in Firefox 48, marionette is required
        capabilities['marionette'] = True
    return capabilities


@pytest.fixture
def fxa_account(base_url):
    url = DEV_URL if 'dev' in base_url else PROD_URL
    return FxATestAccount(url)


@pytest.fixture(scope='session')
def jwt_issuer(base_url, variables):
    try:
        hostname = [urlparse.urlsplit(base_url).hostname]
        return variables['api'][hostname]['jwt_issuer']
    except KeyError:
        return os.getenv('JWT_ISSUER')


@pytest.fixture(scope='session')
def jwt_secret(base_url, variables):
    try:
        hostname = [urlparse.urlsplit(base_url).hostname]
        return variables['api'][hostname]['jwt_secret']
    except KeyError:
        return os.getenv('JWT_SECRET')


@pytest.fixture
def jwt_token(base_url, jwt_issuer, jwt_secret):
    payload = {
        'iss': jwt_issuer,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)}
    return jwt.encode(payload, jwt_secret, algorithm='HS256')


@pytest.fixture
def user(base_url, fxa_account, jwt_token):
    user = {
        'email': fxa_account.email,
        'password': fxa_account.password,
        'username': fxa_account.email.split('@')[0]}
    url = '{base_url}/api/v3/accounts/super-create/'.format(base_url=base_url)
    params = {
        'email': user['email'],
        'username': user['username'],
        'password': user['password'],
        'fxa_id': fxa_account.session.uid}
    headers = {'Authorization': 'JWT {token}'.format(token=jwt_token)}
    r = requests.post(url, data=params, headers=headers)
    assert requests.codes.created == r.status_code
    user.update(r.json())
    return user


@pytest.yield_fixture(scope='session')
def firefox_path(request, tmpdir_factory, firefox_path):
    if firefox_path is not None:
        yield firefox_path
    else:
        cache_path = request.config.cache.makedir('firefox')
        scraper = FactoryScraper(
            'release',
            version='latest-beta',
            destination=str(cache_path))
        download_path = scraper.download()
        print('Firefox downloaded to: {0}'.format(download_path))
        tmpdir = tmpdir_factory.mktemp('firefox')
        install_path = mozinstall.install(download_path, str(tmpdir))
        print('Firefox installed at: {0}'.format(install_path))
        yield mozinstall.get_binary(install_path, 'Firefox')
        shutil.rmtree(str(tmpdir))


@pytest.fixture
def discovery_pane_url(base_url):
    if 'localhost' in base_url:
        return None
    elif 'dev' in base_url:
        return 'https://discovery.addons-dev.allizom.org/'
    elif 'allizom' in base_url:
        return 'https://discovery.addons.allizom.org/'
    else:
        return 'https://discovery.addons.mozilla.org/'
