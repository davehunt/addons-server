import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.ui import WebDriverWait as Wait
import pytest

from pages.desktop.addon import AddOn


@pytest.mark.nondestructive
@pytest.mark.firefox_arguments('-foreground')
def test_install_extension(base_url, selenium):
    """Install an extension that requires a restart"""
    page = AddOn(selenium, base_url, name='downthemall').open()
    page.click_add_to_firefox()
    # with firefox.addon_install_confirmation_notification as notification:
    #     notificaton.accept()
    # with firefox.addon_install_restart_notification as notification:
    #     assert 'will be installed after you restart' in notification.label
    #     notification.close()

    with selenium.context('chrome'):
        notification = Wait(selenium, 10).until(
            expected.presence_of_element_located((
                By.ID, 'addon-install-confirmation-notification')))
        time.sleep(10)  # TODO replace with a wait (https://bugzil.la/1094246)
        notification.find_element(
            By.ID, 'addon-install-confirmation-accept').click()
        time.sleep(10)  # TODO replace with a wait (https://bugzil.la/1094246)
        notification = Wait(selenium, 10).until(
            expected.presence_of_element_located((
                By.ID, 'addon-install-restart-notification')))
        assert 'will be installed after you restart' in \
            notification.get_attribute('label')
        # TODO close popup notification (http://bit.ly/1P4S6g8)


@pytest.mark.nondestructive
@pytest.mark.firefox_arguments('-foreground')
def test_install_restartless_extension(base_url, selenium):
    """Install an extension that does not require a restart"""
    page = AddOn(selenium, base_url, name='adblock-plus').open()
    page.click_add_to_firefox()
    # with firefox.addon_install_confirmation_notification as notification:
    #     notificaton.accept()
    # with firefox.addon_install_complete_notification as notification:
    #     assert 'has been installed successfully' in notificaton.label
    #     notification.close()

    with selenium.context('chrome'):
        notification = Wait(selenium, 10).until(
            expected.presence_of_element_located((
                By.ID, 'addon-install-confirmation-notification')))
        time.sleep(10)  # TODO replace with a wait (https://bugzil.la/1094246)
        notification.find_element(
            By.ID, 'addon-install-confirmation-accept').click()
        time.sleep(10)  # TODO replace with a wait (https://bugzil.la/1094246)
        notification = Wait(selenium, 10).until(
            expected.presence_of_element_located((
                By.ID, 'addon-install-complete-notification')))
        assert 'has been installed successfully' in \
            notification.get_attribute('label')
        # TODO close popup notification (http://bit.ly/1P4S6g8)
