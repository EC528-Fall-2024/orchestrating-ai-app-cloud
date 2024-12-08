require('dotenv').config();
const axios = require('axios');
const { initializeApp } = require('firebase/app');
const { getAuth, signInWithEmailAndPassword } = require('firebase/auth');

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
const FUNCTION_URL = 'https://destroy-resources-531274461726.us-central1.run.app';

async function getAuthToken() {
    try {
        // Wait a moment for Firebase to initialize
        await new Promise(resolve => setTimeout(resolve, 1000));  
        
        const userCredential = await signInWithEmailAndPassword(auth, 'example@test.com', '123456');
        const token = await userCredential.user.getIdToken(true);  // Force refresh token
        console.log('✅ Successfully obtained auth token');
        return token;
    } catch (error) {
        console.error('🔥 Authentication error:', error.code, error.message);
        throw error;
    }
}

async function testDestroyResources() {
    try {
        // Get auth token
        const token = await getAuthToken();
        
        // Configure axios with auth header
        const config = {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },

            data: {}
        };

        console.log('\n🚀 Sending destroy request...');
        const destroyResponse = await axios.delete(FUNCTION_URL, config);
        console.log('✅ Resources destroyed:', destroyResponse.data);

    } catch (error) {
        console.error('❌ Error:', {
            message: error.response?.data || error.message,
            status: error.response?.status,
            statusText: error.response?.statusText,
            details: error.response?.data?.details || 'No additional details'
        });
        
        // Log the full error object in development
        console.error('Full error:', error);
    }
}

// Add proper process handling
testDestroyResources()
    .then(() => {
        console.log('✨ Operation completed');
        process.exit(0);
    })
    .catch((error) => {
        console.error('💥 Fatal error:', error);
        process.exit(1);
    });