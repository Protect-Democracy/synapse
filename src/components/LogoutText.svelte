<script>
	import { auth } from '../auth/firebase';
	import { signOut } from 'firebase/auth';
	import user from '../auth/user';

	// State
	let logoutError = null;
	let loggingAction = false;

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

{#if $user.isLoggedIn}
	<button class="button-text" on:click|preventDefault={logout} disabled={loggingAction}
		>Sign out</button
	>

	{#if logoutError}
		<span class="error-message">{logoutError}</span>
	{/if}

	<span class="spacer">|</span>
{/if}

<style>
	.spacer {
		color: var(--highlight-color);
	}
</style>
