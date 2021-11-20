import logging
from django.views.generic import TemplateView

import uptrace


logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trace_url"] = uptrace.trace_url()
        return context


class HelloView(TemplateView):
    template_name = "hello.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trace_url"] = uptrace.trace_url()
        return context


class FailingView(TemplateView):
    template_name = "hello.html"

    def get_context_data(self, **kwargs):
        print(uptrace.trace_url())
        raise ValueError("something went wrong")
