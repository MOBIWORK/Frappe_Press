<template>
	<div class="flex h-screen flex-col">
		<div class="relative z-10 mx-auto flex-grow py-10 w-full max-w-full grid">
			<div class="">
			<div class="flex flex-col px-4 items-center" @dblclick="redirectForFrappeioAuth">
				<slot name="logo">
					<!-- <div class="flex items-center justify-center space-x-2">
						<FCLogo class="inline-block h-[80px] w-[80px]" />
					</div> -->
				</slot>
			</div>
			<!-- Modified to accept custom width via props with proper responsive handling -->
			<div class="mx-auto w-full bg-white px-4 py-6 sm:rounded-lg max-w-full" :class="[customWidth ? customWidth : 'sm:w-96']">
				<div class="mb-2" v-if="title">
					<span class="text-2xl font-bold leading-5 tracking-tight text-gray-900">
						{{ title }}
					</span>
				</div>
				<p class="mb-6 break-words text-base font-normal leading-[21px] text-gray-700" v-if="subtitle">
					{{ subtitle }}
				</p>
				<slot></slot>
			</div>
			</div>

			<div class="mt-auto flex justify-center">
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
