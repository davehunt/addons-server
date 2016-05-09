from selenium.webdriver.common.by import By

from base import Base


class AddOn(Base):

    URL_TEMPLATE = '{locale}/{product}/addon/{name}'

    _add_to_firefox_locator = (By.CSS_SELECTOR, '#addon .installer.button')

    def click_add_to_firefox(self):
        self.find_element(*self._add_to_firefox_locator).click()
