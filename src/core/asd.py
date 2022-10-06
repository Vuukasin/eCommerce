

import stripe
# This is your test secret API key.
stripe.api_key = 'sk_test_51Lm5hSAf1QNOQU7dlRtOYdUdQbkSSKpVT0aOSzUjReU2zMj9oYbkWHpCu2qGuKOiWQStsLTARHedcM2ocssDr47200nBTlwRk9'


YOUR_DOMAIN = 'http://localhost:4242'

# @app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': '{{PRICE_ID}}',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    # return redirect(checkout_session.url, code=303)

# if __name__ == '__main__':
#     app.run(port=4242)