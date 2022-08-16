/**
 * Store with user in it.  Basically a proxy for firebase
 * auth subscription
 */

// Dependencies
import { writable } from 'svelte/store';
import { auth } from './firebase';

// Create store
const user = writable({});

// Subscribe to auth
auth.onAuthStateChanged(async (u) => {
	// Get id token and attach some helpful data
	if (u) {
		let idToken = await auth.currentUser.getIdToken();
		u.isLoggedIn = true;
		u.idToken = idToken;
		u.data = u.toJSON();
		u.tokens = u.data.stsTokenManager;
		user.set(u);
	} else {
		user.set({ isLoggedIn: false });
	}
});

// Export
export { user as default };
