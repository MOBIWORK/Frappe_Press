<template>
	<div class="flex h-screen overflow-hidden">
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

							<!-- Status Message -->
							<div class="text-center space-y-3">
								<h3 class="text-lg font-medium text-gray-900">
									{{ __('Almost Ready!') }}
								</h3>
								<p class="text-sm text-gray-600">
									{{ __('We are preparing your site. This usually takes a few moments...') }}
								</p>
								
								<!-- Simple Progress Indicator -->
								<div class="flex justify-center space-x-1 mt-4">
									<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
									<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
									<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: 'SignupLoginToSite',
	props: ['productId'],
	data() {
		return {
			product_trial_request: this.$route.query.product_trial_request,
			timeoutWarning: null,
			showTimeoutWarning: false,
			subdomain: this.$route.query.subdomain || null,
			lastLoaded: 0,
		};
	},
	mounted() {
		console.log('[LoginToSite] Mounted with:', {
			product_trial_request: this.product_trial_request,
			productId: this.productId,
			subdomain: this.subdomain
		});
		
		// Start status monitoring
		this.startStatusMonitoring();
		
		// Set timeout warning after 3 minutes
		this.timeoutWarning = setTimeout(() => {
			const status = this.$resources?.siteRequest?.doc?.status;
			if (!status || !['Error', 'Site Created'].includes(status)) {
				this.showTimeoutWarning = true;
			}
		}, 180000); // 3 minutes

		// Start polling for updates
		this.startPolling();
	},
	beforeUnmount() {
		if (this.timeoutWarning) {
			clearTimeout(this.timeoutWarning);
		}
		if (this.pollingInterval) {
			clearInterval(this.pollingInterval);
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
				auto: this.product_trial_request ? true : false,
				onSuccess: (doc) => {
					console.log('[LoginToSite] Site request loaded:', doc);
					this.lastLoaded = Date.now();
					this.handleStatusChange(doc.status);
				},
				onError: (error) => {
					console.log('[LoginToSite] Site request error:', error);
					// Retry after error
					setTimeout(() => {
						this.$resources.siteRequest.reload();
					}, 5000);
				},
				whitelistedMethods: {
					getLoginSid: {
						method: 'get_login_sid',
						onSuccess: (loginURL) => {
							console.log('[LoginToSite] Login URL received:', loginURL);
							window.open(loginURL, '_self');
						},
						onError: (error) => {
							console.log('[LoginToSite] Login error:', error);
						}
					},
				},
			};
		},
		addDomain() {
			return {
				url: 'press.api.site.add_domain',
				makeParams: () => {
					const siteName = this.$resources?.siteRequest?.doc?.site;
					return {
						name: siteName,
						domain: `${this.subdomain}.nhansu360.com`,
					};
				},
				auto: false,
				onSuccess: () => {
					console.log('[LoginToSite] Domain added successfully');
					this.$resources.siteRequest.getLoginSid.submit();
				},
				onError: (error) => {
					console.log('[LoginToSite] Error adding domain:', error);
					// Still proceed to login even if domain addition fails
					this.$resources.siteRequest.getLoginSid.submit();
				},
			};
		},
	},
	computed: {
		saasProduct() {
			return this.$resources?.saasProduct?.doc;
		},
		siteRequestStatus() {
			return this.$resources?.siteRequest?.doc?.status || null;
		},
	},
	methods: {
		startStatusMonitoring() {
			console.log('[LoginToSite] Starting status monitoring...');
			this.$nextTick(() => {
				if (this.$resources.siteRequest && this.product_trial_request) {
					this.$resources.siteRequest.reload();
				}
			});
		},
		
		startPolling() {
			// Poll for updates every 10 seconds
			this.pollingInterval = setInterval(() => {
				const status = this.siteRequestStatus;
				if (!status || !['Error', 'Site Created'].includes(status)) {
					if (!this.$resources.siteRequest?.loading) {
						this.$resources.siteRequest.reload();
					}
				}
			}, 10000);
		},
		
		handleStatusChange(status) {
			console.log('[LoginToSite] Status changed to:', status);
			
			switch (status) {
				case 'Site Created':
					console.log('[LoginToSite] Site created successfully!');
					this.showTimeoutWarning = false;
					// Auto login after a short delay
					setTimeout(() => this.loginToSite(), 1500);
					break;
					
				case 'Error':
					console.log('[LoginToSite] Site creation failed');
					this.showTimeoutWarning = false;
					break;
					
				default:
					console.log('[LoginToSite] Site creation in progress:', status);
					break;
			}
		},
		
		loginToSite() {
			console.log('[LoginToSite] Attempting to login to site...');
			
			// Check if we need to add custom domain first
			if (this.subdomain && this.subdomain.trim() !== '') {
				console.log('[LoginToSite] Adding custom domain:', `${this.subdomain}.nhansu360.com`);
				this.$resources.addDomain.submit();
			} else {
				// Direct login without custom domain
				console.log('[LoginToSite] Proceeding with direct login...');
				this.$resources.siteRequest.getLoginSid.submit();
			}
		},
		
		checkStatus() {
			console.log('[LoginToSite] Manual status check triggered');
			if (!this.$resources.siteRequest?.loading) {
				this.$resources.siteRequest.reload();
			}
		},
	},
};
</script>

<style scoped>
/* Simple styles */
</style>
