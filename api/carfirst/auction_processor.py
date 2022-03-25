from datetime import datetime
from glob import glob
import json
import os
from typing import Any, Dict, List, Text

from carfirst.models import Auction, Bid


class AuctionProcessor:
    """Process for auction files."""

    def process_upcoming_auctions(self):
        files = glob("data/upcoming_auctions/unprocessed/upcoming_auctions-*.json")
        print(f"Processing {len(files)} files")
        for file in files:
            try:
                self.process_auction_file(file)
                self._move_to_processed_directory(file)
            except Exception as ex:
                # TODO
                self._move_to_failed_directory(file)
                print(ex)

    def process_live_auctions(self):
        files = glob("data/live_auctions/unprocessed/live_auctions-*.json")
        print(f"Processing {len(files)} files")
        for file in files:
            try:
                self.process_auction_file(file)
                self._move_to_processed_directory(file)
            except Exception as ex:
                # TODO
                self._move_to_failed_directory(file)
                print(ex)

    def _move_to_processed_directory(self, path: Text):
        new_path = path.replace("unprocessed", "processed")
        directory = os.path.split(new_path)[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        os.rename(path, new_path)

    def _move_to_failed_directory(self, path: Text):
        new_path = path.replace("unprocessed", "failed")
        directory = os.path.split(new_path)[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        os.rename(path, new_path)

    def process_auction_file(self, path):
        print(f"Processing file: {path}")
        file = open(path, "r")
        json_dict: Dict[Text, Any] = json.load(file)
        auctions: List[Dict[Text, Any]] = json_dict.get("auctions", [])
        if len(auctions) == 0:
            return

        auction_ids: List[Text] = [auction["id"] for auction in auctions]
        auctions_to_update: List[Auction] = Auction.objects.filter(
            auction_id__in=auction_ids
        ).all()
        auction_ids_to_update = {
            auction.auction_id: auction for auction in auctions_to_update
        }

        new_auctions: List[Auction] = []
        for auction_dict in auctions:
            if auction_dict["id"] not in auction_ids_to_update:
                new_auction = self._create_auction(auction_dict)
                new_auctions.append(new_auction)
            else:
                self._update_auction(
                    auction_ids_to_update[auction_dict["id"]], auction_dict
                )

            bids: List[Any] = auction_dict.get("bids", [])
            if len(bids) > 0:
                self._process_bids(auction_dict)

        print(f"Processed {len(new_auctions)} auctions.")

        if len(new_auctions) > 0:
            Auction.objects.bulk_create(new_auctions)

    def _create_auction(self, auction: Dict[Text, Any]):
        new_auction = Auction()
        new_auction.auction_id = auction.get("id")
        start_time_int: int = auction.get("start") / 1000
        new_auction.start_time = datetime.fromtimestamp(start_time_int)
        end_time_int: int = auction.get("end") / 1000
        new_auction.end_time = datetime.fromtimestamp(end_time_int)
        new_auction.title = auction.get("title")
        new_auction.subtitle = auction.get("subtitle")[0]
        new_auction.start_price = auction.get("start_price")
        new_auction.bids_placed = auction.get("bids_placed")
        new_auction.bidders = auction.get("bidders")

        bids: List[Dict[Text, Any]] = auction.get("bids", [])
        if len(bids) > 0:
            new_auction.highest_bid = bids[0].get("amount")

        sections: List[Dict] = auction.get("details", {}).get("sections", [])
        items: List[Dict[Text, Any]] = [
            section.get("items", [])
            for section in sections
            if section.get("id") == "highlights"
        ][0]
        items_dict: Dict[Text, Text] = {
            item.get("label", {}).get("text"): item.get("values")[0].get("text")
            for item in items
        }

        new_auction.reference_id = items_dict.get("Reference ID")
        new_auction.location = items_dict.get("Pick-up location")
        new_auction.registered_city = items_dict.get("Registered city")
        new_auction.color = items_dict.get("Color")
        new_auction.transmission_type = items_dict.get("Transmission")
        new_auction.fuel_type = items_dict.get("Fuel type")
        new_auction.registration_year = items_dict.get("Registration year")

        groups: List[Dict[Text, Any]] = [
            section.get("groups", [])
            for section in sections
            if section.get("id") == "features"
        ][0]

        car_details = [detail for detail in groups if detail.get("id") == "carDetails"][
            0
        ]["items"]

        details_dict = {
            detail.get("label").split(":")[0]: detail.get("label").split(":")[1].strip()
            for detail in car_details
        }
        new_auction.make = details_dict.get("Make")
        new_auction.model = details_dict.get("Model")
        new_auction.mileage = int(details_dict.get("Mileage"))
        return new_auction

    def _update_auction(self, auction: Auction, auction_dict: Dict[Text, Any]):
        auction.bids_placed = max(
            auction_dict.get("bids_placed", 0), auction.bids_placed or 0
        )
        auction.bidders = max(auction_dict.get("bidders", 0), auction.bidders or 0)

        bids: List[Dict[Text, Any]] = auction_dict.get("bids", [])
        if len(bids) > 0:
            auction.highest_bid = max(
                auction.highest_bid or 0, bids[0].get("amount", 0)
            )

        auction.save()

    def _process_bids(self, auction: Dict[Text, Any]):
        """Process bids in an auction."""
        auction_id: Text = auction.get("id")
        bids: List[Dict[Text, Any]] = auction.get("bids", [])
        if len(bids) == 0:
            return

        for bid in bids:
            bidder = bid.get("user")
            amount = bid.get("amount")
            bid_time = datetime.fromtimestamp(bid.get("created_at") / 1000)
            bid_dict = {
                "auction_id": auction_id,
                "bidder": bidder,
                "amount": amount,
                "bid_time": bid_time,
            }
            Bid.objects.update_or_create(
                auction_id=auction_id, bidder=bidder, amount=amount, defaults=bid_dict
            )


auction_processor = AuctionProcessor()
