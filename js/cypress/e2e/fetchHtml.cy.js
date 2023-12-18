/// <reference types="cypress" />
/*
describe.skip('Get page html', () => {
  it('displays two todo items by default', () => {
    cy.request({
      url: 'https://debank.com/profile/0x984fc40d64dda70fe73cbc7978362d78f10599a2',
    }).then((response) => {
      cy.writeFile('cypress/downloads/export-wait.html', response.body, 'utf8');
    });
    cy.visit('https://example.cypress.io/todo');
    cy.get('.todo-list li').should('have.length', 2);
  });
});

describe.skip('v2', () => {
  it('displays two todo items by default', () => {
    cy.visit(
      'https://debank.com/profile/0x984fc40d64dda70fe73cbc7978362d78f10599a2'
    );
    // cy.get("[class*='UpdateButton_updateTimeNumber']");
    cy.wait(5000);
    // get body html
    cy.document().then((doc) => {
      cy.log(doc);
      cy.writeFile(
        'cypress/downloads/export-v2.html',
        doc.documentElement.outerHTML,
        'utf8'
      );
    });
  });
});
*/
Cypress.on('uncaught:exception', (err, runnable) => {
  if (err.message.includes('ResizeObserver loop')) {
    return false;
  }
});

describe('v3', () => {
  it('fetches and saves the page html', () => {
    cy.visit(
      'https://debank.com/profile/0x984fc40d64dda70fe73cbc7978362d78f10599a2'
    );
    cy.get("[class*='UpdateButton_refresh']").contains('Data updated');
    // cy.get("[class*='UpdateButton_updateTimeNumber']");
    // cy.wait(5000);
    // get body html
    cy.get('body').then((doc) => {
      // cy.log(doc);
      cy.writeFile(
        'cypress/downloads/export-v3.html',
        doc[0].outerHTML,
        'utf8'
      );
    });
  });
});
