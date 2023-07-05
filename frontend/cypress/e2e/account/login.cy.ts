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

  it('does not log in with invalid credentials', () => {
    cy.get('.email-input').type('invalidemail@test.com')
    cy.get('.password-input').type('invalidpassword')
    cy.get('.login-button').click()
    cy.wait(500)
    cy.url().should('include', '/login')
  })

  // TODO
  it('logs in on-click of submit button', () => {
    cy.login('john')
  })

  // TODO
  // it('logs in on-enter of focused email or password field', () => {
  //   cy.login('john')
  // })

  it('logging in redirects to sites page', () => {
    cy.login('paul')
    cy.url().should('include', '/sites')
  })

  it('logs in, logs out, logs in as different user', () => {
    cy.login('paul')
    cy.get('.account-logout-button').click()
    cy.get('#navbar-logout').click()
    cy.get('.account-logout-button').should('not.exist')
    cy.visit('/login')
    cy.login('jane')
  })

  it('user stays logged in after reload', () => {
    cy.login('john')
    cy.wait(500)
    cy.reload()
    cy.url().should('include', '/sites')
  })
})
