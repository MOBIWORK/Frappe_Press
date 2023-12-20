<template>
	<div
		class="flex flex-row items-center justify-between rounded-lg border-2 p-2"
	>
		<p class="select-all overflow-hidden font-mono text-sm text-gray-800">
			{{ textContent }}
		</p>
		<Button icon="copy" @click="copyTextContentToClipboard" />
	</div>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	props: ['textContent'],
	methods: {
		copyTextContentToClipboard() {
			const clipboard = window.navigator.clipboard;
			clipboard.writeText(this.textContent).then(() => {
				notify({
					title: 'Đã sao chép vào bảng tạm!',
					icon: 'check',
					color: 'green'
				});
			});
		}
	}
};
</script>
