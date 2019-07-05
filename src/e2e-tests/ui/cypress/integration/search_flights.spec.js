context('Search for flights', function () {

    it('Search and select a flight', function () {
        let flight = {
            departureCode: "LGW",
            arrivalCode: "MAD"
        }

        cy.login()

        // Search for a flight from London Gatwich to Madrid on June 26th 2019
        cy.visit('/#/search/results?date=2019-06-26&departure=LGW&arrival=MAD')
        cy.get('[data-test=flight-departure-code]').contains(flight.departureCode)
        cy.get('[data-test=flight-arrival-code]').contains(flight.arrivalCode)

        // Select and confirm whether flight has been successfully selected for booking
        cy.get('[data-test=flight-card]').trigger('mouseover').click()
        cy.get('[data-test=flight-headline]').contains("Review your selection")
    })
})
