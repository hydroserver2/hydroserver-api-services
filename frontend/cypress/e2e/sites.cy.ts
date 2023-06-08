describe('Sites', () => {
  it('Should pass dummy test', () => {
    expect(true).to.equal(true)
  })

  it('Should redirect to login if not logged in', () => {
    cy.visit('/sites')
    cy.url().should('include', '/login')
  })

  // it('Should load the Sites page when logged in', () => {
  //   cy.intercept({
  //     method: 'GET',
  //     url: '/api/session'
  //   },
  //   {
  //     fixture: 'session_logged_in.json'
  //   });

  //   cy.visit('/sites');
  //   cy.url().should('include', '/sites');
  // });

  // it('Should load the Sites component successfully', () => {
  //   cy.url().should('include', '/sites')
  //   cy.get('h5').contains('My Registered Sites')
  //   cy.get('v-btn').contains('Register a new site')
  // })
})
