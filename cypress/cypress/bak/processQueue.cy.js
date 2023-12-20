/// <reference types="cypress" />

const dataDir = 'cypress/e2e/data';
const queueFile = dataDir + '/queue/cypressQueue.json';
const outputFile = dataDir + '/queue/cypressOutput.json';
const logDir = '/Users/macbook-work/Documents/del/log/portfolio';
const rawHtmlDir = 'cypress/downloads/output-html';
const accounts = [];

fs.readdir(queueDir, (err, files) => {
  if (err) {
    console.error(err);
    return;
  }
  files.forEach((file) => {
    if (file.startsWith('NEW')) {
      const filePath = queueDir + '/' + file;
      // const newFilePath = filePath.replace('NEW', 'PROCESSED');
      console.log('Processing file: ' + filePath);
      fs.readFile(filePath, 'utf8', function (err, data) {
        if (err) {
          console.log(err);
          return;
        }
        const obj = JSON.parse(data);
        console.log(obj);
        accounts.push(obj);
      });
    }
  });
});

console.log(accounts);

Cypress.on('uncaught:exception', (err, runnable) => {
  if (err.message.includes('ResizeObserver loop')) {
    return false;
  }
});

describe('v3', () => {
  it('fetches accounts from queue, fetches and saves the html', () => {
    const accountsStr = cy.readFile(queueFile);
    const accounts = JSON.parse(accountsStr);
    console.log(accounts);

    accounts.forEach((account) => {
      cy.visit(account.url);
      cy.get("[class*='UpdateButton_refresh']").contains('Data updated');
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
    });
  });
});
