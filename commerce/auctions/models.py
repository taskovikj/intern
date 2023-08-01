from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    highest_bidder = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name='highest_bids')
    closed = models.BooleanField(default=False)
    image_url = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.listing.title}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField('Listing', related_name='watchlist_listings')

    def __str__(self):
        return f"{self.user.username}'s Watchlist"


class PageVisited(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    # session_start = models.DateTimeField()
    # session_finnish = models.DateTimeField()


class BiddingLogg(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing1 = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
