describe('Profile Page', () => {
  beforeEach(() => {
    cy.viewport(1500, 1200)
  })

  it('populates form with user information', () => {
    cy.login('paul')
    cy.wait(1000)
    cy.visit('/profile')
    cy.wait(1000)
    cy.get('.user-info').contains('Paul')
  })
  // it('allows user to edit their information', () => {})
  // it('allows user to delete their account', () => {})
})
