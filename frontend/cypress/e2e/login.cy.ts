describe('Login Component', () => {
  beforeEach(() => {
    cy.viewport(1500, 1200)
    cy.visit('/login')
  })

  it('renders the login form', () => {
    cy.get('.login-card').should('exist')
    cy.get('.login-title').should('contain', 'Sign In')
    cy.get('.email-input').should('exist')
    cy.get('.password-input').should('exist')
    cy.get('.login-button').should('exist')
    cy.get('.signup-link').should('have.attr', 'href', '/signup')
  })

  it('requires valid email', () => {
    cy.get('.login-button').should('be.disabled')
    cy.get('.password-input').type('testpassword')
    cy.get('.login-button').should('be.disabled')
    cy.get('.email-input').type('invalidemail')
    cy.get('.login-button').should('be.disabled')
  })

  it('requires password', () => {
    cy.get('.login-button').should('be.disabled')
    cy.get('.email-input').type('validemail@test.com')
    cy.get('.login-button').should('be.disabled')
  })

  it('signup button redirects to the signup page', () => {
    cy.get('.signup-link').click()
    cy.url().should('include', '/signup')
  })

  // TODO: When the user enters invalid credentials, they're redirected to the home page
  //       Keep them on the login page! Why does this test pass then? I think it has
  //       to do with how the interceptor keeps processing requests after a fail
  it('does not log in with invalid credentials', () => {
    cy.get('.email-input').type('invalidemail@test.com')
    cy.get('.password-input').type('invalidpassword')
    cy.get('.login-button').click()
    cy.url().should('include', '/login')
  })

  it('logs in with valid credentials', () => {
    cy.login('john')
  })

  it('logging in redirects to sites page', () => {
    cy.login('paul')
    cy.url().should('include', '/sites')
  })

  // TODO: This one fails sometimes because of a GoogleMap race condition
  // it('logs in, logs out, logs in as second user', () => {
  //   cy.login('paul')
  //   cy.get('.account-logout-button').click()
  //   cy.get('#navbar-logout').click()
  //   cy.get('.account-logout-button').should('not.exist')
  //   cy.get('.navbar-login-button').click()
  //   cy.login('jane')
  // })

  it('user stays logged in after reload', () => {
    cy.login('john')
    cy.reload()
    cy.url().should('include', '/sites')
  })
})
