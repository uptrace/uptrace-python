import logging
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from opentelemetry import trace
import uptrace

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        try:
            User.objects.get(id=1)
        except Exception as exc:
            span = trace.get_current_span()
            if span.is_recording():
                span.record_exception(exc)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))

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
