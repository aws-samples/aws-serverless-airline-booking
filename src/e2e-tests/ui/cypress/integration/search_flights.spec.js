context('Search for flights', function () {

    it('Search and select a flight', function () {
        let flight = {
            departureCode: "LGW",
            arrivalCode: "MAD"
        }

        // TODO: Move to fixture/support
        cy.visit('/')
        cy.get('.authenticator__form').within(() => {
            cy.get('input:first').type("demo")
            cy.get('input:last').type("Demo123!")

            cy.get('button').click()

        })
        cy.get('.cta__button > .q-btn-inner > div').contains("Search flights")

        // Search for a flight from London Gatwich to Madrid on June 26th 2019
        cy.visit('/#/search/results?date=2019-06-26&departure=LGW&arrival=MAD')
        cy.get(".flight__departure").contains(flight.departureCode)
        cy.get(".flight__arrival").contains(flight.arrivalCode)
        // cy.get(".flight__price").contains("100 eur")

        // Select 
        cy.get('.flight__card').trigger('mouseover').click()
    })
})
