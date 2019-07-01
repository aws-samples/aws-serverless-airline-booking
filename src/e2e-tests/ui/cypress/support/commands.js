// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

Cypress.Commands.add('login', (options = {}) => {
    // this is an example of skipping your UI and logging in programmatically

    // TODO: fetch it from Secrets Manager/SSM Param
    // and user properties
    const creds = {
        username: 'demo',
        password: "Demo123!",
    }

    cy.visit('/')
    cy.get('[data-test=authenticator]').within(() => {
        cy.get('input:first').type(creds.username)
        cy.get('input:last').type(creds.password)

        cy.get('button').click()
    })
    cy.get('.cta__button > .q-btn-inner > div').contains("Search flights")

})