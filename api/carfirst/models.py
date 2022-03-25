from django.db import models


class Auction(models.Model):
    """Represents an auction in Carfirst"""

    auction_id = models.CharField(max_length=128, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(max_length=128)
    subtitle = models.CharField(max_length=128)
    start_price = models.IntegerField()
    highest_bid = models.IntegerField(null=True, blank=True)
    bids_placed = models.IntegerField()
    bidders = models.IntegerField()
    location = models.CharField(max_length=128)
    registered_city = models.CharField(max_length=128)
    mileage = models.IntegerField()
    color = models.CharField(max_length=128)
    make = models.CharField(max_length=128)
    model = models.CharField(max_length=128)
    transmission_type = models.CharField(max_length=128)
    fuel_type = models.CharField(max_length=128)
    registration_year = models.IntegerField()
    reference_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Bid(models.Model):
    """Represents a bid in auction"""

    auction_id = models.CharField(max_length=128)
    bidder = models.CharField(max_length=128)
    amount = models.IntegerField()
    bid_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
