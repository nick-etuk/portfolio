const dataDir =
  '/Users/macbook-work/Library/CloudStorage/OneDrive-Personal/data/portfolio';
const queueDir = dataDir + '/cypress-queue';
const logDir = '/Users/macbook-work/Documents/del/log/portfolio';
const rawHtmlDir = logDir + '/raw-html';

// read all files in the queue directory that begin with 'NEW' and process them
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
        const url = obj.url;
        console.log(url);
        const fileName = obj.fileName;
        console.log(fileName);

        // console.log(data);
        // cy.visit(
        //   'https://debank.com/profile/0x984fc40d64dda70fe73cbc7978362d78f10599a2'
        // );
        // cy.get("[class*='UpdateButton_refresh']").contains('Data updated');
        // cy.get("[class*='UpdateButton_updateTimeNumber']");
        // cy.wait(5000);
        // get body html
        // cy.get('body').then((doc) => {
        //   // cy.log(doc);
        //   cy.writeFile(
        //     'cypress/downloads/export-v3.html',
        //     doc[0].outerHTML,
        //     'utf8'
        //   );
        // });
        // const html = data;
        // const $ = cheerio.load(html);
        // const title = $('title').text();
        // console.log(title);
        // const body = $('body').text();
        // console.log(body);
        // const bodyHtml = $('body').html();
      });
    }
  });
});
