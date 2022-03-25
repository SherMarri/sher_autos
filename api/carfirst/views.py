from django.http import HttpRequest, JsonResponse
from carfirst.carfirst_bidding_aggregator import bidding_aggregator
from carfirst.auction_processor import auction_processor


def download_upcoming_auctions(request: HttpRequest):
    try:
        bidding_aggregator.fetch_upcoming_auctions()
        return JsonResponse(
            {"success": True, "message": "Upcoming auctions downloaded successfully."}
        )
    except Exception as ex:
        exception_message = str(ex)
        return JsonResponse(
            {
                "success": False,
                "message": f"Failed to download upcoming auctions. Exception: {exception_message}",
            },
            status=500,
        )


def download_live_auctions(request: HttpRequest):
    try:
        bidding_aggregator.fetch_live_auctions()
        return JsonResponse(
            {"success": True, "message": "Live auctions downloaded successfully."}
        )
    except Exception as ex:
        exception_message = str(ex)
        return JsonResponse(
            {
                "success": False,
                "message": f"Failed to download live auctions. Exception: {exception_message}",
            },
            status=500,
        )


def process_upcoming_auctions(request: HttpRequest):
    try:
        auction_processor.process_upcoming_auctions()
        return JsonResponse(
            {"success": True, "message": "Upcoming auctions processed successfully."}
        )
    except Exception as ex:
        exception_message = str(ex)
        return JsonResponse(
            {
                "success": False,
                "message": f"Failed to process upcoming auctions. Exception: {exception_message}",
            },
            status=500,
        )


def process_live_auctions(request: HttpRequest):
    try:
        auction_processor.process_live_auctions()
        return JsonResponse(
            {"success": True, "message": "Live auctions processed successfully."}
        )
    except Exception as ex:
        exception_message = str(ex)
        return JsonResponse(
            {
                "success": False,
                "message": f"Failed to process live auctions. Exception: {exception_message}",
            },
            status=500,
        )
