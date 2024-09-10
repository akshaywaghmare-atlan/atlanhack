import { execSync } from 'child_process';
import fs from 'fs-extra';
import path, { dirname } from 'path';
import { fileURLToPath } from 'url';

// Configuration
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const sourceDir = path.join(__dirname, '.output', 'public');
const targetDir = path.join(__dirname, '..', 'src', 'main', 'resources', 'static', 'dist');


// Function to run a command
function runCommand(command) {
  try {
    console.log(`Running command: ${command}`);
    const output = execSync(command, { encoding: 'utf-8' });
    console.log(output);
  } catch (error) {
    console.error(`Error executing command: ${command}`);
    console.error(error.message);
    process.exit(1);
  }
}

// Generate static files
function generateStatic() {
  console.log('Generating static files...');
  runCommand('npx nuxt generate');
  console.log('Static files generated.');
}

// Remove existing files
function cleanTargetDirectory() {
  console.log(`Cleaning directory: ${targetDir}`);
  try {
    fs.emptyDirSync(targetDir);
    console.log('Target directory cleaned successfully.');
  } catch (err) {
    console.error('Error cleaning target directory:', err);
    process.exit(1);
  }
}

// Copy files
function copyFiles() {
  console.log(`Copying files from ${sourceDir} to ${targetDir}...`);
  try {
    fs.copySync(sourceDir, targetDir);
    console.log('Files copied successfully.');
  } catch (err) {
    console.error('Error copying files:', err);
    process.exit(1);
  }
}

// Main function
function main() {
  generateStatic();
  cleanTargetDirectory();
  copyFiles();
  console.log('Process completed successfully.');
}

try {
  main();
} catch (err) {
  console.error('An error occurred:', err);
  process.exit(1);
}

// // Function to run a command
// function runCommand(command) {
//   return new Promise((resolve, reject) => {
//     exec(command, (error, stdout, stderr) => {
//       if (error) {
//         console.error(`exec error: ${error}`);
//         return reject(error);
//       }
//       console.log(stdout);
//       console.error(stderr);
//       resolve();
//     });
//   });
// }

// // Generate static files
// async function generateStatic() {
//   console.log('Generating static files...');
//   await runCommand('npx nuxt generate');
//   console.log('Static files generated.');
// }

// // Remove existing files
// async function cleanTargetDirectory() {
//   console.log(`Cleaning directory: ${targetDir}`);
//   try {
//     await fs.emptyDir(targetDir);
//     console.log('Target directory cleaned successfully.');
//   } catch (err) {
//     console.error('Error cleaning target directory:', err);
//     process.exit(1);
//   }
// }

// // Copy files
// async function copyFiles() {
//   console.log(`Copying files from ${sourceDir} to ${targetDir}...`);
//   try {
//     await fs.copy(sourceDir, targetDir);
//     console.log('Files copied successfully.');
//   } catch (err) {
//     console.error('Error copying files:', err);
//     process.exit(1);
//   }
// }

// // Main function
// async function main() {
//   await generateStatic();
//   await cleanTargetDirectory();
//   await copyFiles();
//   console.log('Process completed successfully.');
// }

// main().catch(err => {
//   console.error('An error occurred:', err);
//   process.exit(1);
// });