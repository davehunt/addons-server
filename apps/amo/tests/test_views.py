import urllib

from django import http, test
from amo.urlresolvers import reverse

from mock import patch, Mock
from nose.tools import eq_
import test_utils

from amo.pyquery_wrapper import PyQuery
from stats.models import SubscriptionEvent


def test_404_no_app():
    """Make sure a 404 without an app doesn't turn into a 500."""
    # That could happen if helpers or templates expect APP to be defined.
    url = reverse('amo.monitor')
    response = test.Client().get(url + 'nonsense')
    eq_(response.status_code, 404)


class TestStuff(test_utils.TestCase):
    fixtures = ['base/addons', 'base/global-stats', 'base/configs']

    def test_data_anonymous(self):
        def check(expected):
            response = self.client.get('/', follow=True)
            anon = PyQuery(response.content)('body').attr('data-anonymous')
            eq_(anon, expected)

        check('true')
        self.client.login(username='admin@mozilla.com', password='password')
        check('false')

    def test_my_account_menu(self):
        def check(expected):
            response = self.client.get('/', follow=True)
            account = PyQuery(response.content)('ul.account')
            tools = PyQuery(response.content)('ul.tools')
            eq_(account.size(), expected)
            eq_(tools.size(), expected)

        check(0)
        self.client.login(username='admin@mozilla.com', password='password')
        check(1)

    def test_heading(self):
        def title_eq(url, expected):
            response = self.client.get(url, follow=True)
            actual = PyQuery(response.content)('#title').text()
            eq_(expected, actual)

        title_eq('/firefox', 'Add-ons for Firefox')
        title_eq('/thunderbird', 'Add-ons for Thunderbird')
        title_eq('/mobile', 'Mobile Add-ons for Firefox')

    def test_xenophobia(self):
        def box_is_checked(locale='en-US', cookie_val=None):
            if cookie_val is not None:
                self.client.cookies['locale-only'] = cookie_val
            elif 'locale-only' in self.client.cookies:
                del self.client.cookies['locale-only']

            response = self.client.get("/%s/firefox/" % locale)
            doc = PyQuery(response.content)
            return doc("#locale-only").attr('checked')

        def cookie_box(xeno, locale='en-US'):
            if 'locale-only' in self.client.cookies:
                del self.client.cookies['locale-only']

            xeno = 'locale-only=1&' if xeno else ''

            response = self.client.get("/%s/firefox/?%slang=%s&next=/" % (
                    locale, xeno, locale), follow=True)
            doc = PyQuery(response.content)
            box = PyQuery(response.content)('#locale-only').attr('checked')
            cookie = self.client.cookies.get("locale-only")

            if cookie:
                cookie = int(cookie.value)
            return (box, cookie)

        assert box_is_checked(cookie_val=1), ("True cookie does not show "
                "checked box for /en-US/.")
        assert box_is_checked('ja', cookie_val=1), ("True cookie does not "
                "show checked box for /ja/.")
        assert not box_is_checked(cookie_val=0), ("False cookie does show "
                "checked box for /en-US/.")
        assert not box_is_checked('ja', cookie_val=0), ("False cookie does "
                "show checked box for /ja/.")
        assert not box_is_checked(), "Empty cookie does is checked for en-US."
        assert box_is_checked('ja'), "Empty cookie is not checked for ja."

        eq_(('checked', 1), cookie_box(True))
        eq_((None, 0), cookie_box(False))
        eq_(('checked', 1), cookie_box(True, 'ja'))
        eq_((None, 0), cookie_box(False, 'ja'))

    def test_login_link(self):
        r = self.client.get(reverse('home'), follow=True)
        doc = PyQuery(r.content)
        next = urllib.urlencode({'to': '/en-US/firefox/'})
        eq_('/en-US/firefox/users/login?%s' % next,
            doc('#aux-nav p a')[1].attrib['href'])


class TestPaypal(test_utils.TestCase):

    def setUp(self):
        self.url = reverse('amo.paypal')

    def urlopener(self, status):
        m = Mock()
        m.readline.return_value = status
        return m

    @patch('amo.views.urllib2.urlopen')
    def test_not_verified(self, urlopen):
        urlopen.return_value = self.urlopener('xxx')
        response = self.client.post(self.url)
        assert isinstance(response, http.HttpResponseForbidden)

    @patch('amo.views.urllib2.urlopen')
    def test_no_payment_status(self, urlopen):
        urlopen.return_value = self.urlopener('VERIFIED')
        response = self.client.post(self.url)
        eq_(response.status_code, 200)

    @patch('amo.views.urllib2.urlopen')
    def test_subscription_event(self, urlopen):
        urlopen.return_value = self.urlopener('VERIFIED')
        response = self.client.post(self.url, {'txn_type': 'subscr_xxx'})
        eq_(response.status_code, 200)
        eq_(SubscriptionEvent.objects.count(), 1)

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        eq_(response.status_code, 405)
