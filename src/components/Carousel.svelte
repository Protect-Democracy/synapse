<script>
	// Inspiration: https://codepen.io/desandro/pen/wjeBpp
	import { onMount, onDestroy } from 'svelte';
	import cup01 from '../assets/cups/cup-01.svg';
	import cup02 from '../assets/cups/cup-02.svg';
	import cup03 from '../assets/cups/cup-03.svg';
	import cup04 from '../assets/cups/cup-04.svg';
	import cup05 from '../assets/cups/cup-05.svg';

	// State
	let images = [cup01, cup02, cup03, cup04, cup05];
	let carouselHeight = 0;
	let randomSpin = 0;
	let mounted = false;
	let mountedTimeout;
	let continuousSpinTimeout;
	$: transformTheta = 360 / images.length;
	$: transformRadius = Math.round(carouselHeight / 2 / Math.tan(Math.PI / images.length));

	// Methods
	function spin() {
		let direction = Math.random() > 0.5 ? 1 : -1;
		randomSpin =
			Math.floor(Math.random() * images.length * 5 + images.length) * transformTheta * direction;
	}
	function continuousSpin() {
		spin();
		continuousSpinTimeout = setTimeout(() => {
			continuousSpin();
		}, Math.random() * 15000 + 10000);
	}

	// Lifecycle
	onMount(() => {
		// Given that we calculate the transform radius when mounted and then
		// set the style in the dom, this triggers the transition on load/mount,
		// so we hack aounnd this by setting mounted after a tick.
		mountedTimeout = setTimeout(() => {
			mounted = true;

			// Start auto spin
			continuousSpin();
		}, 100);
	});
	onDestroy(() => {
		if (mountedTimeout) {
			clearTimeout(mountedTimeout);
		}
		if (continuousSpinTimeout) {
			clearTimeout(continuousSpinTimeout);
		}
	});
</script>

<div class="carousel" role="presentation" bind:clientHeight={carouselHeight} on:click={spin}>
	<div
		class="carousel-inner"
		style="transform: translateZ({transformRadius * -0.95}px) rotateX({randomSpin}deg)"
		class:mounted
	>
		{#each images as image, i}
			<div
				class="carousel-item"
				style="transform: rotateX({i * transformTheta}deg) translateZ({transformRadius}px)"
			>
				<div class="carousel-item-inner">
					<img class="d-block w-100" src={image} alt={image} />
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	/* Known clipping issue in Safari where you can see the background items
	 as the wheel is spinning. */

	.carousel {
		position: relative;
		height: 100%;
		width: 100%;
		perspective: 1000px;
		overflow: hidden;
		cursor: pointer;
	}

	.carousel-inner {
		position: absolute;
		width: 100%;
		height: 100%;
		transform-style: preserve-3d;
	}

	.carousel-inner.mounted {
		/* cubic-bezier(0.36, 0, 0.66, -0.56) */
		/* https://cubic-bezier.com/#.68,-0.6,.03,1 */
		transition: transform 3s cubic-bezier(0.42, -0.3, 0.06, 1);
	}

	.carousel-item {
		background-color: var(--background-color);
		position: absolute;
		width: 100%;
		height: 100%;
		text-align: center;
	}

	.carousel-item-inner {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		padding: 1em;
		display: grid;
		place-items: center;
	}

	img {
		max-width: 100%;
		max-height: 100%;
	}
</style>
