import logging


class BaseService:
    """Service基类"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
