<script>
	// Inspiration: https://3dtransforms.desandro.com/card-flip

	// State
	export let flipped = false;
</script>

<div class="container">
	<div class="card" class:flipped>
		<div class="front">
			<slot name="front" />
		</div>

		<div class="back">
			<slot name="back" />
		</div>
	</div>
</div>

<style>
	.container {
		position: absolute;
		width: 100%;
		height: 100%;
		perspective: 600px;
	}

	.card {
		width: 100%;
		height: 100%;
		position: relative;
		transition: transform 1s;
		transform-style: preserve-3d;
		transform-origin: center right;
	}

	.front,
	.back {
		position: absolute;
		height: 100%;
		width: 100%;
		backface-visibility: hidden;

		/* Fixes firefox bug */
		transform: rotateX(0deg);
	}

	.back {
		transform: rotateY(180deg);
		z-index: -1;
	}

	.card.flipped {
		/* Z translation to make element "above" front one */
		transform: translateX(-100%) rotateY(-180deg) translateZ(-1px);
	}

	.card.flipped .back {
		z-index: 1;
	}
</style>
