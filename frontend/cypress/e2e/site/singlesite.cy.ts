describe('SingleSite', () => {
  beforeEach(() => {
    cy.viewport(1500, 1200)
    cy.login('paul')
    cy.wait(1000)
    cy.visit('/sites/9344a3d4-a45a-4529-b731-b51149b4d1b8')
  })

  it('renders site content', () => {
    cy.wait(500)
    cy.get('.single-site-name h5').contains('Site in Miami')
  })

  it('renders owner specific button when logged in', () => {
    cy.get('.access_control').click()
    cy.get('.access_control_dialog').should('be.visible')
  })
})

// Single Site as owner:
// Edit a site
// Delete a site

// access control
// add secondary owners
// transfer ownership
// remove secondary owner
// make site private

// Visit as follower:
