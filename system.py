from math import sqrt


WALK_SPEED = 5
RIDE_SPEED = 20
SEARCH_RADIUS = 1
MAX_TIME = 20

MAP = { 
    'PLACE1': (0, 0),
    'PLACE2': (10, 1),
    'PLACE3': (-5, 10)
}


def argmin(arr, key=lambda x: True):
    min_val, min_id = None, None
    for i, v in enumerate(arr):
        if not key(v):
            continue
        elif min_val is None:
            min_val = v
            min_id = i
        elif v < min_val:
            min_val = v
            min_id = i
    return min_id


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xy = (x, y)
    
    def distance_to(self, other):
        return sqrt((self.x - other.x) ** 2 +
                    (self.y - other.y) ** 2)


class Order:
    def __init__(self, start_pos, end_pos, max_price, max_time):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.max_price = max_price
        self.max_time = max_time
        self.length = start_pos.distance_to(end_pos)

    def set_timings(self, start_time, duration):
        self.start_time = start_time
        self.duration = duration
        self.end_time = start_time + duration

    def time_left(self, t):
        return max(0, min(self.end_time - t, self.duration))

    def distance_to_start(self, pt):
        return pt.distance_to(self.start_pos)


class Unit:
    def __init__(self, name, speed, tariff, time_period, curr_pos):
        self.name = name
        self.queue = []
        self.speed = speed
        self.tariff = tariff
        self.tper = time_period
        self.current_pos = curr_pos
        self.session_size = 3
        self.enabled = True

    def at_work(self, t):
        return self.tper[0] <= t < self.tper[1]        

    def can_append(self, t):
        if len(self.queue) >= self.session_size:
            return False
        elif not self.at_work(t):
            return False
        return self.enabled
    
    def get_time_left(self, t):
        a = t if not self.queue else self.queue[-1].end_time
        return a - t

    def order_time(self, order):
        from_pos = self.last_point()
        path = order.distance_to_start(from_pos)
        path += order.length
        return path // self.speed

    def last_point(self):
        if self.queue:
            return self.queue[-1].end_point
        return self.current_pos

    def calc_coef(self, order, t):
        if not self.can_append(t):
            return -1
        tp = self.get_time_left(t)
        tp += self.order_time(order)
        if not self.at_work(t + tp):
            return -1
        c = order.length * self.tariff
        n = len(self.queue)
        a = tp * c * sqrt(n + 1)
        b = order.max_time * order.max_price
        return a / b

    def append_order(self, order, t):
        self.log('added the order!')
        st = t + self.get_time_left(t)
        d = self.order_time(order)
        order.set_timings(st, d)
        self.queue.append(order)

    def log(self, text):
        print(f'[UNIT {self.name}]', text)

    def update(self, t):
        if not self.queue:
            return
        elif t >= self.queue[0].end_time:
            self.current_pos = self.queue[0].end_pos
            del self.queue[0]
            self.log('Order has been delivered')


class Delivery:
    def __init__(self, units):
        self.units = units
        self.t = 0
    
    def add_order(self, order):
        coef = [u.calc_coef(order, self.t) for u in self.units]
        print(coef)
        i = argmin(coef, lambda x: x >= 0)
        self.units[i].append_order(order, self.t)

    def update(self):
        print('UPDATING', self.t)
        for u in self.units:
            u.update(self.t)
        self.t += 1
    
    def update_loop(self):
        while self.t < MAX_TIME:
            self.update()


core = Delivery([
    Unit('u0', 1, 1, (0, MAX_TIME), Point(0, 5)),
    Unit('u1', 1, 1, (0, 10), Point(2, 2))
])

while core.t < MAX_TIME:
    if core.t == 5:
        order = Order(Point(2, 2), Point(5, 6), 50, 20)
        core.add_order(order)
    core.update()