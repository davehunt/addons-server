from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

import jingo
import jinja2

from . import forms


@jingo.register.function
def SimpleSearchForm(request, search_cat):
    data = request.GET
    if search_cat and 'cat' not in request.GET:
        data = dict(request.GET, cat=search_cat)
    return forms.SimpleSearchForm(data)


@jingo.register.function
def showing(query, pager):
    """Writes a string that tells the user what they are seeing in terms of
    search results."""
    format_opts = (pager.start_index(), pager.end_index(),
                   pager.paginator.count,)
    query = escape(query)

    if query:
        showing = _(u'Showing {0} - {1} of {2} results for '
                    '<strong>{3}</strong>').format(*(format_opts + (query,)))
    else:
        showing = _(u'Showing {0} - {1} of {2} results').format(*format_opts)

    return jinja2.Markup(showing)
