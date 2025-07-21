<template>
	<!-- Main Loading State - Show when we have a request but site isn't created yet -->
	<div
		class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4"
		v-if="shouldShowMainLoading"
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
						{{ __('Setting Up Your Site') }}
					</h2>
					<p class="text-sm text-gray-600 break-all">
						{{ this.$resources?.siteRequest?.doc?.domain || this.$resources?.siteRequest?.doc?.site || 'Loading...' }}
					</p>
				</div>
			</div>

			<div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
				<div class="space-y-6">
					<!-- Enhanced Loading Animation -->
					<div class="flex justify-center">
						<div class="relative">
							<div class="w-16 h-16 border-4 border-blue-200 rounded-full animate-pulse"></div>
							<div class="absolute top-0 left-0 w-16 h-16 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
						</div>
					</div>

					<!-- Status Message -->
					<div class="text-center space-y-3">
						<h3 class="text-lg font-medium text-gray-900">
							{{ currentBuildStep || __('Completing setup') }}
						</h3>
						<p class="text-sm text-gray-600">
							{{ __('We are preparing your site. This usually takes a few moments...') }}
						</p>
						
						<!-- Real Progress Bar - Only show when we have real progress data -->
						<div v-if="progressCount > 0" class="space-y-3 mt-6">
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
							<div class="text-xs text-gray-500">
								Progress from server: {{ Math.round(progressCount) }}%
							</div>
						</div>

						<!-- Simple Loading Indicator when no progress data -->
						<div v-else class="flex justify-center space-x-1 mt-4">
							<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
							<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
							<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
						</div>
					</div>

					<!-- Timeout Warning -->
					<div v-if="showTimeoutWarning" class="p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
						<div class="flex items-center space-x-3">
							<svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"></path>
							</svg>
							<div>
								<p class="text-sm font-medium text-yellow-800">
									{{ __('Taking longer than expected') }}
								</p>
								<p class="text-xs text-yellow-700">
									{{ __('Please be patient, setup is still in progress...') }}
								</p>
							</div>
						</div>
						<button 
							@click="checkStatus"
							class="mt-3 w-full text-xs bg-yellow-100 hover:bg-yellow-200 text-yellow-800 py-2 px-3 rounded-lg transition-colors duration-200"
						>
							{{ __('Check Status') }}
						</button>
					</div>
				</div>
			</div>
		</div>
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

							<!-- Status Message -->
							<div class="text-center space-y-3">
								<h3 class="text-lg font-medium text-gray-900">
									{{ __('Almost Ready!') }}
								</h3>
								<p class="text-sm text-gray-600">
									{{ __('We are preparing your site. This usually takes a few moments...') }}
								</p>
								
								<!-- Job Progress Bar - Show even without job ID initially -->
								<div v-if="showProgressBar" class="space-y-3 mt-6">
									<!-- Show real progress if we have job data -->
									<div v-if="jobProgress.totalSteps > 0">
										<div class="flex justify-between text-sm">
											<span class="text-gray-600">{{ jobProgress.currentStep }}</span>
											<span class="text-gray-500">{{ Math.round(jobProgress.percentage) }}%</span>
										</div>
										<div class="w-full bg-gray-200 rounded-full h-2">
											<div 
												class="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
												:style="{ width: jobProgress.percentage + '%' }"
											></div>
										</div>
										<div class="text-xs text-gray-500">
											{{ jobProgress.completedSteps }} / {{ jobProgress.totalSteps }} steps completed
										</div>
									</div>
									
									<!-- Show simulated progress when no job data yet -->
									<div v-else>
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
										<div class="text-xs text-gray-500">
											Setting up your site...
										</div>
									</div>
								</div>

								<!-- Fallback Progress Indicator -->
								<div v-else class="flex justify-center space-x-1 mt-4">
									<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
									<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
									<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
								</div>
							</div>

							<!-- Timeout Warning -->
							<div v-if="showTimeoutWarning" class="p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
								<div class="flex items-center space-x-3">
									<svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"></path>
									</svg>
									<div>
										<p class="text-sm font-medium text-yellow-800">
											{{ __('Taking longer than expected') }}
										</p>
										<p class="text-xs text-yellow-700">
											{{ __('Please be patient, setup is still in progress...') }}
										</p>
									</div>
								</div>
								<button 
									@click="checkStatus"
									class="mt-3 w-full text-xs bg-yellow-100 hover:bg-yellow-200 text-yellow-800 py-2 px-3 rounded-lg transition-colors duration-200"
								>
									{{ __('Check Status') }}
								</button>
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
			subdomain: this.$route.query.subdomain || null, // Lấy subdomain từ query params
			// Job progress tracking
			jobProgress: {
				percentage: 0,
				currentStep: 'Initializing...',
				completedSteps: 0,
				totalSteps: 0,
				steps: []
			},
		};
	},
	mounted() {
		console.log('=== LoginToSite Debug Info ===');
		console.log('Route query:', this.$route.query);
		console.log('product_trial_request:', this.product_trial_request);
		console.log('productId:', this.productId);
		console.log('subdomain:', this.subdomain);
		
		// Set timeout warning after 2 minutes
		this.timeoutWarning = setTimeout(() => {
			if (!['Error', 'Site Created'].includes(this.$resources?.siteRequest?.doc?.status)) {
				this.showTimeoutWarning = true;
			}
		}, 120000); // 2 minutes

		// Subscribe to job updates via socket (like JobPage.vue)
		this.$socket.on('agent_job_update', this.handleJobUpdate);
		
		// Reload every minute as fallback (like JobPage.vue)
		this.reloadInterval = setInterval(() => {
			this.reloadProgress();
		}, 1000 * 60);
		
		// Check resources after mount
		this.$nextTick(() => {
			console.log('Resources after mount:', this.$resources);
			console.log('siteRequest resource:', this.$resources?.siteRequest);
		});
	},
	beforeUnmount() {
		if (this.timeoutWarning) {
			clearTimeout(this.timeoutWarning);
		}
		
		// Cleanup progress interval
		if (this.progressInterval) {
			clearInterval(this.progressInterval);
		}
		
		// Cleanup reload interval (like JobPage.vue)
		if (this.reloadInterval) {
			clearInterval(this.reloadInterval);
		}
		
		// Cleanup socket listeners (like JobPage.vue)
		this.$socket.emit('doc_unsubscribe', 'Agent Job', this.currentJobId);
		this.$socket.off('agent_job_update');
	},
	resources: {
		saasProduct() {
			return {
				type: 'document',
				doctype: 'Product Trial',
				name: this.productId,
				auto: true,
				onSuccess(doc) {
					console.log('saasProduct loaded:', doc);
				},
				onError(error) {
					console.error('saasProduct error:', error);
				}
			};
		},
		siteRequest() {
			console.log('Setting up siteRequest resource with name:', this.product_trial_request);
			return {
				type: 'document',
				doctype: 'Product Trial Request',
				name: this.product_trial_request,
				realtime: true,
				auto: this.product_trial_request ? true : false, // Only auto if we have a name
				onSuccess(doc) {
					console.log('siteRequest loaded successfully:', doc);
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
				onError(error) {
					console.error('siteRequest error:', error);
					console.error('Failed to load Product Trial Request:', this.product_trial_request);
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
		addDomain() {
			return {
				url: 'press.api.site.add_domain',
				makeParams: () => {
					const siteName = this.$resources?.siteRequest?.doc?.site;
					console.log('Adding domain with params:', siteName, `${this.subdomain}.nhansu360.com`);
					return {
						name: siteName,
						domain: `${this.subdomain}.nhansu360.com`,
					};
				},
				auto: false,
				onSuccess: () => {
					console.log('Domain added successfully, proceeding to login');
					// Proceed to actual login after domain is added
					this.$resources.siteRequest.getLoginSid.submit();
				},
				onError: (error) => {
					console.error('Error adding domain:', error);
					// Still proceed to login even if domain addition fails
					this.$resources.siteRequest.getLoginSid.submit();
				},
			};
		},
		siteCreationJob() {
			return {
				type: 'document',
				doctype: 'Agent Job',
				name: () => this.currentJobId,
				auto: false,
				realtime: true,
				transform(job) {
					if (!job) return null;
					
					// Calculate progress percentage based on completed steps
					const completedSteps = job.steps?.filter(step => step.status === 'Success').length || 0;
					const totalSteps = job.steps?.length || 1;
					const percentage = Math.round((completedSteps / totalSteps) * 100);
					
					// Find current running step
					const runningStep = job.steps?.find(step => step.status === 'Running');
					const currentStepName = runningStep?.step_name || 
						(job.status === 'Success' ? 'Completed' : 'Processing...');
					
					return {
						...job,
						progress: {
							percentage,
							currentStep: currentStepName,
							completedSteps,
							totalSteps,
							status: job.status
						}
					};
				},
				onSuccess(job) {
					if (job && job.progress) {
						this.jobProgress = job.progress;
					}
				}
			};
		},
	},
	computed: {
		saasProduct() {
			return this.$resources?.saasProduct?.doc;
		},
		currentJobId() {
			// Get job ID from site request document with safe access
			const jobId = this.$resources?.siteRequest?.doc?.job || null;
			console.log('Current Job ID:', jobId);
			console.log('Site Request Doc:', this.$resources?.siteRequest?.doc);
			return jobId;
		},
		showProgressBar() {
			// Show progress bar when site is being created (more lenient condition)
			const status = this.$resources?.siteRequest?.doc?.status;
			const shouldShow = status && !['Error', 'Site Created'].includes(status);
			console.log('Show Progress Bar:', shouldShow, 'Status:', status, 'Job ID:', this.currentJobId);
			
			// Force show progress bar if we're in creating state regardless of status
			const isCreating = this.product_trial_request && !status; // If we have a request but no status yet
			const forceShow = isCreating || shouldShow;
			
			console.log('Force Show Progress Bar:', forceShow, 'Is Creating:', isCreating, 'Should Show:', shouldShow);
			return forceShow;
		},
		// Safe access to site request status
		siteRequestStatus() {
			return this.$resources?.siteRequest?.doc?.status || null;
		},
		// Add computed to check if we should show the main loading state
		shouldShowMainLoading() {
			const hasRequest = !!this.product_trial_request;
			const hasDoc = !!this.$resources?.siteRequest?.doc;
			const status = this.$resources?.siteRequest?.doc?.status;
			const isInProgress = hasRequest && (!hasDoc || (status && !['Error', 'Site Created'].includes(status)));
			
			console.log('Should Show Main Loading:', isInProgress, 'Has Request:', hasRequest, 'Has Doc:', hasDoc, 'Status:', status);
			return isInProgress;
		},
	},
	methods: {
		loginToSite() {
			console.log('LoginToSite called with subdomain:', this.subdomain);
			console.log('Site info:', this.$resources?.siteRequest?.doc?.site);
			console.log('Full siteRequest doc:', this.$resources?.siteRequest?.doc);
			
			// Safe access to resources
			if (!this.$resources || !this.$resources.siteRequest) {
				console.error('Resources not available yet');
				return;
			}
			
			// Check if we have subdomain and should add domain
			if (this.subdomain && this.$resources.siteRequest.doc?.site) {
				console.log('Calling add_domain before login');
				console.log('addDomain resource status:', this.$resources.addDomain);
				if (this.$resources.addDomain) {
					this.$resources.addDomain.submit();
				}
			} else {
				// Proceed directly to login if no subdomain
				console.log('No subdomain found, proceeding directly to login. Subdomain:', this.subdomain, 'Site:', this.$resources.siteRequest.doc?.site);
				if (this.$resources.siteRequest.getLoginSid) {
					this.$resources.siteRequest.getLoginSid.submit();
				}
			}
		},
		checkStatus() {
			// Safe access check
			if (!this.$resources || !this.$resources.siteRequest) {
				console.error('Resources not available for status check');
				return;
			}
			
			// Force reload the siteRequest to check current status
			this.$resources.siteRequest.reload();
			this.showTimeoutWarning = false;
			
			// Reset timeout
			if (this.timeoutWarning) {
				clearTimeout(this.timeoutWarning);
			}
			this.timeoutWarning = setTimeout(() => {
				const status = this.$resources?.siteRequest?.doc?.status;
				if (status && !['Error', 'Site Created'].includes(status)) {
					this.showTimeoutWarning = true;
				}
			}, 120000);
		},
		handleJobUpdate(data) {
			// Follow JobPage.vue pattern exactly
			if (data.id === this.currentJobId) {
				console.log('Job update received via socket:', data);
				
				// Transform steps data like JobPage.vue
				data.steps = data.steps.map((step) => {
					step.title = step.step_name;
					step.duration = this.$format?.duration?.(step.duration) || step.duration;
					return step;
				});

				// Update resource doc directly like JobPage.vue
				if (this.$resources.siteCreationJob.doc) {
					this.$resources.siteCreationJob.doc = {
						...this.$resources.siteCreationJob.doc,
						...data,
					};
				}
				
				// Calculate progress based on completed steps
				const completedSteps = data.steps?.filter(step => step.status === 'Success').length || 0;
				const totalSteps = data.steps?.length || 1;
				const percentage = Math.min(Math.round((completedSteps / totalSteps) * 100), 95);
				
				// Find current running step
				const runningStep = data.steps?.find(step => step.status === 'Running');
				const pendingStep = data.steps?.find(step => step.status === 'Pending');
				const currentStepName = runningStep?.step_name || 
					pendingStep?.step_name || 
					(data.status === 'Success' ? 'Completed' : 'Processing...');
				
				// Update job progress
				this.jobProgress = {
					percentage: data.status === 'Success' ? 100 : percentage,
					currentStep: this.translateStepName(currentStepName),
					completedSteps,
					totalSteps,
					status: data.status,
					steps: data.steps || []
				};
			}
		},
		translateStepName(stepName) {
			// Translate technical step names to user-friendly messages
			const stepTranslations = {
				'New Site': 'Creating site structure',
				'Setup Environment': 'Setting up environment',
				'Install Apps': 'Installing applications',
				'Setup Database': 'Configuring database',
				'Setup NGINX': 'Setting up web server',
				'Reload NGINX': 'Finalizing web server',
				'Enable Scheduler': 'Enabling background tasks',
				'Update Site Configuration': 'Updating configuration',
				'Bench Setup NGINX': 'Setting up web server',
				'Prefilling Setup Wizard': 'Preparing setup wizard',
				'Wait for Site': 'Preparing site creation',
				'Completed': 'Setup completed',
				'Initializing...': 'Getting ready...'
			};
			
			return stepTranslations[stepName] || stepName || 'Processing...';
		},
		startJobTracking() {
			if (this.currentJobId) {
				console.log('Starting job tracking for:', this.currentJobId);
				// Subscribe to job updates
				this.$socket.emit('doc_subscribe', 'Agent Job', this.currentJobId);
				// Load initial job data
				this.$resources.siteCreationJob.reload();
			}
		},
		startRealProgressTracking() {
			console.log('Starting real progress tracking...');
			
			// Only use real progress from getProgress API
			if (this.$resources?.siteRequest?.getProgress) {
				// Initial load
				this.$resources.siteRequest.getProgress.reload();
				
				// Poll every 3 seconds for real progress
				this.progressInterval = setInterval(() => {
					if (!this.$resources.siteRequest.getProgress.loading && 
						!['Error', 'Site Created'].includes(this.siteRequestStatus)) {
						console.log('Polling real progress...');
						this.$resources.siteRequest.getProgress.reload();
					}
				}, 3000);
			}
		},
		reloadProgress() {
			// Follow JobPage.vue reload pattern
			if (
				!this.$resources.siteRequest?.loading &&
				!this.$resources.siteRequest?.getProgress?.loading &&
				// reload if last loaded more than 5 seconds ago
				Date.now() - (this.lastLoaded || 0) > 5000
			) {
				console.log('Fallback reload progress and site request...');
				this.$resources.siteRequest.reload();
				this.$resources.siteRequest.getProgress?.reload();
				this.lastLoaded = Date.now();
			}
		}
	},
	watch: {
		// Watch for job ID changes to start tracking
		currentJobId: {
			handler(newJobId, oldJobId) {
				if (oldJobId && oldJobId !== newJobId) {
					// Unsubscribe from old job
					this.$socket.emit('doc_unsubscribe', 'Agent Job', oldJobId);
				}
				if (newJobId) {
					this.startJobTracking();
				}
			},
			immediate: true
		},
		// Watch for site request status changes with safe access
		siteRequestStatus: {
			handler(newStatus) {
				if (newStatus === 'Site Created') {
					this.jobProgress.percentage = 100;
					this.jobProgress.currentStep = 'Site ready!';
					this.showTimeoutWarning = false;
				}
			}
		}
	},
};
</script>
