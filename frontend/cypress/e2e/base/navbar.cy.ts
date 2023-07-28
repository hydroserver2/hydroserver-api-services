describe('Navbar', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.viewport(1500, 1200)
  })

  it('unauthenticated user sees unauthenticated navbar', () => {
    cy.get('.signup-btn').should('be.visible')
    cy.get('.navbar-login-button').should('be.visible')
    cy.get('.account-logout-button').should('not.exist')
  })

  it('authenticated user sees authenticated navbar', () => {
    cy.login('paul')
    cy.get('.account-logout-button').should('be.visible')
    cy.get('.signup-btn').should('not.exist')
    cy.get('.navbar-login-button').should('not.exist')
  })

  it('clicking login directs to login page', () => {
    cy.get('.navbar-login-button').click()
    cy.url().should('include', '/Login')
  })

  it('clicking logout logs out the user', () => {
    cy.login('paul')
    cy.get('.account-logout-button').click()
    cy.get('#navbar-logout').click()
    cy.get('.navbar-login-button').should('be.visible')
  })
})
