from django.urls import path
from carfirst.views import (
    download_upcoming_auctions,
    download_live_auctions,
    process_live_auctions,
    process_upcoming_auctions,
)

urlpatterns = [
    path(
        "download_upcoming_auctions",
        download_upcoming_auctions,
        name="carfirst_download_upcoming_auctions",
    ),
    path(
        "download_live_auctions",
        download_live_auctions,
        name="carfirst_download_live_auctions",
    ),
    path(
        "process_upcoming_auctions",
        process_upcoming_auctions,
        name="carfirst_process_upcoming_auctions",
    ),
    path(
        "process_live_auctions",
        process_live_auctions,
        name="carfirst_process_live_auctions",
    ),
]
