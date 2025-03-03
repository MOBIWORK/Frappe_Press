<template>
	<div class="flex items-center justify-center">
		<div class="flex flex-col items-center">
			<img class="w-fit md:w-2/5" src="../../assets/404.png" />
			<h2 class="mt-5 text-2xl font-bold text-gray-900">
				{{ $t('Not Found') }}
			</h2>
			<h3 class="text-base font-semibold text-gray-700">
				{{ $t('message_not_found') }}
			</h3>
		</div>
	</div>
</template>

<script>
export default {
	name: '404NotFound',
	data() {
		return {
			surprise: false
		};
	}
};
</script>
