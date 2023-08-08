import string
import uuid
import random

from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Listing, Watchlist, Comment, BiddingLogg, PageVisited

from .models import User, Category

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    query = request.GET.get('query')
    price_filter = request.GET.get('price_filter')
    sort_by = request.GET.get('sort_by')
    listings_photo = request.GET.get('show_with_photo')
    no_bidders = request.GET.get('no_bidders')
    active_listings = request.GET.get('active_listings')
    user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)

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

    slider_items = Listing.objects.all().order_by('-id')[:3]
    return render(request, 'auctions/index.html', {
        'listings': listings, 'slider_items': slider_items
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


def generate_random_string(length=6):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_price():
    return round(random.randint(10, 5000), 2)


def take_random_id(start, finnish):
    return round(random.randint(start, finnish))


def create_categories(num_categories):
    for i in range(num_categories):
        name = f"Category {i + 1}"
        Category.objects.create(name=name)
    return "Categories created successfully."


def create_users(num_users):
    existing_usernames = set(User.objects.values_list('username', flat=True))
    for i in range(num_users):
        username = None
        while not username or username in existing_usernames:
            username = f"user_{uuid.uuid4().hex[:10]}"
        existing_usernames.add(username)

        password = "admin"
        email = f"user{i + 1}@test.com"
        user = User.objects.create_user(username, email, password)
        user.save()
    return "Users created successfully."


def create_listings(num_listings, img_link):
    categories = Category.objects.all()
    users = User.objects.all()

    for i in range(num_listings):
        title = f"Title{i + 1}"
        description = generate_random_string(100)
        starting_price = generate_random_price()
        current_price = starting_price
        # image_url = f"data:image/jpeg;base64,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"
        category = random.choice(categories)  # Use 'random.choice()' from the 'random' module
        creator = random.choice(users)  # Use 'random.choice()' from the 'random' module

        listing = Listing.objects.create(
            title=title,
            description=description,
            starting_price=starting_price,
            current_price=current_price,
            image_url=img_link,
            creator=creator,
        )
        listing.categories.add(category)

    return "Listings created successfully."


def create_logs(num_logs):
    users = User.objects.all()
    listings = Listing.objects.all()
    for i in range(num_logs):
        user = random.choice(users)
        for j in range(take_random_id(5, 40)):
            listing = random.choice(listings)
            if listing.creator != user:
                path = "/listing/" + str(listing.id)
                try:
                    PageVisited.objects.create(user=user, path=path)
                except Exception as e:
                    print(f"Error creating log: {e}")
    return "Visit logs created."


def create_bid_logs(num_bid_logs):
    users = User.objects.all()
    listings = Listing.objects.all()
    for i in range(num_bid_logs):
        user = random.choice(users)
        for j in range(take_random_id(1, 5)):
            listing = random.choice(listings)
            min_price = listing.current_price
            if user != listing.creator:
                for k in range(take_random_id(5, 15)):
                    try:
                        BiddingLogg.objects.create(user=user, listing1=listing, bid_amount=min_price + 2 * k)
                    except Exception as e:
                        print(f"Error creating bid log: {e}")
                listing.current_price = min_price + 2 * k
                listing.highest_bidder = user
                listing.save()

    return "Bidding logs created."


def count_entities():
    entities_count = []
    entities_count.append(str(User.objects.all().count()) + " Users")
    entities_count.append(str(Listing.objects.all().count()) + " Listings")
    entities_count.append(str(Category.objects.all().count()) + " Categories")
    entities_count.append(str(PageVisited.objects.all().count()) + " Logs for visits")
    entities_count.append(str(BiddingLogg.objects.all().count()) + " Logs for bids")
    return "\n".join(entities_count)


def create_entities(request):
    if request.method == 'POST':
        num_categories = request.POST.get('num_categories')
        num_users = request.POST.get('num_users')
        num_listings = request.POST.get('num_listings')
        num_logs = request.POST.get('num_logs')
        num_bid_logs = request.POST.get('num_bid_logs')
        img_link = request.POST.get('img_link')

        result = []
        if num_categories.isdigit() and int(num_categories) > 0:
            result.append(create_categories(int(num_categories)))

        # Check if num_users is a non-empty string and a valid integer
        if num_users.isdigit() and int(num_users) > 0:
            result.append(create_users(int(num_users)))

        if num_listings.isdigit() and int(num_listings) > 0:
            result.append(create_listings(int(num_listings), img_link))

        if num_logs.isdigit() and int(num_logs) > 0:
            result.append(create_logs(int(num_logs)))

        if num_bid_logs.isdigit() and int(num_bid_logs) > 0:
            result.append(create_bid_logs(int(num_bid_logs)))

        entities_count = count_entities()
        result.append(entities_count)

        return HttpResponse("\n".join(result))

    return render(request, 'create_entities.html')
