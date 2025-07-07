<template>
	<div
		class="flex h-screen w-screen flex-col items-center justify-center bg-gray-600 bg-opacity-50"
		v-if="$resources?.siteRequest?.doc?.status && !['Error', 'Site Created'].includes($resources?.siteRequest?.doc?.status)"
	>
		<SignupSpinner />
		<p class="text-white">
			{{ __('Completing setup') }}
		</p>
	</div>
	<div class="flex h-screen overflow-hidden" v-else>
		<div class="w-full overflow-auto">
			<!-- Success State - Beautiful Login Screen -->
			<div
				v-if="$resources?.siteRequest?.doc?.status === 'Site Created'"
				class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4"
			>
				<div class="w-full max-w-md">
					<!-- Logo and Title -->
					<div class="text-center mb-8">
						<div v-if="saasProduct" class="mb-6">
							<img
								class="mx-auto h-16 w-16 rounded-xl shadow-lg"
								:src="saasProduct?.logo"
								:alt="saasProduct?.title"
							/>
							<h1 class="mt-4 text-2xl font-bold text-gray-900">
								{{ saasProduct?.title }}
							</h1>
						</div>
						<div class="space-y-2">
							<h2 class="text-xl font-semibold text-gray-900">
								{{ __('🎉 Site Created Successfully!') }}
							</h2>
							<p class="text-sm text-gray-600">
								{{ __('Your trial site is ready at') }}
							</p>
							<p class="text-sm font-medium text-blue-600 break-all">
								{{ $resources?.siteRequest?.doc?.domain || $resources?.siteRequest?.doc?.site }}
							</p>
						</div>
					</div>

					<!-- Login Card -->
					<div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
						<div class="space-y-6">
							<!-- Success Icon -->
							<div class="text-center">
								<div class="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
									<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
									</svg>
								</div>
								<h3 class="text-lg font-medium text-gray-900 mb-2">
									{{ __('Ready to Login') }}
								</h3>
								<p class="text-sm text-gray-500">
									{{ __('Click below to access your new site') }}
								</p>
							</div>

							<!-- Login Button -->
							<Button
								variant="solid"
								class="w-full py-3 text-base font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all duration-200 transform hover:scale-[1.02] shadow-lg"
								@click="loginToSite"
								:loading="this.$resources?.siteRequest?.getLoginSid.loading"
							>
								<span class="flex items-center justify-center">
									<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
									</svg>
									{{ __('Access Your Site') }}
								</span>
							</Button>

							<!-- Error Message -->
							<div v-if="this.$resources?.siteRequest?.getLoginSid.error" 
								class="p-4 bg-red-50 border border-red-200 rounded-xl">
								<p class="text-sm text-red-600 text-center">
									{{ this.$resources?.siteRequest?.getLoginSid.error }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Error State -->
			<div
				v-else-if="$resources?.siteRequest?.doc?.status === 'Error'"
				class="min-h-screen bg-gradient-to-br from-red-50 via-white to-pink-50 flex items-center justify-center p-4"
			>
				<div class="w-full max-w-md">
					<div class="text-center mb-8">
						<div v-if="saasProduct" class="mb-6">
							<img
								class="mx-auto h-16 w-16 rounded-xl shadow-lg opacity-75"
								:src="saasProduct?.logo"
								:alt="saasProduct?.title"
							/>
							<h1 class="mt-4 text-2xl font-bold text-gray-900">
								{{ saasProduct?.title }}
							</h1>
						</div>
					</div>

					<div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
						<div class="text-center space-y-6">
							<!-- Error Icon -->
							<div class="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
								<svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
								</svg>
							</div>

							<div class="space-y-3">
								<h3 class="text-lg font-medium text-gray-900">
									{{ __('Site Creation Failed') }}
								</h3>
								<p class="text-sm text-gray-600">
									{{ $resources?.siteRequest?.doc?.domain || $resources?.siteRequest?.doc?.site }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Progress State -->
			<div
				v-else
				class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4"
			>
				<div class="w-full max-w-md">
					<div class="text-center mb-8">
						<div v-if="saasProduct" class="mb-6">
							<img
								class="mx-auto h-16 w-16 rounded-xl shadow-lg"
								:src="saasProduct?.logo"
								:alt="saasProduct?.title"
							/>
							<h1 class="mt-4 text-2xl font-bold text-gray-900">
								{{ saasProduct?.title }}
							</h1>
						</div>
						<div class="space-y-2">
							<h2 class="text-xl font-semibold text-gray-900">
								{{ __('Creating Your Site') }}
							</h2>
							<p class="text-sm text-gray-600 break-all">
								{{ this.$resources?.siteRequest?.doc?.domain || this.$resources?.siteRequest?.doc?.site }}
							</p>
						</div>
					</div>

					<div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
						<div class="space-y-6">
							<!-- Progress Animation -->
							<div class="flex justify-center">
								<div class="relative">
									<div class="w-16 h-16 border-4 border-blue-200 rounded-full animate-pulse"></div>
									<div class="absolute top-0 left-0 w-16 h-16 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
								</div>
							</div>

							<!-- Progress Bar -->
							<div class="space-y-3">
								<div class="flex justify-between text-sm">
									<span class="text-gray-600">{{ currentBuildStep }}</span>
									<span class="text-gray-500">{{ Math.round(progressCount) }}%</span>
								</div>
								<div class="w-full bg-gray-200 rounded-full h-2">
									<div 
										class="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
										:style="{ width: progressCount + '%' }"
									></div>
								</div>
							</div>

							<!-- Status Message -->
							<div class="text-center">
								<p class="text-sm text-gray-600">
									{{ __('Please wait while we prepare your site...') }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
<script>
import LoginBox from '../../components/auth/LoginBox.vue';
import Spinner from '../../components/Spinner.vue';
import { Progress } from 'frappe-ui';

export default {
	name: 'SignupLoginToSite',
	props: ['productId'],
	components: {
		LoginBox,
		Progress,
		SignupSpinner: Spinner,
	},
	data() {
		return {
			product_trial_request: this.$route.query.product_trial_request,
			progressCount: 0,
			currentBuildStep: 'Preparing for build',
			timeoutWarning: null,
			showTimeoutWarning: false,
		};
	},
	mounted() {
		// Set timeout warning after 2 minutes
		this.timeoutWarning = setTimeout(() => {
			if (!['Error', 'Site Created'].includes(this.$resources?.siteRequest?.doc?.status)) {
				this.showTimeoutWarning = true;
			}
		}, 120000); // 2 minutes
	},
	beforeUnmount() {
		if (this.timeoutWarning) {
			clearTimeout(this.timeoutWarning);
		}
	},
	resources: {
		saasProduct() {
			return {
				type: 'document',
				doctype: 'Product Trial',
				name: this.productId,
				auto: true,
			};
		},
		siteRequest() {
			return {
				type: 'document',
				doctype: 'Product Trial Request',
				name: this.product_trial_request,
				realtime: true,
				auto: true,
				onSuccess(doc) {
					console.log('doc : >>>>>>>>>>>>>>>>>>>>>>>>>', doc);
					if (doc.status == 'Site Created') {
						this.showTimeoutWarning = false;
						this.loginToSite();
					} else if (
						doc.status == 'Wait for Site' ||
						doc.status == 'Prefilling Setup Wizard'
					) {
						this.$resources.siteRequest.getProgress.reload();
					}
				},
				whitelistedMethods: {
					getProgress: {
						method: 'get_progress',
						makeParams() {
							return {
								current_progress:
									this.$resources.siteRequest.getProgress.data?.progress || 0,
							};
						},
						onSuccess: (data) => {
							if (data.status === 'Site Created') {
								this.showTimeoutWarning = false;
								return this.loginToSite();
							}

							const currentStepMap = {
								'Wait for Site': 'Creating your site',
								'New Site': 'Creating your site',
								'Prefilling Setup Wizard': 'Setting up your site',
								'Update Site Configuration': 'Setting up your site',
								'Enable Scheduler': 'Setting up your site',
								'Bench Setup NGINX': 'Setting up your site',
								'Reload NGINX': 'Setting up your site',
							};

							this.currentBuildStep =
								currentStepMap[data.current_step] ||
								data.current_step ||
								this.currentBuildStep;
							this.progressCount += 1;

							if (
								!(
									this.$resources.siteRequest.getProgress.error &&
									this.progressCount <= 10
								)
							) {
								this.progressCount = Math.round(data.progress * 10) / 10;
								setTimeout(() => {
									if (
										['Site Created', 'Error'].includes(
											this.$resources.siteRequest.doc.status,
										)
									)
										return;

									this.$resources.siteRequest.getProgress.reload();
								}, 2000);
							}
						},
						onError: (error) => {
							console.error('Progress check error:', error);
							// Still continue checking but show warning
							this.showTimeoutWarning = true;
						},
					},
					getLoginSid: {
						method: 'get_login_sid',
						onSuccess(loginURL) {
							window.open(loginURL, '_self');
						},
					},
				},
			};
		},
	},
	computed: {
		saasProduct() {
			return this.$resources.saasProduct.doc;
		},
	},
	methods: {
		loginToSite() {
			this.$resources.siteRequest.getLoginSid.submit();
		},
		checkStatus() {
			// Force reload the siteRequest to check current status
			this.$resources.siteRequest.reload();
			this.showTimeoutWarning = false;
			
			// Reset timeout
			if (this.timeoutWarning) {
				clearTimeout(this.timeoutWarning);
			}
			this.timeoutWarning = setTimeout(() => {
				if (!['Error', 'Site Created'].includes(this.$resources?.siteRequest?.doc?.status)) {
					this.showTimeoutWarning = true;
				}
			}, 120000);
		},
	},
};
</script>
