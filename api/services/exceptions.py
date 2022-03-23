class AuctionRequestException(Exception):
    """
    Should be raised if an exception occurs while calling the Carfirst dealer/auction API.
    """

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"AuctionRequestException, {self.message}"
        else:
            return "AuctionRequestException: Failed to fetch the results."
