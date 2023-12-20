/// <reference types="cypress" />

const runId = Cypress.env('runId');
// const runId = 383;
const dataDir = 'cypress/e2e/data';
const queueFile = `${dataDir}/queue/cypressQueue-${runId}.json`;
const statusFile = `${dataDir}/queue/cypressStatus-${runId}.json`;
const logDir = '/Users/macbook-work/Documents/del/log/portfolio';
const rawHtmlDir = `${dataDir}/output-html/${runId}`;

Cypress.on('uncaught:exception', (err, runnable) => {
  if (err.message.includes('ResizeObserver loop')) {
    return false;
  }
});

describe('v3', () => {
  it('fetches accounts from queue, fetches and saves the html', () => {
    const updatedAccounts = [];
    cy.readFile(queueFile).then((data) => {
      cy.log(JSON.stringify(data, 2, null));
      // const accounts = JSON.parse(data);

      // cy.log(accounts);
      // const accounts = [];
      data.forEach((account) => {
        account.status = 'ERROR';
        cy.visit(account.url);
        cy.get("[class*='UpdateButton_refresh']").contains('Data updated');
        account.status = 'PARSING';
        // cy.get("[class*='UpdateButton_updateTimeNumber']");
        // cy.wait(5000);
        // get body html
        cy.get('body').then((doc) => {
          // cy.log(doc);
          cy.writeFile(
            `${rawHtmlDir}/${account.fileName}`,
            doc[0].outerHTML,
            'utf8'
          );
        });
        updatedAccounts.push(account);
      });
    });
    cy.writeFile(statusFile, updatedAccounts, 'utf8');
  });
});
