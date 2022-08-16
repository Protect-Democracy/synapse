<script>
	import { auth, provider } from '../auth/firebase';
	import { signInWithPopup, signOut } from 'firebase/auth';
	import user from '../auth/user';

	// State
	let loginError = null;
	let logoutError = null;
	let loggingAction = false;

	// Login
	async function login() {
		loggingAction = true;

		try {
			await signInWithPopup(auth, provider);
			loggingAction = false;
		} catch (e) {
			console.error(e);
			errorMessage = e.toString();
			loggingAction = false;
		}
	}

	// Logout
	async function logout() {
		loggingAction = true;

		try {
			await signOut(auth);
			loggingAction = false;
		} catch (e) {
			console.error(e);
			logoutError = e.toString();
			loggingAction = false;
		}
	}
</script>

<div class="authenticate">
	{#if !$user.isLoggedIn}
		<button on:click|preventDefault={login} disabled={loggingAction}>Sign up</button>

		{#if loginError}
			<div class="error-message">{loginError}</div>
		{:else}
			<div class="help">Google login; triggers popup.</div>
		{/if}
	{/if}
</div>
