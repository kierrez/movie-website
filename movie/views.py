from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, F
from django.contrib import messages
from .models import *
from .forms import EditRating
from utils.utils import paginate
import datetime
import calendar
import re
from django.views.generic import View


def home(request):
    # manager for getting user's ratings
    # show others ratings maybe
    all_movies = Title.objects.filter(rating__user=request.user, type__name='movie')
    all_series = Title.objects.filter(rating__user=request.user, type__name='series')
    context = {
        'ratings': Title.objects.all()[:10],
        'info': {
            'last_movie': all_movies[0],
            'last_series': all_series[0] if all_series else None,
            'last_good': all_movies.filter(rating__rate__gte=5)[0],
            'movie_count': all_movies.count(),
            'series_count': all_series.count(),
            # 'search_movies': reverse('explore') + '?select_type=movie&q=',
            # 'search_series': reverse('explore') + '?select_type=series&q=',
        }
    }
    return render(request, 'home.html', context)


def explore(request):
    # if request.method == 'POST':
    #     if not request.user.is_superuser:
    #         messages.info(request, 'Only admin can do this', extra_tags='alert-info')
    #         return redirect(reverse('explore'))
    #
    #     choosen_obj = get_object_or_404(Title, const=request.POST.get('const'))
    #     if 'watch' in request.POST.keys():
    #         choosen_obj.watch_again_date = datetime.datetime.now()
    #     elif 'unwatch' in request.POST.keys():
    #         choosen_obj.watch_again_date = None
    #     choosen_obj.save(update_fields=['watch_again_date'])
    #     return redirect(request.META.get('HTTP_REFERER'))
    entries = Title.objects.all()
    query = request.GET.get('q')
    selected_type = request.GET.get('select_type')
    if selected_type in 'movie series'.split():
        # entries = entries.filter(Q(type_id=Type.objects.get(name=selected_type).id))
        entries = entries.filter(Q(type__name=selected_type))
    if query:
        if len(query) > 2:
            entries = entries.filter(Q(name__icontains=query) | Q(year=query)).distinct()
        else:
            entries = entries.filter(Q(name__startswith=query) | Q(year=query)).distinct()

    page = request.GET.get('page')
    ratings = paginate(entries, page)

    query_string = ''
    if query and selected_type:
        select_type = '?select_type={}'.format(selected_type)
        q = '&q={}'.format(query)
        query_string = select_type + q + '&page='

    context = {
        'ratings': ratings,
        'query': query,
        'selected_type': selected_type,
        'query_string': query_string,
    }
    return render(request, 'entry.html', context)
#
#
# def book(request):
#     return render(request, 'book.html')
#
#
# def search(request):
#     return render(request, 'search.html')
#
#
# def about(request):
#     return render(request, 'about.html')
#
#
def entry_details(request, slug):
    requested_obj = get_object_or_404(Title, slug=slug)
    if request.method == 'GET':
        context = {
            'entry': requested_obj,
            'archive': Rating.objects.filter(title=requested_obj, user=request.user),
            # 'link_month': reverse('entry_show_rated_in_month',
            #                       kwargs={'year': requested_obj.rate_date.year, 'month': requested_obj.rate_date.month})
        }
        return render(request, 'entry_details.html', context)
#
#     if request.method == 'POST':
#         if not request.user.is_superuser:
#             messages.info(request, 'Only admin can edit', extra_tags='alert-info')
#             return redirect(requested_obj)
#
#         keys = request.POST.keys()  # todo not a fan of this. its bcs I used btn and value is '', maybe add value
#         if any(x in keys for x in ['watch', 'unwatch']):
#             if 'watch' in keys:
#                 requested_obj.watch_again_date = datetime.datetime.now()
#             elif 'unwatch' in keys:
#                 requested_obj.watch_again_date = None
#             requested_obj.save(update_fields=['watch_again_date'])
#         elif any(x in keys for x in ['fav_add', 'fav_remove']):
#             if 'fav_add' in keys:
#                 Favourite.objects.create(const=requested_obj.const, order=Favourite.objects.all().count() + 1)
#             elif 'fav_remove' in keys:
#                 to_delete = Favourite.objects.get(const=requested_obj.const)
#                 Favourite.objects.filter(order__gt=to_delete.order).update(order=F('order') - 1)
#                 to_delete.delete()
#         return redirect(reverse('entry_details', kwargs={'slug': slug}))
#
#
# def entry_edit(request, slug):
#     requested_obj = get_object_or_404(Title, slug=slug)
#     if not request.user.is_superuser:
#         messages.info(request, 'Only admin can edit', extra_tags='alert-info')
#         return redirect(requested_obj)
#
#     form = EditRating(instance=Rating.objects.filter(user=request.user, title=requested_obj))
#     if request.method == 'POST':
#         form = EditRating(request.POST)
#         if form.is_valid():
#             new_rate = form.cleaned_data.get('rate')
#             new_date = form.cleaned_data.get('rate_date')
#             # message = ''
#             # if requested_obj.rating_set.first() != int(new_rate):
#             #     message += 'rating: {} changed for {}'.format(requested_obj.rate, new_rate)
#             #     requested_obj.rate = new_rate
#             # if requested_obj.rate_date != new_date:
#             #     message += ', ' if message else ''
#             #     message += 'date: {} changed for {}'.format(requested_obj.rate_date, new_date)
#             #     requested_obj.rate_date = new_date
#             # if message:
#             #     messages.success(request, message, extra_tags='alert-success')
#             # else:
#             #     messages.info(request, 'nothing changed', extra_tags='alert-info')
#             # requested_obj.save(update_fields=['rating__rate', 'rating__rate_date'])
#             return redirect(requested_obj)
#     context = {
#         'form': form,
#         'entry': requested_obj,
#     }
#     return render(request, 'entry_edit.html', context)


def entry_details_redirect(request, const):
    requested_obj = get_object_or_404(Title, const=const)
    return redirect(requested_obj)


def entry_groupby_year(request):
    context = {
        'year_count': Title.objects.values('year').annotate(the_count=Count('year')).order_by('-year'),
    }
    return render(request, 'entry_groupby_year.html', context)


def entry_groupby_genre(request):
    context = {
        'genre': Genre.objects.all().annotate(num=Count('title')).order_by('-num'),  # todo, genre.set all?
    }
    return render(request, 'entry_groupby_genre.html', context)


def entry_groupby_director(request):
    context = {
        'director': Director.objects.filter(title__type__name='movie').annotate(num=Count('title')).order_by('-num')[:50],
    }
    return render(request, 'entry_groupby_director.html', context)


def entry_show_from_year(request, year):
    # entries = Title.objects.filter(year=year).order_by('-rate', '-rate_imdb', '-votes')
    entries = Title.objects.filter(year=year)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': year,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_rated_in_month(request, year, month):
    entries = Rating.objects.filter(user=request.user, rate_date__year=year, rate_date__month=month)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': '{} {}'.format(calendar.month_name[int(month)], year),
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_genre(request, genre):
    entries = Genre.objects.get(name=genre).title_set.all()
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': genre,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_rate(request, rate):
    entries = Title.objects.filter(rating__user=request.user, rating__rate=rate)
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': rate,
    }
    return render(request, 'entry_show_from.html', context)


def entry_show_from_director(request, pk):
    entries = Director.objects.get(id=pk).title_set.all()
    page = request.GET.get('page')
    ratings = paginate(entries, page)
    context = {
        'ratings': ratings,
        'title': Director.objects.get(id=pk).name,
    }
    return render(request, 'entry_show_from.html', context)


# def watchlist(request):
#     if request.method == 'GET':
#         context = {
#             # 'ratings': Title.objects.filter(watch_again_date__isnull=True).order_by('-rate_date'),todo isnull problem
#             'ratings': [e for e in Title.objects.all() if e.watch_again_date],
#             # 'history': Archive.objects.filter(watch_again_date__isnull=False),
#             'title': 'See again'
#         }
#         return render(request, 'watchlist.html', context)
#
#     if request.method == 'POST':
#         if not request.user.is_superuser:
#             messages.info(request, 'Only admin can do this', extra_tags='alert-info')
#             return redirect(reverse('watchlist'))
#         choosen_obj = get_object_or_404(Title, const=request.POST.get('const'))
#         if request.POST.get('unwatch'):
#             choosen_obj.watch_again_date = None
#         choosen_obj.save()
#         return redirect(reverse('watchlist'))
#
#
# def imdb_watchlist(request):
#     if request.method == 'GET':
#         context = {
#             'seen': ImdbWatchlist.objects.seen(),
#             'not_seen': ImdbWatchlist.objects.not_seen(),
#             'delete': ImdbWatchlist.objects.to_delete(),
#             'title': 'IMDb Watchlist'
#         }
#         return render(request, 'imdb_watchlist.html', context)
#
#     if request.method == 'POST':
#         if not request.user.is_superuser:
#             messages.info(request, 'Only admin can do this', extra_tags='alert-info')
#             return redirect(reverse('imdb_watchlist'))
#         readd, delete = request.POST.get('watchlist_readd'), request.POST.get('watchlist_del')
#         choosen_obj = get_object_or_404(ImdbWatchlist, const=readd or delete)
#         if delete:
#             choosen_obj.set_to_delete = True
#             messages.info(request, '{} has been deleted from the watchlist'.format(choosen_obj.name))
#         elif readd:
#             choosen_obj.set_to_delete = False
#             messages.info(request, '{} has been restored to the watchlist'.format(choosen_obj.name))
#         choosen_obj.save(update_fields=['set_to_delete'])
#         return redirect(reverse('imdb_watchlist'))
#
#
# def favourite(request):
#     if request.method == 'POST':
#         item_order = request.POST.get('item_order')
#         if item_order:
#             item_order = re.findall('tt\d{7}', item_order)
#             print('new_order', item_order)
#             for new_position, item in enumerate(item_order, 1):
#                 Favourite.objects.filter(const=item).update(order=new_position)
#     context = {
#         'ratings': [(fav.order, fav.get_entry) for fav in Favourite.objects.all().order_by('order')],
#     }
#     return render(request, 'favourite.html', context)