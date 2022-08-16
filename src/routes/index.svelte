<script>
	import LoginButton from '../components/LoginButton.svelte';
	import LogoutText from '../components/LogoutText.svelte';
	import Subscribe from '../components/Subscribe.svelte';
	import Carousel from '../components/Carousel.svelte';
	import user from '../auth/user';
	import pdLogoWhite from '../assets/logo/pd-logo-white.svg';
</script>

<div class="container">
	<div>
		<header>
			<h1>Random 1-on-1's every <strong>2</strong> weeks</h1>
		</header>

		<main class="split">
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
				<LogoutText />
				Made with love for <img src={pdLogoWhite} alt="Protect Democracy logo" />
			</p>
		</footer>
	</div>
</div>

<style>
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
		vertical-align: middle;
	}
</style>
