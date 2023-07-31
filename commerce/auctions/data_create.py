# create_data.py
import os
import random
import string
import django
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
# Set up Django environment
django.setup()

from auctions.models import User, PageVisited, BiddingLogg
from auctions.models import Listing, Category


def generate_random_string(length=6):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_price():
    return round(random.randint(10, 5000), 2)


def take_random_id(start, finnish):
    return round(random.randint(start, finnish))


def create_categories():
    for i in range(20):
        name = f"Category {i + 1}"
        Category.objects.create(name=name)
    print("Categories created successfully.")


def create_users():
    for i in range(100):
        username = f"user{i + 1}"
        password = "admin"
        email = "test@test.com"
        user = User.objects.create_user(username, email, password)
        user.save()
    print("Users created successfully.")


def create_listings():
    categories = Category.objects.all()
    users = User.objects.all()

    for i in range(10000):
        title = f"Title{i + 1}"
        description = generate_random_string(100)
        starting_price = generate_random_price()
        current_price = starting_price
        image_url = f"https://www.shutterstock.com/image-vector/hot-sale-promotion-label-tag-illustration-1410327293"
        category = random.choice(categories)
        creator = random.choice(users)

        listing = Listing.objects.create(
            title=title,
            description=description,
            starting_price=starting_price,
            current_price=current_price,
            image_url=image_url,
            creator=creator,

        )
        listing.categories.add(category)

    print("Listings created successfully.")


def create_logs():
    for i in range(take_random_id(5, 20)):
        user = random.choice(User.objects.all())
        for i in range(take_random_id(5, 40)):
            listing = random.choice(Listing.objects.all())
            if listing.creator != user:
                path = "/listing/" + str(listing.id)
                PageVisited.objects.create(user=user, path=path)
    print("Visit logs created")


def create_bid_logs():
    for i in range(take_random_id(5, 20)):
        user = random.choice(User.objects.all())
        for i in range(take_random_id(1, 5)):
            listing = random.choice(Listing.objects.all())
            min_price = listing.current_price
            if user != listing.creator:
                for i in range(take_random_id(5, 15)):
                    BiddingLogg.objects.create(user=user, listing1=listing, bid_amount=min_price + 2 * i)
                listing.current_price = min_price + 2 * i
                listing.highest_bidder = user
                listing.save()

    print("Bidding logs created")


def count_entities():
    print("The database contains:")
    print(str(User.objects.all().count()) + " Users")
    print(str(Listing.objects.all().count()) + " Listings")
    print(str(Category.objects.all().count()) + " Categories")
    print(str(PageVisited.objects.all().count()) + " Logs for visits")
    print(str(BiddingLogg.objects.all().count()) + " Logs for bids")


if __name__ == "__main__":
    create_categories()
    create_users()
    create_listings()
    create_logs()
    create_bid_logs()
    count_entities()
