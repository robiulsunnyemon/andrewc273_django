from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import Throttled

class AIUsageThrottle(UserRateThrottle):
    rate = '3/day'

    def wait(self):
        return super().wait()

    def throttle_failure(self):
        raise Throttled(detail="You can only use AI 3 times per day")