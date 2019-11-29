context('Search for flights', function () {

    it('Book and pay for a flight', function () {
        let flight = {
            departureCode: "LGW",
            arrivalCode: "MAD"
        }

        cy.login()

        // Search for a flight from London Gatwich to Madrid on June 26th 2019
        cy.visit('/#/search/results?date=2019-06-26&departure=LGW&arrival=MAD')
        cy.get('[data-test=flight-departure-code]').contains(flight.departureCode)
        cy.get('[data-test=flight-arrival-code]').contains(flight.arrivalCode)

        // Select 
        cy.get('[data-test=flight-card]').trigger('mouseover').click()

        // Input Payment data
        cy.get('[data-test=form-name]').type("E2E Test")
        cy.get('[data-test=form-postcode]').type('234563')
        cy.get('[data-test=form-country]').click()
            // select first country that appears
            .get('.q-popover > .q-list > :nth-child(1) > .q-item-main > .q-item-label').click()

        // Enter test card data into Stripe Elements:
        // Credits: https://gist.github.com/mbrochh/460f6d4fce959791c8f947cb30bed6a7#gistcomment-2906104
        cy.get('.__PrivateStripeElement > iframe').then(($elements) => {
            // $elements result set is the iframes for credit, expiry.
            const stripeElementsInputSelector = '.InputElement';

            // type into the first element:
            const creditInput = $elements.eq(0).contents().find(stripeElementsInputSelector);
            cy.wrap(creditInput).type('4242424242424242');

            // type into the expiry element:
            const expirationInput = $elements.eq(1).contents().find(stripeElementsInputSelector);
            // Expire far in the future: Dec 2059 seems to work.
            cy.wrap(expirationInput).type('12/59');

            // type into the cvc element:
            const cvcInput = $elements.eq(2).contents().find(stripeElementsInputSelector);
            cy.wrap(cvcInput).type('442');
        });

        // Once clicked, it should pre-authorize Payment and kick off the booking process
        cy.get('[data-test=payment-button]').click()

        // If pre-authorization worked, and booking process has been kicked off successfully we should be redirected to Bookings page
        // Due to networking calls variying, 10s is the worst case scenario even for 2G network 
        // Therefore it's safe to fail the test if nothing happens after that amount
        cy.location('hash', { timeout: 10000 }).should('eq', '#/profile/bookings')
    })
})
