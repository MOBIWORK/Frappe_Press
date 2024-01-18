<template>
	<div class="h-full">
		<div
			:class="
				hasForgotPassword || hasResetPassword
					? 'grid grid-cols-1'
					: 'grid min-h-screen grid-cols-1 md:grid-cols-2'
			"
		>
			<div
				v-if="hasForgotPassword != 1 && hasResetPassword != 1"
				class="col-span-1 hidden items-center justify-center bg-[#F4F5F6] md:flex"
			>
				<img class="inline-block w-[500px]" src="../../assets/left_login.png" />
			</div>
			<div
				:class="
					hasForgotPassword || hasResetPassword
						? 'col-span-1'
						: 'col-span-1 flex justify-center md:bg-white'
				"
			>
				<div :class="top ? top : `mt-24`">
					<div class="flex justify-center">
						<slot name="logo">
							<img
								class="h-[30px]"
								src="../../assets/cropped-mbw.cloud_.10.png"
							/>
						</slot>
					</div>
					<div
						v-if="hasForgotPassword || hasResetPassword"
						class="container mx-auto mt-8 max-w-[450px] rounded-xl bg-white px-4 py-8 sm:mt-14 sm:px-6"
					>
						<div class="mb-6 text-center" v-if="title">
							<span class="text-base text-gray-900">{{ title }}</span>
						</div>
						<slot></slot>
					</div>
					<div
						v-else
						class="mx-auto mt-14 w-[80vw] rounded-xl bg-white px-4 sm:mt-5 sm:px-8 md:w-[50vw] lg:w-[450px]"
						:class="{ [py]: py, 'py-8': !py }"
					>
						<div class="mb-6 text-center" v-if="title">
							<span class="text-base text-gray-900">{{ title }}</span>
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

export default {
	name: 'LoginBox',
	props: ['title', 'logo', 'top', 'py'],
	components: {
		FCLogo,
		FrappeLogo
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
		}
	}
};
</script>
