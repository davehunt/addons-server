# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pages.desktop.home import Home


def test_login(base_url, selenium, user):
    """User can login"""
    page = Home(selenium, base_url).open()
    assert not page.logged_in
    page.login(user['email'], user['password'])
    assert page.logged_in


def test_logout(base_url, selenium, user):
    """User can logout"""
    page = Home(selenium, base_url).open()
    page.login(user['email'], user['password'])
    page.logout()
    assert not page.logged_in


def test_home(base_url, selenium):
    assert Home(selenium, base_url).open().header.root is not None
