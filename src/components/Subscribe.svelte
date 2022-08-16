<script>
	import { getDoc, setDoc, doc, onSnapshot, Timestamp } from 'firebase/firestore';
	import { onMount, onDestroy } from 'svelte';
	import { db } from '../auth/firebase';
	import user from '../auth/user';

	// State
	let initialLoad = true;
	let dbDocument = null;
	let dbError = null;
	let subscribing = false;
	let subscribingError = null;
	let dbUnsubscribe = null;
	$: isSubscribed = dbDocument && dbDocument.properties && dbDocument.properties.subscribed;
	$: userId = $user.isLoggedIn && $user.data && $user.data.uid ? $user.data.uid : null;

	// Database entry subscription
	function dbSubscribe() {
		if (dbUnsubscribe) {
			dbUnsubscribe();
		}
		if (!userId) {
			initialLoad = false;
			return;
		}

		const dbDoc = doc(db, 'neurons', userId);
		dbUnsubscribe = onSnapshot(
			dbDoc,
			(snapshot) => {
				initialLoad = false;
				dbDocument = {
					id: snapshot ? snapshot.id : undefined,
					properties: snapshot && snapshot.data ? snapshot.data() || {} : {}
				};
			},
			(error) => {
				console.error(error);
				dbError = error.toString();
			}
		);
	}

	// Subscribe
	async function subscribe() {
		if (!userId) {
			return;
		}

		subscribingError = null;
		dbError = null;
		subscribing = true;

		try {
			let data = {
				uid: $user.uid,
				subscribed: true,
				updated: Timestamp.fromDate(new Date()),
				name: $user.data.displayName,
				email: $user.data.email
			};

			await setDoc(doc(db, 'neurons', data.uid), data);
		} catch (e) {
			console.error(e);
			subscribingError = e.toString();
		}

		subscribing = false;
	}

	// Subscribe
	async function unsubscribe() {
		if (!userId) {
			return;
		}

		subscribingError = null;
		dbError = null;
		subscribing = true;

		try {
			let data = {
				uid: $user.uid,
				subscribed: false,
				updated: Timestamp.fromDate(new Date()),
				name: $user.data.displayName,
				email: $user.data.email
			};
			console.log(data);

			await setDoc(doc(db, 'neurons', data.uid), data);
		} catch (e) {
			console.error(e);
			subscribingError = e.toString();
		}

		subscribing = false;
	}

	// Lifecycle
	onMount(() => {
		dbSubscribe();
	});
	onDestroy(() => {
		if (dbUnsubscribe) {
			dbUnsubscribe();
		}
	});
</script>

<div class="subscribe">
	{#if isSubscribed}
		<h2 class="is-subscribed">You are subscribed!</h2>

		<div class="spacer" />

		<button
			on:click|preventDefault={unsubscribe}
			disabled={subscribing || initialLoad}
			aria-describedby="unsubscribe-help"
		>
			Unsubscribe</button
		>

		{#if !subscribingError || !dbError}
			<div id="unsubscribe-help" class="help">
				If you don't want anymore emails, tap the button above.
			</div>
		{/if}
	{:else}
		<button
			on:click|preventDefault={subscribe}
			disabled={subscribing || initialLoad}
			aria-describedby="subscribe-help">Subscribe</button
		>

		{#if !subscribingError || !dbError}
			<div id="subscribe-help" class="help">
				You'll recieve an email every 2 weeks to match you up for a 1-on-1.
			</div>
		{/if}
	{/if}

	{#if dbError}
		<div class="error-message">
			{dbError.match(/permission-denied/)
				? 'Not authorized: make sure you login with a PD or VS email.'
				: dbError}
		</div>
	{/if}

	{#if subscribingError}
		<div class="error-message">{subscribingError}</div>
	{/if}
</div>

<style>
	.help,
	.error-message {
		max-width: 20em;
	}

	.is-subscribed {
		margin-bottom: 2rem;
	}

	.spacer {
		width: 50%;
		margin: 0 auto 2rem auto;
		border-bottom: 1px solid var(--highlight-color);
	}
</style>
