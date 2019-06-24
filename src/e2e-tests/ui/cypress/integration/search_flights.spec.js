context('Search for flights', function () {

    it('Search for flights', function () {
        // TODO: Move to fixture/support
        cy.visit('/')
        cy.get('.authenticator__form').within(() => {
            cy.get('input:first').type("demo")
            cy.get('input:last').type("Demo123!")

            cy.get('button').click()
        })

        // TODO: Search for a flight from LGW to MAD

    })
})
