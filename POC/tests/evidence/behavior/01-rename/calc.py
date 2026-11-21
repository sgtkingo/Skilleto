def invoice_total(prices, tax_rate=0.0):
    subtotal = sum(prices)
    subtotal += subtotal * tax_rate
    return round(subtotal, 2)
