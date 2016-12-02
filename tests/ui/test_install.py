from foxpuppet.browser.notifications import (
    AddOnInstallComplete,
    AddOnInstallConfirmation,
    AddOnInstallRestart)
import pytest

from pages.desktop.addon import AddOn


@pytest.mark.nondestructive
@pytest.mark.firefox_arguments('-foreground')
def test_install_extension(base_url, selenium, firefox):
    """Install an extension that requires a restart"""
    page = AddOn(selenium, base_url, name='downthemall').open()
    page.click_add_to_firefox()
    firefox.wait_for_notification(AddOnInstallConfirmation).install()
    firefox.wait_for_notification(AddOnInstallRestart).close()


@pytest.mark.nondestructive
@pytest.mark.firefox_arguments('-foreground')
def test_install_restartless_extension(base_url, selenium, firefox):
    """Install an extension that does not require a restart"""
    page = AddOn(selenium, base_url, name='adblock-plus').open()
    page.click_add_to_firefox()
    firefox.wait_for_notification(AddOnInstallConfirmation).install()
    firefox.wait_for_notification(AddOnInstallComplete).close()
