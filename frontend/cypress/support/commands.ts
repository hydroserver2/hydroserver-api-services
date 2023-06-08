interface User {
  email: string
  password: string
  first_name: string
}

Cypress.Commands.add('login', (name: string) => {
  cy.fixture('users.json').then((users: User[]) => {
    const user = users.find((user) => user.first_name === name)

    if (!user) throw new Error(`User with name ${name} not found in fixture.`)

    cy.get('.email-input').type(user.email)
    cy.get('.password-input').type(user.password)
    cy.get('.login-button').click()
    cy.url().should('include', '/sites')
  })
})
