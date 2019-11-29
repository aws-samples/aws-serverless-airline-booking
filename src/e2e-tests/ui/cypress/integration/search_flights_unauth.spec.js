context('Search for flights when not signed in', function () {
    it('Should redirect non-authenticated users', () => {
        cy.visit('/')
        // Should be on a new URL which includes '/commands/actions'
        cy.url().should('include', '/#/auth?redirectTo=home')
        cy.get('[data-test=authenticator]').within(() => {
            cy.get('input:first').should('have.attr', 'placeholder', 'Enter your username')
            cy.get('input:last').should('have.attr', 'placeholder', 'Enter your password')
        })
    })
})
