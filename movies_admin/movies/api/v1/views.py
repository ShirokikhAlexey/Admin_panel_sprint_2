from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from django.core.paginator import Paginator, InvalidPage

from movies.models import FilmWork

PAGINATE_BY = 50


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

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset().values('id', 'title', 'description', 'creation_date',
                                              'rating', 'type', 'actors',
                                              'directors', 'writers', 'genres')

        paginator = Paginator(queryset, per_page=PAGINATE_BY)

        page_kwarg = self.page_kwarg
        page_param = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1

        try:
            page_number = int(page_param)
        except ValueError:
            if page_param == 'last':
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
        except InvalidPage as e:
            raise Http404()

        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": prev,
            "next": _next,
            'results': page.object_list
        }
        return context

    def render_to_response(self, context, **response_kwargs):
        context['results'] = list(context['results'])
        return JsonResponse(context)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return self.get_object(self.get_queryset()
                               .values('id', 'title', 'description', 'creation_date',
                                       'rating', 'type', 'actors',
                                       'directors', 'writers', 'genres'))
