import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { 
    getAuth, 
    signInWithPopup, 
    GoogleAuthProvider,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword
} from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

// Read from localStorage to allow runtime overrides, with default fallback to user's config
const savedConfig = localStorage.getItem("firebase_config");
const firebaseConfig = savedConfig ? JSON.parse(savedConfig) : {
    apiKey: "AIzaSyCPUzqqptz59hIKKaDzsxfX3seDfg-mkW4",
    authDomain: "ecosphere-ai-392fe.firebaseapp.com",
    projectId: "ecosphere-ai-392fe",
    storageBucket: "ecosphere-ai-392fe.firebasestorage.app",
    messagingSenderId: "569945884756",
    appId: "1:569945884756:web:ef9fa49c4ae7a22aa705c1"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { 
    auth, 
    googleProvider, 
    signInWithPopup, 
    signInWithEmailAndPassword, 
    createUserWithEmailAndPassword 
};
