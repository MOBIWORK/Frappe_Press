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
					</div>

					<!-- Login Card -->
					<div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
						<div class="space-y-6">
							<!-- Success Icon -->


							<!-- Show progress when completing -->
							<div v-if="showCompletionAnimation" class="space-y-4">
								<div class="text-center">
									<div class="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
										<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
										</svg>
									</div>
									<h3 class="text-lg font-medium text-gray-900 mb-2">
										{{ currentStep }}
									</h3>
									<p class="text-sm text-gray-500">
										{{ progressMessage }}
									</p>
									<p v-if="subdomain && subdomain.trim() !== ''" class="text-xs text-blue-600 mt-2">
										Đang thiết lập và kiểm tra domain cho site của bạn...
									</p>
								</div>
								
								<!-- Progress Bar -->
								<div class="space-y-3">
									<div class="flex justify-between text-sm">
										<span class="text-gray-600">{{ currentStep }}</span>
										<span class="text-gray-500 font-semibold">{{ progressPercentage }}%</span>
									</div>
									<div class="w-full bg-gray-200 rounded-full h-3">
										<div 
											class="h-3 rounded-full transition-all duration-700 ease-out shadow-sm bg-gradient-to-r from-green-500 to-green-600"
											:style="{ width: progressPercentage + '%' }"
										>
										</div>
									</div>
									<div class="text-xs text-gray-500 text-center">
										{{ __('Chuyển hướng sang thiết lập thông tin ...') }}
									</div>
								</div>
							</div>

							<!-- Login Button - Only show when not completing -->
							<Button
								v-else
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
						<!-- <div class="space-y-2">
							<h2 class="text-xl font-semibold text-gray-900">
								{{ __('Creating Your Site') }}
							</h2>
							<p class="text-sm text-gray-600 break-all">
								{{ this.$resources?.siteRequest?.doc?.domain || this.$resources?.siteRequest?.doc?.site }}
							</p>
						</div> -->
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
									{{ currentStep }}
								</h3>
								<!-- <p class="text-sm text-gray-600">
									{{ __('We are preparing your site. This usually takes a few moments...') }}
								</p> -->
								
								<!-- Progress Bar -->
								<div class="mt-6 space-y-3">
									<div class="flex justify-between text-sm">
										<span class="text-gray-600">{{ currentStep }}</span>
										<span class="text-gray-500 font-semibold">{{ progressPercentage }}%</span>
									</div>
									<div class="w-full bg-gray-200 rounded-full h-3">
										<div 
											class="h-3 rounded-full transition-all duration-700 ease-out shadow-sm"
											:class="progressBarClass"
											:style="{ width: progressPercentage + '%' }"
										>
											<!-- Shine effect -->
											<div v-if="!isError" class="h-full w-full bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-pulse"></div>
										</div>
									</div>
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
			selected_template: this.$route.query.selected_template || null,
			lastLoaded: 0,
			// Progress tracking
			progressPercentage: 0,
			currentStep: 'Đang khởi tạo...',
			progressMessage: 'Chuẩn bị tạo site của bạn...',
			progressInterval: null,
			showCompletionAnimation: false,
			progressSteps: [
				{ name: 'Khởi tạo môi trường', duration: 15000, target: 12 },
				{ name: 'Tạo cấu trúc site', duration: 60000, target: 30 },
				{ name: 'Cài đặt ứng dụng', duration: 60000, target: 55 },
				{ name: 'Cấu hình cơ sở dữ liệu', duration: 45000, target: 75 },
				{ name: 'Thiết lập web server', duration: 30000, target: 90 },
				{ name: 'Đang hoàn tất...', duration: 8000, target: 98 }
			],
			currentStepIndex: 0,
			stepStartTime: null,
			loginInProgress: false, // Flag to prevent multiple login attempts
		};
	},
	mounted() {
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

		// Start progress simulation if we have a trial request
		if (this.product_trial_request) {
			setTimeout(() => {
				if (!this.progressInterval) {
					this.startProgress();
				}
			}, 1000); // Start after 1 second
		}
	},
	beforeUnmount() {
		if (this.timeoutWarning) {
			clearTimeout(this.timeoutWarning);
		}
		if (this.pollingInterval) {
			clearInterval(this.pollingInterval);
		}
		// Cleanup progress interval
		this.stopProgress();
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
					this.lastLoaded = Date.now();
					this.handleStatusChange(doc.status);
				},
				onError: () => {
					// Retry after error
					setTimeout(() => {
						this.$resources.siteRequest.reload();
					}, 5000);
				},
				whitelistedMethods: {
					getLoginSid: {
						method: 'get_login_sid',
						onSuccess: (loginURL) => {
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
						domain: this.productId === 'mbw_cms' || this.productId === 'go1_cms' 
							? `${this.subdomain}.nhansu360.com`
							: `${this.subdomain}.${this.saasProduct?.domain}`,
					};
				},
				auto: false,
				onSuccess: (result) => {
					console.log('[LoginToSite] Domain added successfully:', result);
					// Don't call getLoginSid here, let addDomainAndWait handle the timing
				},
				onError: (error) => {
					console.log('[LoginToSite] Domain addition failed:', error);
					// Still proceed to login even if domain addition fails
					// The server will handle domain validation
				},
			};
		},
		saveLanguage() {
			return {
				url: 'press.api.site.save_setup_wizard_language',
				makeParams: ({ lang_code }) => ({ lang_code }),
			};
		},
		checkDomainStatus() {
			return {
				url: 'press.api.site.get_domain_status',
				makeParams: () => {
					const siteName = this.$resources?.siteRequest?.doc?.site;
					const domain = this.productId === 'mbw_cms' || this.productId === 'go1_cms'
						? `${this.subdomain}.nhansu360.com`
						: `${this.subdomain}.${this.saasProduct?.domain}`;
					return {
						name: siteName,
						domain: domain,
					};
				},
				auto: false,
				onSuccess: () => {
					// Domain status check completed
				},
				onError: () => {
					// Domain status check failed
				},
			};
		},
		handleCmsSiteCreation() {
				return {
					url: 'press.api.app_cms.handle_cms_site_creation',
					makeParams: () => {
						const siteName = this.$resources?.siteRequest?.doc?.site;

						return {
							site_name: siteName,
							product_id: this.productId,
							subdomain: this.subdomain,
							template_name: this.selected_template
						};
					},
					auto: false,
					onSuccess: (data) => {
						console.log('CMS site creation handled successfully:', data);
					},
					onError: (error) => {
						console.error('Error handling CMS site creation:', error);
					}
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
		isError() {
			return this.siteRequestStatus === 'Error' || this.currentStep === 'Có lỗi xảy ra';
		},
		isComplete() {
			return this.siteRequestStatus === 'Site Created' || this.progressPercentage >= 100;
		},
		shouldShowProgressInSuccess() {
			return this.siteRequestStatus === 'Site Created' && this.showCompletionAnimation;
		},
		progressBarClass() {
			if (this.isError) {
				return 'bg-gradient-to-r from-red-500 to-red-600';
			} else if (this.isComplete) {
				return 'bg-gradient-to-r from-green-500 to-green-600';
			} else {
				return 'bg-gradient-to-r from-blue-500 to-blue-600';
			}
		},
	},
	methods: {
		startStatusMonitoring() {
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
			switch (status) {
				case 'Site Created':
					this.showTimeoutWarning = false;
					this.completeProgress();
					this.showCompletionAnimation = true;

					// Wait for domain setup if we have subdomain
					if (this.subdomain && this.subdomain.trim() !== '') {
						this.setupDomainAndWaitForReady();

						// Emergency fallback after 6 minutes
						setTimeout(() => {
							if (!this.loginInProgress) {
								this.proceedToLogin();
							}
						}, 360000);

					} else {
						// No custom domain needed, proceed directly
						setTimeout(() => this.proceedToLogin(), 3000);
					}
					break;
					
				case 'Error':
					this.showTimeoutWarning = false;
					this.stopProgress();
					this.currentStep = 'Có lỗi xảy ra';
					this.progressMessage = 'Không thể tạo site. Vui lòng thử lại.';
					break;
					
				case 'Wait for Site':
				case 'New Site':
				case 'Prefilling Setup Wizard':
					// Start progress if not already started
					if (!this.progressInterval) {
						this.startProgress();
					}
					break;
					
				default:
					if (status) {
						// Start progress for any other status
						if (!this.progressInterval) {
							this.startProgress();
						}
					}
					break;
			}
		},

		setupDomainAndWaitForReady() {
			// Update progress to show domain setup
			this.currentStep = 'Đang thiết lập domain...';
			this.progressMessage = 'Đang cấu hình domain cho site của bạn. Quá trình này có thể mất vài phút...';

			// Add domain first
			this.$resources.addDomain.submit();

			// Maximum timeout fallback (5 minutes)
			setTimeout(() => {
				this.proceedToLogin();
			}, 300000);

			// Start checking domain status after delay
			setTimeout(() => {
				this.waitForDomainReady();
			}, 10000);
		},

		waitForDomainReady() {
			const maxAttempts = 30; // Maximum 30 attempts (about 5 minutes)
			const checkInterval = 10000; // Check every 10 seconds
			let attempts = 0;

			const checkDomainStatus = () => {
				attempts++;

				// Update progress message
				this.progressMessage = `Đang đợi domain sẵn sàng. Quá trình này có thể mất vài phút...`;

				// Check domain status using the API
				this.$resources.checkDomainStatus.submit();

				// Wait for the API response
				setTimeout(() => {
					const result = this.$resources.checkDomainStatus.data;
					const error = this.$resources.checkDomainStatus.error;

					// If API call failed, try fallback after many failures
					if (error || (result && !result.success)) {
						if (attempts >= 10) {
							this.fallbackPingDomain();
							return;
						}
					}

					// ONLY proceed when domain is truly Active
					if (result && result.success && result.status === 'Active') {
						this.proceedToLogin();
						return;
					}

					// Check if we've exceeded max attempts
					if (attempts >= maxAttempts) {
						this.proceedToLogin();
						return;
					}

					// Domain not ready yet, continue checking
					setTimeout(checkDomainStatus, checkInterval);

				}, 2000); // Wait 2 seconds for API response
			};

			// Start checking
			checkDomainStatus();
		},

		proceedToLogin() {
			// Prevent multiple login attempts
			if (this.loginInProgress) {
				return;
			}

			this.loginInProgress = true;

			// Update progress to show we're ready
			this.currentStep = '';
			this.progressMessage = 'Đang chuyển hướng đến site của bạn...';
			// Handle CMS if needed
			if (this.productId === 'mbw_cms' && this.selected_template) {
				const siteName = this.$resources?.siteRequest?.doc?.site;

				if (!siteName) {
					console.error('CMS Error: site_name is null/undefined');
					return;
				}

				this.$resources.handleCmsSiteCreation.submit();
			}
			// Save language for setup wizard
			this.saveLanguageForSetupWizard();

			// Verify domain is ready before login if we have subdomain
			if (this.subdomain && this.subdomain.trim() !== '') {
				this.verifyDomainBeforeLogin();
			} else {
				this.performActualLogin();
			}
		},

		fallbackPingDomain() {
			const domain = this.productId === 'mbw_cms' || this.productId === 'go1_cms'
				? `${this.subdomain}.nhansu360.com`
				: `${this.subdomain}.${this.saasProduct?.domain}`;

			// Try to load a small image from the domain to test connectivity
			const testUrl = `https://${domain}/favicon.ico?t=${Date.now()}`;
			const img = new Image();

			img.onload = () => {
				this.proceedToLogin();
			};

			img.onerror = () => {
				// Even if ping fails, proceed to login after a short delay
				setTimeout(() => {
					this.proceedToLogin();
				}, 5000);
			};

			// Set a timeout to prevent infinite waiting
			setTimeout(() => {
				if (!this.loginInProgress) {
					this.proceedToLogin();
				}
			}, 15000);

			img.src = testUrl;
		},

		verifyDomainBeforeLogin() {
			// Check domain status one final time before login
			this.$resources.checkDomainStatus.submit();

			setTimeout(() => {
				const result = this.$resources.checkDomainStatus.data;

				if (result && result.success && result.status === 'Active') {
					this.performActualLogin();
				} else {
					this.finalPingBeforeLogin();
				}
			}, 3000); // Wait 3 seconds for API response
		},

		finalPingBeforeLogin() {
			const domain = this.productId === 'mbw_cms' || this.productId === 'go1_cms'
				? `${this.subdomain}.nhansu360.com`
				: `${this.subdomain}.${this.saasProduct?.domain}`;

			const testUrl = `https://${domain}/favicon.ico?t=${Date.now()}`;
			const img = new Image();

			img.onload = () => {
				this.performActualLogin();
			};

			img.onerror = () => {
				this.performActualLogin();
			};

			// Timeout after 10 seconds
			setTimeout(() => {
				this.performActualLogin();
			}, 10000);

			img.src = testUrl;
		},

		performActualLogin() {
			// This is the actual login that triggers navigation
			this.$resources.siteRequest.getLoginSid.submit();
		},

		loginToSite() {
			// This method is called when user manually clicks the login button
			this.proceedToLogin();
		},
		
		saveLanguageForSetupWizard() {
			// Get language from multiple sources (priority order)
			let currentLang = null;
			
			// 1. Try localStorage first (where language is stored during site creation)
			currentLang = localStorage.getItem('lang');
			
			// 2. Fallback to URL parameters if localStorage is empty
			if (!currentLang) {
				currentLang = this.$route.query.lang;
			}
			
			// 3. Default fallback
			if (!currentLang) {
				currentLang = 'vi';
			}
			
			console.log('saveLanguageForSetupWizard - Language found:', currentLang);
			
			// Save to server-side using API
			if (currentLang) {
				this.$resources.saveLanguage.submit({
					lang_code: currentLang
				});
				
				// Also set cookies and localStorage as backup
				document.cookie = `setup_wizard_lang=${currentLang}; path=/; max-age=3600; SameSite=Lax`;
				localStorage.setItem('setup_wizard_lang', currentLang);
				
				console.log('saveLanguageForSetupWizard - Saved language:', currentLang);
			}
		},
		
		checkStatus() {
			if (!this.$resources.siteRequest?.loading) {
				this.$resources.siteRequest.reload();
			}
		},

		// Progress methods
		startProgress() {
			this.progressPercentage = 0;
			this.currentStepIndex = 0;
			this.stepStartTime = Date.now();
			this.currentStep = this.progressSteps[0].name;
			this.progressMessage = 'Đang thiết lập môi trường...';

			this.progressInterval = setInterval(() => {
				this.updateProgress();
			}, 200); // Update every 200ms for smooth animation
		},

		updateProgress() {
			if (this.currentStepIndex >= this.progressSteps.length) {
				return;
			}

			const currentStepData = this.progressSteps[this.currentStepIndex];
			const elapsed = Date.now() - this.stepStartTime;
			const stepProgress = Math.min(elapsed / currentStepData.duration, 1);

			// Calculate target progress for current step
			const previousTarget = this.currentStepIndex > 0 ? 
				this.progressSteps[this.currentStepIndex - 1].target : 0;
			const targetProgress = currentStepData.target;

			// Smooth progress interpolation
			const newProgress = previousTarget + (targetProgress - previousTarget) * this.easeOutCubic(stepProgress);
			this.progressPercentage = Math.min(Math.round(newProgress), 98); // Never exceed 98% until completion

			// Update progress message
			this.updateProgressMessage();

			// Move to next step if current step is complete
			if (stepProgress >= 1 && this.currentStepIndex < this.progressSteps.length - 1) {
				this.currentStepIndex++;
				this.stepStartTime = Date.now();
				this.currentStep = this.progressSteps[this.currentStepIndex].name;
			}
		},

		updateProgressMessage() {
			const estimatedTime = Math.max(90 - Math.floor(this.progressPercentage / 1.5), 10);
			this.progressMessage = `Còn khoảng ${estimatedTime} giây nữa...`;
		},

		completeProgress() {
			this.stopProgress();
			
			// Animate to 100% smoothly
			const animateToComplete = () => {
				if (this.progressPercentage < 100) {
					this.progressPercentage = Math.min(this.progressPercentage + 2, 100);
					setTimeout(animateToComplete, 50);
				} else {
					// Only show "Hoàn tất" when truly at 100%
					this.currentStep = '🎉 Hoàn tất!';
					this.progressMessage = 'Site của bạn đã sẵn sàng!';
				}
			};
			
			animateToComplete();
		},

		stopProgress() {
			if (this.progressInterval) {
				clearInterval(this.progressInterval);
				this.progressInterval = null;
			}
		},

		// Easing function for smooth animation
		easeOutCubic(t) {
			return 1 - Math.pow(1 - t, 3);
		},
	},
};
</script>

<style scoped>
/* Simple styles */
</style>
