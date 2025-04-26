<template>
	<div
		v-if="showLoading"
		class="fixed inset-0 z-20 flex h-full w-full items-center justify-center gap-2 bg-black bg-opacity-30 text-gray-900"
	>
		<Spinner class="h-5 w-5" /> {{ $t('Loading') }}...
	</div>
</template>

<script setup>
import { showLoading } from '@/composables/language';
</script>
