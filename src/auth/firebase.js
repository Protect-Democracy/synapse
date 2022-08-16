import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { getFirestore, setLogLevel } from 'firebase/firestore';
import firebaseConfig from '../config/firebase';

// Initialize Firebase
const app = initializeApp(firebaseConfig.connection);

// Initialize Firebase Authentication and get a reference to the service
const auth = getAuth(app);

// Google auth
// https://developers.google.com/identity/protocols/oauth2/scopes
const provider = new GoogleAuthProvider();
provider.addScope('profile');
provider.addScope('email');

// Make firestore connection
if (firebaseConfig.debug) {
	setLogLevel('debug');
}
const db = getFirestore(app);

export { app, auth, provider, db };
