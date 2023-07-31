from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Listing, Watchlist, Comment,BiddingLogg

from .models import User, Category

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    query = request.GET.get('query')
    price_filter = request.GET.get('price_filter')
    sort_by = request.GET.get('sort_by')
    listings_photo = request.GET.get('show_with_photo')
    no_bidders = request.GET.get('no_bidders')
    active_listings = request.GET.get('active_listings')

    listings = Listing.objects.all()

    if query:
        listings = listings.filter(title__icontains=query)

    if price_filter:
        if price_filter == '0-100':
            listings = listings.filter(starting_price__range=(0, 100))
        elif price_filter == '101-200':
            listings = listings.filter(starting_price__range=(101, 200))
        elif price_filter == '201-300':
            listings = listings.filter(starting_price__range=(201, 300))
        elif price_filter == '300+':
            listings = listings.filter(starting_price__gte=300)

    if sort_by == 'price_high_low':
        listings = listings.order_by('-starting_price')
    elif sort_by == 'price_low_high':
        listings = listings.order_by('starting_price')
    elif sort_by == 'titleAZ':
        listings = listings.order_by('title')

    if no_bidders:
        listings = listings.exclude(highest_bidder__isnull=False)

    if listings_photo:
        listings = listings.exclude(image_url='')

    if active_listings:
        listings = listings.exclude(closed=True)

    paginator = Paginator(listings, 100)
    page = request.GET.get('page')
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)

    return render(request, 'auctions/index.html', {
        'listings': listings,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/login')

    return _wrapped_view


@login_required
def create_listing(request):
    categories = Category.objects.all()
    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')
        starting_price = request.POST.get('starting_price')
        image_url = request.POST.get('image_url')
        category_id = request.POST.get('category')

        listing = Listing(
            title=title,
            description=description,
            starting_price=starting_price,
            current_price=starting_price,
            image_url=image_url,
            creator=request.user
        )
        listing.save()

        if category_id:
            listing.categories.add(category_id)

        return redirect('/')

    return render(request, 'create_listing.html', {'categories': categories})


@login_required
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    user_watchlist.listings.add(listing)
    return redirect('/')


@login_required
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    user_watchlist.listings.remove(listing)
    return redirect('/watchlist/')


@login_required
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    comments = listing.comments.all()

    if request.method == 'POST':
        # if bidding
        if 'bid_amount' in request.POST:
            bid_amount = float(request.POST.get('bid_amount'))
            if bid_amount >= listing.starting_price and bid_amount > listing.current_price:
                listing.current_price = bid_amount
                listing.highest_bidder = request.user
                listing.save()
                logs = BiddingLogg(
                    user=request.user,
                    listing1=listing,
                    bid_amount=bid_amount,
                )
                logs.save()
            else:
                error_message = "Invalid bid amount. The bid must be at least as large as the starting bid and " \
                                "greater than any other bids placed."
                return render(request, 'listing_detail.html',
                              {'listing': listing, 'comments': comments, 'error_message': error_message})

        # if commenting
        elif 'text' in request.POST:
            text = request.POST.get('text')
            if text.strip():
                comment = Comment.objects.create(listing=listing, user=request.user, text=text)
                comment.save()
                return redirect('listing_detail', listing_id=listing.id)

    return render(request, 'listing_detail.html', {'listing': listing, 'comments': comments})


@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if request.user == listing.creator:
        listing.closed = True
        listing.save()

    return redirect('listing_detail', listing_id=listing.id)


@login_required
def my_listings(request):
    user_listings = Listing.objects.filter(creator=request.user)
    return render(request, 'my_listings.html', {'user_listings': user_listings})


@login_required
def list_watchlist(request):
    user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    watchlist_listings = user_watchlist.listings.all()
    return render(request, 'watchlist.html', {'watchlist_listings': watchlist_listings})


def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if listing.creator == request.user:
        listing.delete()
    return redirect('my_listings')


@login_required
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')

        category = Category(name=name)
        category.save()

        return redirect('/create_category')

    categories = Category.objects.all()
    return render(request, 'create_category.html', {'categories': categories})


@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        category.delete()

    return redirect('create_category')


@login_required
def add_comment_to_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if request.method == 'POST':
        text = request.POST.get('text')
        if text.strip():  # Ensure the comment is not empty
            comment = Comment.objects.create(listing=listing, user=request.user, text=text)
            comment.save()
            return redirect('listing_detail', listing_id=listing.id)

    return redirect('listing_detail', listing_id=listing.id)


@login_required
def list_category(request, category_id):
    cat = get_object_or_404(Category, id=category_id)
    listings = Listing.objects.filter(categories=category_id)
    return render(request, 'categories_list.html', {'category': cat, 'listings': listings})


@login_required
def my_profile(request):
    user = request.user
    return render(request, 'my_profile.html', {'user': user})
