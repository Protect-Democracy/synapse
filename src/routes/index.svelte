<script>
	import { slide } from 'svelte/transition';
	import LoginButton from '../components/LoginButton.svelte';
	import LogoutText from '../components/LogoutText.svelte';
	import Subscribe from '../components/Subscribe.svelte';
	import Carousel from '../components/Carousel.svelte';
	import CardFlip from '../components/CardFlip.svelte';
	import user from '../auth/user';
	import pdLogoWhite from '../assets/logo/pd-logo-white.svg';

	// State
	let about = false;
</script>

<div class="viewport">
	<CardFlip flipped={about}>
		<div slot="front" class="container">
			<div>
				<header>
					<h1>Random 1-on-1's every <strong>2</strong> weeks</h1>
				</header>

				<main class="split" transition:slide>
					<div class="carousel-container">
						<Carousel />
					</div>

					<div>
						<LoginButton />

						{#if $user.isLoggedIn}
							<Subscribe />
						{/if}
					</div>
				</main>

				<footer>
					<p>
						<a
							href="#about"
							on:click|preventDefault={() => {
								about = true;
							}}>About</a
						>
						<span class="spacer">|</span>

						<LogoutText />

						Made with love for
						<img src={pdLogoWhite} alt="Protect Democracy logo" />
					</p>
				</footer>
			</div>
		</div>

		<div slot="back" class="container">
			<div class="about">
				<h1>About</h1>

				<p>
					This little application let's people at Protect Democracy sign up for 1-on-1 meetings with
					other people that have signed-up as well. You will recieve an email pairing you up every 2
					weeks. It's up to you both to schedule, but the email will come with a helpful link to get
					you started. If you don't want to recieve emails anymore, just login and unsubscribe.
				</p>

				<footer>
					<p>
						<a
							href="#home"
							on:click|preventDefault={() => {
								about = false;
							}}>Home</a
						>
						<span class="spacer">|</span>

						<LogoutText />

						Made with love for
						<img src={pdLogoWhite} alt="Protect Democracy logo" />
					</p>
				</footer>
			</div>
		</div>
	</CardFlip>
</div>

<style>
	.viewport {
		position: relative;
		width: 100%;
		min-height: 100vh;
	}

	header {
		text-align: center;
		margin-bottom: 3rem;
	}

	h1 {
		font-size: 2.5rem;
		margin: 0;
		padding: 0;
	}

	h1 strong {
		text-decoration: underline;
	}

	.container {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100vh;
	}

	.split {
		display: flex;
	}

	.split > div {
		width: 25vw;
		margin: 0 1rem;
		display: flex;
		align-items: center;
		justify-content: center;
		text-align: center;
	}

	.carousel-container {
		width: 25vw;
		min-height: 20vw;
		position: relative;
	}

	footer {
		padding-top: 6rem;
		text-align: center;
		max-width: 20rem;
		margin: 0 auto;
		opacity: 0.8;
	}

	footer img {
		max-height: 1.3em;
		max-width: 3.2em;
		vertical-align: middle;
		display: inline;
	}

	.about {
		max-width: 20rem;
	}
</style>
