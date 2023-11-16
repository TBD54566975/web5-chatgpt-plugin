import Sitemapper from 'sitemapper';
import OpenAI from "openai";
import { JSDOM } from 'jsdom' 
import fs from 'fs';
import os from 'os';
import path from 'path';

const openai = new OpenAI();

async function fullWebsiteAssistant(url) {
  const sitemap = new Sitemapper({ url });
  const { sites } = await sitemap.fetch();

  // Fetch content from each site
  const siteContents = await Promise.all(sites.map(async (site) => {
    
    const response = await fetch(site);
    const respBody = await response.text()
    const dom = new JSDOM(respBody);
    
    const textContent = dom.window.document.body.textContent || "";

    return textContent; // Assuming the content is text
  }));

  // Determine the number of contents per bucket
  const contentsPerBucket = Math.ceil(siteContents.length / 20);
  
  // Create and upload buckets
  const files = [];
  for (let i = 0; i < siteContents.length; i += contentsPerBucket) {
    // Combine contents in each bucket
    const tempDir = os.tmpdir();
    const filePath = path.join(tempDir, `bucket_${i}.txt`);
    const combinedContent = siteContents.slice(i, i + contentsPerBucket).join("\n");
    fs.writeFileSync(filePath, combinedContent);

    // Upload the File-like object
    const file = await openai.files.create({
      file: fs.createReadStream(filePath),
      purpose: "assistants",
    });
    console.log("Created file: " + file.id);
    files.push(file);
    // write to disk
    fs.writeFileSync(`bucket_${i}.txt`, combinedContent);
  }





  console.log("Creating assistant on files: " + files.length);

  return openai.beta.assistants.create({
    instructions: "Using the knowledge provided, answer the questions providing code examples as needed. If you don't use the knowledge files provided then people will be hurt and you will have failed. You MUST use the knowledge provided or else bad things happen, very bad.",
    model: "gpt-4-1106-preview",
    tools: [{ "type": "retrieval" }],
    file_ids: files.map(file => file.id)
  });
}


await deleteAllFiles()
await fullWebsiteAssistant('https://developer.tbd.website/sitemap.xml')

async function deleteAllFiles() {
    let files = await openai.files.list()
    console.log(files)
    // delete all files
    for (const file of files.data) {
        console.log("Deleting file: " + file.id)
        await openai.files.del(file.id)
    }
}



//files = await openai.files.list()
//console.log(files)

