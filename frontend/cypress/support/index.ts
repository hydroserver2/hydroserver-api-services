declare namespace Cypress {
  interface Chainable<Subject> {
    login(email: string): Chainable<Subject>
  }
}
