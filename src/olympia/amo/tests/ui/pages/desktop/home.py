# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from selenium.webdriver.common.by import By

from base import Base


class Home(Base):

    _promo_box_locator = (By.ID, 'promos')

    def wait_for_page_to_load(self):
        promo_box = self.find_element(*self._promo_box_locator)
        self.wait.until(lambda s: promo_box.size['height'] == 271)
