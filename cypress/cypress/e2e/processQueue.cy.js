/// <reference types="cypress" />

const runId = Cypress.env('runId');
// const runId = 402;
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

describe('Fetch html', () => {
  it('Get accounts from queue, fetches html', () => {
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

        // total_div = driver.find_element(By.CSS_SELECTOR, "[class*='HeaderInfo_totalAsset']")
        /*
        cy.get("[class*='HeaderInfo_totalAsset']").should((element) => {
          let totalText = element.text();
          totalText = totalText.replace('$', '').replace(',', '');
          // new_total = float(first_number(total_text))
          const newTotal = parseFloat(totalText);
          account.total = newTotal;
          if (newTotal * 1.2 < account.lastTotal) account.status = 'INVALID';
          cy.log(
            `totalText:${newTotal} newTotal: ${newTotal} lastTotal: ${account.lastTotal} status: ${account.status}`
          );
        });
        */

        cy.get('body').then((doc) => {
          cy.writeFile(
            `${rawHtmlDir}/${account.fileName}`,
            doc[0].outerHTML,
            'utf8'
          );
        });
        updatedAccounts.push(account);
        cy.log(`Updated account ${account}. Pausing for 5 seconds...`);
        cy.wait(5000);
      });
    });
    cy.writeFile(statusFile, updatedAccounts, 'utf8');
  });
});
