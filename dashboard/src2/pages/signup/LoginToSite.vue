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

					<!-- Status Message with Real Progress from Job Steps -->
					<div class="text-center space-y-3">
						<h3 class="text-lg font-medium text-gray-900">
							{{ currentDisplayStep || __('Completing setup') }}
						</h3>
						<p class="text-sm text-gray-600">
							{{ __('We are preparing your site. This usually takes a few moments...') }}
						</p>
						
						<!-- Real Progress Bar from Job Steps -->
						<div class="space-y-3 mt-6">
							<div class="flex justify-between text-sm">
								<span class="text-gray-600">{{ currentDisplayStep }}</span>
								<span class="text-gray-500 font-semibold">{{ displayPercentage }}%</span>
							</div>
							<div class="w-full bg-gray-200 rounded-full h-3">
								<div 
									class="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500 ease-out shadow-sm"
									:style="{ width: displayPercentage + '%' }"
								></div>
							</div>
							<div class="text-xs text-gray-500">
								{{ progressSummary }}
							</div>
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
			subdomain: this.$route.query.subdomain || null,
			lastLoaded: 0,
			// Enhanced job progress tracking like JobPage.vue
			jobProgress: {
				percentage: 0,
				currentStep: 'Initializing...',
				completedSteps: 0,
				totalSteps: 0,
				steps: []
			},
			// Add debug flags
			debugMode: process.env.NODE_ENV === 'development',
			// Job tracking state
			isJobTrackingActive: false,
			jobCheckInterval: null,
		};
	},
	mounted() {
		this.log('=== LoginToSite Debug Info ===');
		this.log('Route query:', this.$route.query);
		this.log('product_trial_request:', this.product_trial_request);
		this.log('productId:', this.productId);
		this.log('subdomain:', this.subdomain);
		
		// Start immediate status check
		this.startStatusMonitoring();
		
		// Set timeout warning after 3 minutes (increased from 2)
		this.timeoutWarning = setTimeout(() => {
			const status = this.$resources?.siteRequest?.doc?.status;
			this.log('Timeout check - current status:', status);
			if (!status || !['Error', 'Site Created'].includes(status)) {
				this.log('Showing timeout warning');
				this.showTimeoutWarning = true;
			}
		}, 180000); // 3 minutes

		// Subscribe to socket updates early
		this.setupSocketListeners();
		
		// Start aggressive polling for status updates
		this.startPolling();
		
		this.$nextTick(() => {
			this.log('Resources after mount:', this.$resources);
			this.checkInitialStatus();
		});
	},
	beforeUnmount() {
		this.log('Cleanup on unmount');
		this.cleanup();
	},
	resources: {
		saasProduct() {
			return {
				type: 'document',
				doctype: 'Product Trial',
				name: this.productId,
				auto: true,
				onSuccess: (doc) => {
					this.log('saasProduct loaded:', doc);
				},
				onError: (error) => {
					this.log('saasProduct error:', error);
				}
			};
		},
		siteRequest() {
			this.log('Setting up siteRequest resource with name:', this.product_trial_request);
			return {
				type: 'document',
				doctype: 'Product Trial Request',
				name: this.product_trial_request,
				realtime: true,
				auto: this.product_trial_request ? true : false,
				onSuccess: (doc) => {
					this.log('siteRequest loaded successfully:', doc);
					this.lastLoaded = Date.now();
					this.handleStatusChange(doc.status);
				},
				onError: (error) => {
					this.log('siteRequest error:', error);
					// Don't give up on error, keep trying
					setTimeout(() => {
						this.log('Retrying siteRequest after error...');
						this.$resources.siteRequest.reload();
					}, 5000);
				},
				whitelistedMethods: {
					getProgress: {
						method: 'get_progress',
						makeParams() {
							return {
								current_progress: this.progressCount || 0,
							};
						},
						onSuccess: (data) => {
							this.log('Progress data received:', data);
							this.handleProgressUpdate(data);
						},
						onError: (error) => {
							this.log('Progress check error:', error);
							// Continue checking even on error
							this.scheduleNextProgressCheck();
						},
					},
					getLoginSid: {
						method: 'get_login_sid',
						onSuccess: (loginURL) => {
							this.log('Login URL received:', loginURL);
							window.open(loginURL, '_self');
						},
						onError: (error) => {
							this.log('Login error:', error);
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
					this.log('Adding domain with params:', siteName, `${this.subdomain}.nhansu360.com`);
					return {
						name: siteName,
						domain: `${this.subdomain}.nhansu360.com`,
					};
				},
				auto: false,
				onSuccess: () => {
					this.log('Domain added successfully, proceeding to login');
					this.$resources.siteRequest.getLoginSid.submit();
				},
				onError: (error) => {
					this.log('Error adding domain:', error);
					// Still proceed to login even if domain addition fails
					this.$resources.siteRequest.getLoginSid.submit();
				},
			};
		},
		// Simplified job tracking like JobPage.vue
		siteCreationJob() {
			return {
				type: 'document',
				doctype: 'Agent Job',
				name: () => this.currentJobId,
				auto: false, // Don't auto load until we have valid job ID
				realtime: true,
				transform: (job) => {
					if (!job) return null;
					
					// Transform steps like JobPage.vue
					if (job.steps) {
						for (let step of job.steps) {
							step.title = step.step_name;
							step.duration = this.$format?.duration?.(step.duration) || step.duration;
							step.isOpen = this.jobProgress.steps.find(s => s.name === step.name)?.isOpen || false;
						}
					}

					// Handle delivery failure like JobPage.vue
					if (job.status === 'Delivery Failure' && job.steps && job.steps[0]) {
						job.steps[0].output = job.output;
					}

					return job;
				},
				onSuccess: (job) => {
					this.log('Job data loaded:', job);
					if (job) {
						this.updateJobProgress(job);
					}
				},
				onError: (error) => {
					this.log('Job loading error:', error);
				}
			};
		},
	},
	computed: {
		saasProduct() {
			return this.$resources?.saasProduct?.doc;
		},
		currentJobId() {
			const doc = this.$resources?.siteRequest?.doc;
			const jobId = doc?.job || null;
			this.log('Current Job ID computed:', jobId, 'from doc:', doc);
			return jobId;
		},
		hasValidJobId() {
			return this.currentJobId && this.currentJobId.trim() !== '';
		},
		// Current job data like JobPage.vue
		currentJob() {
			return this.$resources?.siteCreationJob?.doc || null;
		},
		// Check if we have job steps to display like JobPage.vue
		hasJobSteps() {
			return this.currentJob && this.currentJob.steps && this.currentJob.steps.length > 0;
		},
		// Display properties for the template
		currentDisplayStep() {
			if (this.hasJobSteps) {
				return this.jobProgress.currentStep;
			}
			return this.currentBuildStep;
		},
		displayPercentage() {
			if (this.hasJobSteps) {
				return Math.round(this.jobProgress.percentage);
			}
			return Math.round(this.progressCount);
		},
		progressSummary() {
			if (this.hasJobSteps) {
				return `${this.jobProgress.completedSteps} / ${this.jobProgress.totalSteps} steps completed`;
			}
			return 'Setting up your site...';
		},
		showProgressBar() {
			const status = this.$resources?.siteRequest?.doc?.status;
			const shouldShow = status && !['Error', 'Site Created'].includes(status);
			this.log('Show Progress Bar:', shouldShow, 'Status:', status);
			return shouldShow || this.product_trial_request; // Show if we have a request regardless
		},
		siteRequestStatus() {
			return this.$resources?.siteRequest?.doc?.status || null;
		},
		shouldShowMainLoading() {
			const hasRequest = !!this.product_trial_request;
			const status = this.siteRequestStatus;
			const isInProgress = hasRequest && (!status || !['Error', 'Site Created'].includes(status));
			
			this.log('Should Show Main Loading:', isInProgress, 'Status:', status);
			return isInProgress;
		},
	},
	methods: {
		log(...args) {
			// Always log on production for debugging - you can disable this later
			console.log('[LoginToSite]', ...args);
		},
		
		startStatusMonitoring() {
			this.log('Starting status monitoring...');
			// Immediate check
			this.$nextTick(() => {
				if (this.$resources.siteRequest && this.product_trial_request) {
					this.$resources.siteRequest.reload();
				}
			});
		},
		
		setupSocketListeners() {
			this.log('Setting up socket listeners...');
			// Follow JobPage.vue pattern exactly
			this.$socket.on('agent_job_update', this.handleJobUpdate);
		},
		
		startPolling() {
			this.log('Starting polling...');
			// More aggressive polling for production
			this.pollingInterval = setInterval(() => {
				this.pollForUpdates();
			}, 10000); // Every 10 seconds
			
			// Fallback reload like JobPage.vue
			this.reloadInterval = setInterval(() => {
				this.reloadIfNeeded();
			}, 30000); // Every 30 seconds
		},
		
		pollForUpdates() {
			const status = this.siteRequestStatus;
			this.log('Polling update - current status:', status);
			
			if (!status || !['Error', 'Site Created'].includes(status)) {
				// Reload site request
				if (!this.$resources.siteRequest?.loading) {
					this.$resources.siteRequest.reload();
				}
				
				// Check progress
				if (this.$resources.siteRequest?.getProgress && !this.$resources.siteRequest.getProgress.loading) {
					this.$resources.siteRequest.getProgress.reload();
				}
			}
		},
		
		reloadIfNeeded() {
			// Follow JobPage.vue reload pattern
			if (
				!this.$resources.siteRequest?.loading &&
				Date.now() - this.lastLoaded > 5000
			) {
				this.log('Fallback reload...');
				this.$resources.siteRequest.reload();
				this.lastLoaded = Date.now();
			}
		},
		
		checkInitialStatus() {
			this.log('Checking initial status...');
			const doc = this.$resources?.siteRequest?.doc;
			if (doc) {
				this.log('Initial doc found:', doc);
				this.handleStatusChange(doc.status);
			} else if (this.product_trial_request) {
				this.log('No doc yet, forcing reload...');
				this.$resources.siteRequest.reload();
			}
		},
		
		handleStatusChange(status) {
			this.log('Status changed to:', status);
			
			switch (status) {
				case 'Site Created':
					this.log('Site created successfully!');
					this.showTimeoutWarning = false;
					this.jobProgress.percentage = 100;
					this.jobProgress.currentStep = 'Site ready!';
					this.loginToSite();
					break;
					
				case 'Error':
					this.log('Site creation failed');
					this.showTimeoutWarning = false;
					break;
					
				case 'Wait for Site':
				case 'New Site':
				case 'Prefilling Setup Wizard':
					this.log('Site creation in progress, starting progress tracking...');
					this.showTimeoutWarning = false;
					this.startProgressTracking();
					break;
					
				default:
					if (status) {
						this.log('Unknown status, continuing monitoring:', status);
						this.startProgressTracking();
					}
					break;
			}
		},
		
		startProgressTracking() {
			this.log('Starting progress tracking...');
			
			// Start job ID checking first
			this.startJobIdChecking();
			
			// Start progress API polling
			if (this.$resources.siteRequest?.getProgress) {
				this.$resources.siteRequest.getProgress.reload();
			}
		},
		
		startJobIdChecking() {
			this.log('Starting job ID checking...');
			
			// Check immediately if we have job ID
			if (this.hasValidJobId) {
				this.log('Job ID available immediately, starting tracking');
				this.startJobTracking();
			} else {
				this.log('No job ID yet, setting up periodic check');
				// Check for job ID every 5 seconds
				this.jobCheckInterval = setInterval(() => {
					this.checkForJobId();
				}, 5000);
			}
		},
		
		checkForJobId() {
			this.log('Checking for job ID...');
			
			if (this.hasValidJobId && !this.isJobTrackingActive) {
				this.log('Job ID found, starting tracking:', this.currentJobId);
				this.startJobTracking();
				
				// Clear the checking interval
				if (this.jobCheckInterval) {
					clearInterval(this.jobCheckInterval);
					this.jobCheckInterval = null;
				}
			} else if (!this.hasValidJobId) {
				this.log('Still no job ID, will check again...');
				// Force reload site request to get latest data
				if (!this.$resources.siteRequest?.loading) {
					this.$resources.siteRequest.reload();
				}
			}
		},
		
		startJobTracking() {
			// Safety check - only proceed if we have valid job ID
			if (!this.hasValidJobId) {
				this.log('Cannot start job tracking - no valid job ID');
				return;
			}
			
			if (this.isJobTrackingActive) {
				this.log('Job tracking already active');
				return;
			}
			
			this.log('Starting job tracking for valid ID:', this.currentJobId);
			this.isJobTrackingActive = true;
			
			// Subscribe to job updates like JobPage.vue - ONLY with valid ID
			this.$socket.emit('doc_subscribe', 'Agent Job', this.currentJobId);
			
			// Load initial job data - ONLY with valid ID
			if (this.$resources.siteCreationJob) {
				this.$resources.siteCreationJob.reload();
			}
		},
		
		stopJobTracking() {
			if (!this.isJobTrackingActive) {
				return;
			}
			
			this.log('Stopping job tracking');
			this.isJobTrackingActive = false;
			
			// Unsubscribe from current job if we have valid ID
			if (this.hasValidJobId) {
				this.$socket.emit('doc_unsubscribe', 'Agent Job', this.currentJobId);
			}
		},
		
		handleJobUpdate(data) {
			// Follow JobPage.vue pattern exactly - with safety check
			if (!this.hasValidJobId || data.id !== this.currentJobId) {
				return;
			}
			
			this.log('Job update received via socket:', data);
			
			// Transform steps data like JobPage.vue
			if (data.steps) {
				data.steps = data.steps.map((step) => {
					step.title = step.step_name;
					step.duration = this.$format?.duration?.(step.duration) || step.duration;
					step.isOpen = this.jobProgress.steps.find(s => s.name === step.name)?.isOpen || false;
					return step;
				});
			}

			// Update resource doc directly like JobPage.vue
			if (this.$resources.siteCreationJob?.doc) {
				this.$resources.siteCreationJob.doc = {
					...this.$resources.siteCreationJob.doc,
					...data,
				};
			}
			
			this.updateJobProgress(data);
		},
		
		updateJobProgress(job) {
			if (!job || !job.steps) return;
			
			// Calculate progress like JobPage.vue
			const completedSteps = job.steps.filter(step => step.status === 'Success').length;
			const totalSteps = job.steps.length;
			const percentage = totalSteps > 0 ? Math.min(Math.round((completedSteps / totalSteps) * 100), 95) : 0;
			
			// Find current step
			const runningStep = job.steps.find(step => step.status === 'Running');
			const pendingStep = job.steps.find(step => step.status === 'Pending');
			const currentStepName = runningStep?.step_name || 
				pendingStep?.step_name || 
				(job.status === 'Success' ? 'Completed' : 'Processing...');
			
			// Update job progress
			this.jobProgress = {
				percentage: job.status === 'Success' ? 100 : percentage,
				currentStep: this.translateStepName(currentStepName),
				completedSteps,
				totalSteps,
				status: job.status,
				steps: job.steps || []
			};
			
			this.log('Job progress updated:', this.jobProgress);
		},
		
		translateStepName(stepName) {
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
		
		loginToSite() {
			this.log('LoginToSite called with subdomain:', this.subdomain);
			
			if (!this.$resources?.siteRequest) {
				this.log('Resources not available yet');
				return;
			}
			
			if (this.subdomain && this.$resources.siteRequest.doc?.site) {
				this.log('Adding domain before login');
				if (this.$resources.addDomain) {
					this.$resources.addDomain.submit();
				}
			} else {
				this.log('Proceeding directly to login');
				if (this.$resources.siteRequest.getLoginSid) {
					this.$resources.siteRequest.getLoginSid.submit();
				}
			}
		},
		
		checkStatus() {
			this.log('Manual status check triggered');
			
			if (!this.$resources?.siteRequest) {
				this.log('Resources not available for status check');
				return;
			}
			
			// Force reload
			this.$resources.siteRequest.reload();
			this.showTimeoutWarning = false;
			
			// Reset timeout
			if (this.timeoutWarning) {
				clearTimeout(this.timeoutWarning);
			}
			this.timeoutWarning = setTimeout(() => {
				const status = this.siteRequestStatus;
				if (!status || !['Error', 'Site Created'].includes(status)) {
					this.showTimeoutWarning = true;
				}
			}, 180000); // 3 minutes
		},
		
		cleanup() {
			this.log('Starting cleanup...');
			
			// Clear all timers
			if (this.timeoutWarning) {
				clearTimeout(this.timeoutWarning);
				this.timeoutWarning = null;
			}
			if (this.pollingInterval) {
				clearInterval(this.pollingInterval);
				this.pollingInterval = null;
			}
			if (this.reloadInterval) {
				clearInterval(this.reloadInterval);
				this.reloadInterval = null;
			}
			if (this.jobCheckInterval) {
				clearInterval(this.jobCheckInterval);
				this.jobCheckInterval = null;
			}
			
			// Stop job tracking safely
			this.stopJobTracking();
			
			// Cleanup socket listeners like JobPage.vue
			this.$socket.off('agent_job_update', this.handleJobUpdate);
			
			this.log('Cleanup completed');
		},
	},
	watch: {
		// Watch for job ID changes - with safety check
		currentJobId: {
			handler(newJobId, oldJobId) {
				this.log('Job ID changed from', oldJobId, 'to', newJobId);
				
				// Stop tracking old job if it was active
				if (oldJobId && oldJobId !== newJobId && this.isJobTrackingActive) {
					this.log('Unsubscribing from old job:', oldJobId);
					this.$socket.emit('doc_unsubscribe', 'Agent Job', oldJobId);
					this.isJobTrackingActive = false;
				}
				
				// Start tracking new job if we have valid ID
				if (newJobId && newJobId !== oldJobId && newJobId.trim() !== '') {
					this.log('New valid job ID detected, starting tracking');
					this.startJobTracking();
				}
			},
			// Remove immediate: true to avoid calling with undefined
		},
		
		// Watch for status changes
		siteRequestStatus: {
			handler(newStatus, oldStatus) {
				if (newStatus !== oldStatus) {
					this.log('Site status changed from', oldStatus, 'to', newStatus);
					this.handleStatusChange(newStatus);
				}
			}
		}
	},
};
</script>
