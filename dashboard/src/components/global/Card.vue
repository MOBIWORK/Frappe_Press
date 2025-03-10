<template>
	<div class="flex flex-col rounded-lg border bg-white px-6 py-5">
		<div class="flex flex-wrap items-baseline justify-between">
			<div class="mb-2 flex items-center space-x-2">
				<div class="flex items-center space-x-2" v-if="$slots['actions-left']">
					<slot name="actions-left"></slot>
				</div>
				<div>
					<h2 class="text-xl font-semibold">{{ title }}</h2>
					<p class="mt-1.5 text-base text-gray-600" v-if="subtitle">
						{{ subtitle }}
					</p>
				</div>
				<div class="flex items-center space-x-2" v-if="$slots['info-more']">
					<slot name="info-more"></slot>
				</div>
			</div>
			<div
				class="flex min-w-max items-center space-x-2"
				v-if="$slots['actions']"
			>
				<slot name="actions"></slot>
			</div>
		</div>
		<p class="mt-1.5 text-base text-gray-600" v-if="description">
			{{ description }}
		</p>
		<div
			v-if="loading"
			class="mt-4 flex flex-auto flex-col items-center justify-center rounded-md"
		>
			<LoadingText />
		</div>
		<div
			class="mt-4 flex-auto"
			:class="{ 'overflow-auto': !stopOverflow }"
			v-else-if="$slots['default']"
		>
			<slot></slot>
		</div>
	</div>
</template>
<script>
import { LoadingText } from 'frappe-ui';
export default {
	name: 'Card',
	props: ['title', 'subtitle', 'description', 'loading', 'stopOverflow'],
	components: {
		LoadingText
	}
};
</script>
