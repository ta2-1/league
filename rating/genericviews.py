

from django.views.generic import ListView, DetailView


class ExtraContextMixin(object):
    def get_context_data(self, **kwargs):
        context = super(ExtraContextMixin, self).get_context_data(**kwargs)
        extra_context = self.kwargs.get("extra_context", {})
        context.update(extra_context)
        return context


class ListViewWithExtraContext(ExtraContextMixin, ListView):
    pass


class DetailedWithExtraContext(ExtraContextMixin, DetailView):
    pass
