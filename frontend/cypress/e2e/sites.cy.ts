describe('Sites', () => {
  beforeEach(() => {
    cy.viewport(1500, 1200)
    cy.visit('/login')
  })

  it('redirects to login if not logged in', () => {
    cy.visit('/sites')
    cy.url().should('include', '/login')
  })

  it('renders data', () => {
    cy.login('paul')
    cy.url().should('include', '/sites')
    cy.get('.owned-sites-table')
      .find('tbody')
      .find('tr')
      .should('have.length.greaterThan', 0)
  })

  it('opens and closes site form', () => {
    cy.login('paul')
    cy.get('.register-site-btn').click()
    // cy.get('v-dialog').should('be.visible')
    // cy.get('SiteForm').find('button').contains('Close').click()
    // cy.get('v-dialog').should('not.be.visible')
  })

  it.only('links navigate to the correct pages', () => {
    cy.login('john')
    cy.get('.manage-metadata-button').click()
    cy.url().should('include', '/Metadata')
    cy.visit('/sites')
    cy.get('.owned-sites-table tbody tr').first().click()
    cy.get('.single-site-name').should('be.visible')
  })
})
