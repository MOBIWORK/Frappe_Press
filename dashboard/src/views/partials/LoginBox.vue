<template>
	<div class="h-full">
		<div class="grid min-h-screen grid-cols-1 md:grid-cols-2">
			<div class="col-span-1 hidden h-screen md:flex">
				<img
					class="inline-block h-full w-full object-cover"
					src="../../assets/left_content.svg"
				/>
			</div>
			<div
				class="relative col-span-1 flex justify-center md:overflow-auto md:bg-white"
			>
				<div
					class="absolute left-1/2 top-1/2 h-full -translate-x-1/2 -translate-y-1/2"
					:class="hasSetupAccount ? 'py-[8%]' : 'py-[20%]'"
				>
					<div class="flex justify-center">
						<slot name="logo">
							<img src="../../assets/logo_eov.png" />
						</slot>
					</div>
					<div
						class="mx-auto w-[80vw] rounded-xl bg-white px-4 sm:px-8 md:w-[50vw] lg:w-[450px]"
						:class="{ [py]: py, 'py-8': !py }"
					>
						<div class="mb-6 text-center" v-if="title">
							<span class="text-base text-gray-900">{{ title }}</span>
						</div>
						<div class="mb-4 w-max">
							<SelectLanguage></SelectLanguage>
						</div>
						<slot></slot>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import FCLogo from '@/components/icons/FCLogo.vue';
import FrappeLogo from '@/components/icons/FrappeLogo.vue';
import { notify } from '@/utils/toast';
import SelectLanguage from '@/components/global/SelectLanguage.vue';

export default {
	name: 'LoginBox',
	props: ['title', 'logo', 'top', 'py'],
	components: {
		FCLogo,
		FrappeLogo,
		SelectLanguage
	},
	mounted() {
		const params = new URLSearchParams(window.location.search);

		if (params.get('showRemoteLoginError')) {
			notify({
				title: 'Token Invalid or Expired',
				color: 'red',
				icon: 'x'
			});
		}
	},
	methods: {
		redirectForFrappeioAuth() {
			window.location = '/f-login';
		}
	},
	computed: {
		hasForgotPassword() {
			return this.$route.name == 'Login' && this.$route.query.forgot;
		},
		hasResetPassword() {
			return this.$route.name == 'Reset Password';
		},
		hasSetupAccount() {
			return ['Setup Account', 'Setup Account Billing'].includes(
				this.$route.name
			);
		}
	}
};
</script>
