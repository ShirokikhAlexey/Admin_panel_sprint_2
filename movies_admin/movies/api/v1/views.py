from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.core.paginator import InvalidPage
from django.http import JsonResponse, Http404
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        return (
            self.model
                .objects
                .annotate(actors=ArrayAgg('people__full_name',
                                          filter=Q(personfilmwork__role='actor'), distinct=True))
                .annotate(writers=ArrayAgg('people__full_name',
                                           filter=Q(personfilmwork__role='writer'), distinct=True))
                .annotate(directors=ArrayAgg('people__full_name',
                                             filter=Q(personfilmwork__role='director'), distinct=True))
                .annotate(genres=ArrayAgg('genre__name', distinct=True))
                .order_by('id')

        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class Movies(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset().values('id', 'title', 'description', 'creation_date',
                                              'rating', 'type', 'actors',
                                              'directors', 'writers', 'genres')
        count, total, prev, next, result = self.paginate_queryset(queryset, self.paginate_by)

        context = {
            "count": count,
            "total_pages": total,
            "prev": prev,
            "next": next,
            'results': list(result)
        }
        return context

    def paginate_queryset(self, queryset, page_size):
        """Paginate the queryset, if needed."""
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404()
        try:
            page = paginator.page(page_number)
            if page.has_next():
                _next = page.next_page_number()
            else:
                _next = None

            if page.has_previous():
                prev = page.previous_page_number()
            else:
                prev = None

            return paginator.count, paginator.num_pages, prev, _next, page.object_list
        except InvalidPage as e:
            raise Http404()


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return self.get_object(self.get_queryset()
                               .values('id', 'title', 'description', 'creation_date',
                                       'rating', 'type', 'actors',
                                       'directors', 'writers', 'genres'))
