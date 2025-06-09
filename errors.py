class InsufficientBalanceError(Exception):
    """Исключение, возникающее при попытке превышения нулевого баланса."""
    def __init__(self, message="You exceeded your current quota, please check your plan and billing details."):
        self.message = message
        super().__init__(self.message)


