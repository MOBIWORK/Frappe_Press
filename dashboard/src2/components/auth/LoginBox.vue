<template>
	<div class="flex flex-col">
		<div class="relative z-10 mx-auto w-full max-w-full flex flex-col">
			<div class="flex-1 flex flex-col justify-center py-4 sm:py-6 md:py-8">
			<div class="flex flex-col px-4 items-center" @dblclick="redirectForFrappeioAuth">
				<slot name="logo">
					<!-- <div class="flex items-center justify-center space-x-2">
						<FCLogo class="inline-block h-[80px] w-[80px]" />
					</div> -->
				</slot>
			</div>
			<div class="mx-auto w-full bg-white px-3 sm:px-4 py-4 sm:py-6 sm:rounded-lg max-w-full" :class="[customWidth ? customWidth : 'sm:w-96']">
				<div class="mb-1 sm:mb-2" v-if="title">
					<span class="text-2xl font-bold leading-5 tracking-tight text-gray-900">
						{{ title }}
					</span>
				</div>
				<p class="mb-4 sm:mb-6 break-words text-sm sm:text-base font-normal leading-[21px] text-gray-700" v-if="subtitle">
					{{ subtitle }}
				</p>
				<slot></slot>
				<!-- <slot name="voucher"></slot> -->
			</div>
			</div>

			<div class="flex justify-center py-3 sm:py-4">
				<slot name="footer"></slot>
			</div>
		</div>
	</div>
</template>

<script>
import { toast } from 'vue-sonner';
import FCLogo from '@/components/icons/FCLogo.vue';

export default {
	name: 'LoginBox',
	props: ['title', 'logo', 'subtitle', 'customWidth'],
	components: {
		FCLogo,
	},
	mounted() {
		const params = new URLSearchParams(window.location.search);

		if (params.get('showRemoteLoginError')) {
			toast.error('Token Invalid or Expired');
		}
	},
	methods: {
		redirectForFrappeioAuth() {
			window.location = '/f-login';
		},
	},
};
</script>
