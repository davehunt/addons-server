# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from pages.desktop.base import Base


class Login(Base):

    _email_locator = (By.ID, 'id_username')
    _continue_locator = (By.CSS_SELECTOR, '#normal-login .login-source-button')

    def login(self, email, password):
        self.find_element(*self._email_locator).send_keys(email)
        self.find_element(*self._continue_locator).click()
        from fxapom.pages.sign_in import SignIn
        sign_in = SignIn(self.selenium)
        # TODO wait for sign in page to load
        self.wait.until(lambda s: self.is_element_displayed(
            *sign_in._email_input_locator))
        sign_in.login_password = password
        sign_in.click_sign_in()
        self.wait.until(lambda s: self.logged_in)
