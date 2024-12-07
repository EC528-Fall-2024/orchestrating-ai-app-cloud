require('dotenv').config();
const axios = require('axios');
const { initializeApp } = require('firebase/app');
const { getAuth, signInWithEmailAndPassword } = require('firebase/auth');
const fs = require('fs');

// Your Firebase config (get this from Firebase Console)
const firebaseConfig = {
    apiKey: "AIzaSyA9YPNJUo9Z6OIxgACbSLB-VUQDaaXxdMQ",
    authDomain: "cynthusgcp-438617.firebaseapp.com",
    projectId: "cynthusgcp-438617",
    storageBucket: "cynthusgcp-438617.firebasestorage.app",
    messagingSenderId: "531274461726",
    appId: "1:531274461726:web:2808bff76aea329ada740f",
    measurementId: "G-566Z5L0800"
  };

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Cloud Function URL
const FUNCTION_URL = 'https://us-central1-cynthusgcp-438617.cloudfunctions.net/bucket_operations';
const srcFileName = 'mnist_test.py'; // src code location
const srcFileName2 = 'report-ip.sh'; // src code location
const configFileName = 'config.json'; // config file location

async function getAuthToken() {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, 'example@test.com', '123456');
    return userCredential.user.getIdToken();
  } catch (error) {
    console.error('Authentication error:', error.message);
    throw error;
  }
}

async function testBucketOperations() {
  try {
    // Get auth token
    const token = await getAuthToken();
    
    // Configure axios with auth header
    const config = {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };

    // Test 1: Create bucket
    console.log('\n🚀 Testing bucket creation...');
    const createResponse = await axios.post(FUNCTION_URL, {
      operation: 'create'
    }, config);
    console.log('✅ Bucket created:', createResponse.data);

    console.log('\n🚀 Testing bucket creation...');
    const createOutputResponse = await axios.post(FUNCTION_URL, {
      operation: 'create_output'
    }, config);
    console.log('✅ Output Bucket created:', createResponse.data);

    // Test 2: Upload file
    console.log('\n🚀 Testing src file upload...');
    const srcFileContent = fs.readFileSync(srcFileName, 'utf8');
    const srcUploadResponse = await axios.post(FUNCTION_URL, {
      operation: 'upload',
      path: `src/${srcFileName}`,
      content: srcFileContent
    }, config);
    console.log('✅ File uploaded:', srcUploadResponse.data);

    // Test 2: Upload file
    console.log('\n🚀 Testing src file upload...');
    const srcFileContent2 = fs.readFileSync(srcFileName2, 'utf8');
    const srcUploadResponse2 = await axios.post(FUNCTION_URL, {
      operation: 'upload',
      path: `src/${srcFileName2}`,
      content: srcFileContent2
    }, config);
    console.log('✅ File uploaded:', srcUploadResponse2.data);


    console.log('\n🚀 Testing config file upload...');
    const configFileContent = fs.readFileSync('config.json', 'utf8');
    const configUploadResponse = await axios.post(FUNCTION_URL, {
      operation: 'upload',
      path: `${configFileName}`,
      content: configFileContent
    }, config);
    console.log('✅ File uploaded:', configUploadResponse.data);

    

    // Test 3: Generate requirements.txt (POST)
    console.log('\n🚀 Testing requirements.txt generation...');
    const requirementsResponse = await axios.post(FUNCTION_URL, {
      operation: 'generate_requirements'
    }, config);
    console.log('✅ Requirements generated:', requirementsResponse.data);



  } catch (error) {
    // Enhance error logging
    console.error('❌ Error:', {
      message: error.response?.data || error.message,
      status: error.response?.status,
      statusText: error.response?.statusText
    });
  }
}
testBucketOperations();
