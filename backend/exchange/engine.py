from dataclasses import dataclass

@dataclass
class BookOrder:
    order_id: str
    user_id: int
    side: str
    price: int
    quantity: int
    sequence: int

@dataclass
class Fill:
    buy_order_id: str
    sell_order_id: str
    price: int
    quantity: int

def sort_resting(orders, incoming_side):
    opposing = [o for o in orders if o.side != incoming_side and o.quantity > 0]
    return sorted(opposing, key=(lambda o: (o.price, o.sequence)) if incoming_side == "BUY" else (lambda o: (-o.price, o.sequence)))

def match(incoming, resting_orders):
    qty = incoming.quantity
    fills = []
    for resting in resting_orders:
        if qty <= 0:
            break
        if resting.side == incoming.side:
            continue
        crosses = resting.price <= incoming.price if incoming.side == "BUY" else resting.price >= incoming.price
        if not crosses:
            break
        amount = min(qty, resting.quantity)
        if amount <= 0:
            continue
        fills.append(Fill(incoming.order_id, resting.order_id, resting.price, amount) if incoming.side == "BUY" else Fill(resting.order_id, incoming.order_id, resting.price, amount))
        qty -= amount
    return fills, qty
