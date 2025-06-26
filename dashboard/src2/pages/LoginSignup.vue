<template>
	<div class="grid min-h-screen grid-cols-1 md:grid-cols-2">
		<!-- Left Column: Background and Logo -->
		<div class="col-span-1 hidden h-screen bg-gray-50 md:flex">
			<div v-if="saasProduct" class="relative h-screen w-full overflow-hidden">
				<!-- Background Image - removed blur effect -->
				<img
					:src="saasProduct?.background"
					alt="Background"
					class="h-full w-full object-cover"
				/>

				<!-- Product Logo Overlay -->

			</div>

			<div v-else class="relative h-screen w-full overflow-hidden">
				<!-- Background Image - removed blur effect -->
				<img
					src="/public/bg1.png"
					alt="Background"
					class="h-full w-full object-cover"
				/>
			</div>
		</div>

		<!-- Right Column: Auth Forms - set to full width and height -->
		<div class="relative col-span-1 flex h-full w-full items-center justify-center py-8 md:overflow-auto md:bg-white">
			<LoginBox
				:title="title"
				class="w-full h-full md:h-auto md:max-w-md transition-all duration-300 shadow-xl rounded-xl"
				:class="{ 
					'pointer-events-none': $resources.signup.loading || $resources.checkEmailExists.loading
				}"
			>
				<template v-slot:default>
					<!-- Unified Email Form - Initial Step -->
					<div v-if="showEmailForm && !is2FA && !hasForgotPassword && !resetPasswordEmailSent" 
						class="transition-all duration-300 w-full">
						<form class="flex flex-col space-y-4 w-full" @submit.prevent="handleEmailSubmit">
							<FormControl
								label="Email"
								type="email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								v-model="email"
								variant="outline"
								required
								class="focus-within:shadow-sm transition-all duration-300 w-full"
							/>
							<Button
								class="mt-4 transform transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 w-full"
								:loading="$resources.checkEmailExists.loading"
								variant="solid"
								type="submit"
							>
								{{__('Send verification code')}}
							</Button>
						</form>
					</div>

					<!-- Login Form - When user exists -->
					<div v-else-if="showLoginForm && !is2FA && !hasForgotPassword && !resetPasswordEmailSent"
						class="transition-all duration-300 w-full">
						<form class="flex flex-col space-y-4 w-full">
							<FormControl
								label="Email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								v-model="email"
								:disabled="true"
								variant="outline"
								required
								class="w-full"
							/>

							<!-- OTP Verification Input (when OTP is sent) -->
							<template v-if="otpSent">
								<FormControl
									:label="__('Verification code')"
									placeholder="123456"
									variant="outline"
									ref="otpInput"
									v-model="otp"
									required
									class="focus-within:shadow-sm transition-all duration-300 w-full"
								/>
								<div class="space-y-3 w-full">
									<Button
										class="w-full transform transition-all duration-300 hover:shadow-md hover:-translate-y-0.5"
										:loading="$resources.verifyOTPAndLogin.loading"
										variant="solid"
										@click="verifyOTPAndLogin"
									>
										{{__('Submit verification code')}}
									</Button>
									<Button
										class="w-full transition-all duration-300"
										:loading="$resources.sendOTP.loading"
										variant="outline"
										:disabled="otpResendCountdown > 0"
										@click="$resources.sendOTP.submit()"
									>
										<span class="flex items-center justify-center">
											<span>{{__('Resend verification code')}}</span>
											<span v-if="otpResendCountdown > 0" class="text-xs font-medium bg-gray-100 py-1 px-2 rounded-full">
												{{ otpResendCountdown }}s
											</span>
										</span>
									</Button>
								</div>
							</template>

							<!-- Loading state while sending OTP -->
							<template v-else>
								<div class="mt-4 w-full">
									<Button
										class="w-full"
										:loading="$resources.sendOTP.loading"
										variant="solid"
										disabled
									>
										<span class="flex items-center justify-center gap-2">
											<span>Sending verification code...</span>
										</span>
									</Button>
								</div>
							</template>
						</form>

						<div class="mt-6 flex justify-start w-full">
							<Button
								variant="ghost"
								@click="resetToEmailForm"
								class="text-sm transform transition-all duration-300 hover:-translate-x-0.5"
							>
								← {{__('Use different email')}}
							</Button>
						</div>

						<!-- Error Messages -->
						<ErrorMessage
							class="mt-4 w-full"
							:message="
								$resources.sendOTP.error ||
								$resources.verifyOTPAndLogin.error
							"
						/>
					</div>

					<!-- Signup Form - When user doesn't exist -->
					<div v-else-if="showSignupForm && !otpRequested && !resetPasswordEmailSent" 
						class="transition-all duration-300 w-full">
						<form class="flex flex-col space-y-4">
							<FormControl
								label="Email"
								type="email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								variant="outline"
								v-model="email"
								:disabled="true"
								required
								class="w-full"
							/>
							<div class="mt-4">
								<Button
									class="w-full"
									:loading="$resources.signup.loading"
									variant="solid"
									disabled
								>
									<span class="flex items-center justify-center gap-2">
										<span>Creating account and sending verification code...</span>
									</span>
								</Button>
							</div>
						</form>

						<div class="mt-6 flex justify-start">
							<Button
								variant="ghost"
								@click="resetToEmailForm"
								class="text-sm transform transition-all duration-300 hover:-translate-x-0.5"
							>
								← {{__('Use different email')}}
							</Button>
						</div>

						<ErrorMessage class="mt-4" :message="$resources.signup.error" />
					</div>

					<!-- 2FA Section -->
					<div v-else-if="is2FA" class="transition-all duration-300 w-full">
						<form class="flex flex-col space-y-4" @submit.prevent="submitForm">
							<FormControl
								label="2FA Code from your Authenticator App"
								placeholder="123456"
								v-model="twoFactorCode"
								required
								variant="outline"
								class="focus-within:shadow-sm transition-all duration-300"
							/>
							<Button
								class="transform transition-all duration-300 hover:shadow-md hover:-translate-y-0.5"
								:loading="
									$resources.verify2FA.loading ||
									$session.login.loading ||
									$resources.resetPassword.loading
								"
								variant="solid"
								@click="
									$resources.verify2FA.submit({
										user: email,
										totp_code: twoFactorCode,
									})
								"
							>
								{{__('Verify')}}
							</Button>
							<ErrorMessage
								class="mt-4"
								:message="$resources.verify2FA.error"
							/>
						</form>
					</div>

					<!-- Forgot Password Section -->
					<div v-else-if="hasForgotPassword" class="transition-all duration-300 w-full">
						<form class="flex flex-col space-y-4" @submit.prevent="submitForm">
							<FormControl
								label="Email"
								type="email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								v-model="email"
								variant="outline"
								required
								class="focus-within:shadow-sm transition-all duration-300"
							/>
							<router-link
								class="mt-2 text-sm text-blue-600 hover:text-blue-800 transition-colors duration-300"
								:to="{
									name: 'Login',
									query: { ...$route.query, forgot: undefined },
								}"
							>
								I remember my password
							</router-link>
							<Button
								class="transform transition-all duration-300 hover:shadow-md hover:-translate-y-0.5"
								:loading="$resources.resetPassword.loading"
								variant="solid"
							>
								Reset Password
							</Button>
						</form>
					</div>

					<!-- OTP Verification for Signup -->
					<div v-else-if="otpRequested" class="transition-all duration-300 w-full">
						<form class="flex flex-col space-y-4">
							<FormControl
								label="Email"
								type="email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								v-model="email"
								variant="outline"
								:disabled="true"
								required
								class="w-full"
							/>
							<FormControl
								:label="__('Verification code')"
								type="text"
								placeholder="123456"
								maxlength="6"
								v-model="otp"
								required
								variant="outline"
								class="focus-within:shadow-sm transition-all duration-300 w-full"
							/>
							<ErrorMessage
								class="mt-2"
								:message="$resources.verifyOTP.error"
							/>
							<div class="space-y-3">
								<Button
									class="w-full transform transition-all duration-300 hover:shadow-md hover:-translate-y-0.5"
									variant="solid"
									:loading="$resources.verifyOTP.loading"
									@click="$resources.verifyOTP.submit()"
								>
									{{__('Verify')}}
								</Button>
								<Button
									class="w-full transition-all duration-300"
									variant="outline"
									:loading="$resources.resendOTP.loading"
									@click="$resources.resendOTP.submit()"
									:disabled="otpResendCountdown > 0"
								>
									<span class="flex items-center justify-center gap-2">
										<span>{{__('Resend verification code')}}</span>
										<span v-if="otpResendCountdown > 0" class="text-xs font-medium bg-gray-100 py-1 px-2 rounded-full">
											{{ otpResendCountdown }}s
										</span>
									</span>
								</Button>
							</div>
						</form>
					</div>

					<!-- Reset Password Success -->
					<div
						class="p-4 bg-green-50 border border-green-100 rounded-lg text-green-800 w-full"
						v-else-if="resetPasswordEmailSent"
					>
						<p class="flex items-center gap-2">
							<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							We have sent an email to
							<span class="font-semibold">{{ email }}</span>
							. Please click on the link received to reset your password.
						</p>
					</div>
				</template>
				
				<!-- Product Logo -->
				<template v-slot:logo v-if="saasProduct">
					<div class="flex mb-4 w-full justify-center">
						<img
							class="h-16 w-auto rounded-md shadow-md transition-all duration-300 hover:shadow-lg"
							:src="saasProduct?.logo"
							alt="Product Logo"
						/>
					</div>
				</template>
				
				<!-- Language Selector - made full width -->
				<template v-slot:footer>
					<div class="flex items-center justify-center border-t border-gray-100 mt-6 w-full">
						<SelectLanguage class="w-full opacity-80 hover:opacity-100 transition-opacity duration-300" />
					</div>
				</template>
			</LoginBox>
		</div>
	</div>
</template>

<script>
import LoginBox from '../components/auth/LoginBox.vue';
import GoogleIconSolid from '@/components/icons/GoogleIconSolid.vue';
import GoogleIcon from '@/components/icons/GoogleIcon.vue';
import { toast } from 'vue-sonner';
import { getToastErrorMessage } from '../utils/toast';
import SelectLanguage from '../components/SelectLanguage.vue';

export default {
	name: 'Signup',
	components: {
		LoginBox,
		GoogleIcon,
		SelectLanguage
	},
	data() {
		return {
			email: '',
			account_request: '',
			otpRequested: false,
			otp: '',
			otpSent: false,
			twoFactorCode: '',
			password: null,
			otpResendCountdown: 0,
			resetPasswordEmailSent: false,
			// New states for unified flow
			showEmailForm: true,
			showLoginForm: false,
			showSignupForm: false,
			emailChecked: false,
			userExists: false,
			isCheckUser: false,
			listApp: [],
			isCheckSite: '',
		};
	},
	mounted() {
		this.email = localStorage.getItem('login_email');
		setInterval(() => {
			if (this.otpResendCountdown > 0) {
				this.otpResendCountdown -= 1;
			}
		}, 1000);
	},
	watch: {
		email() {
			this.resetSignupState();
		},
	},
	resources: {
		signup() {
			return {
				url: 'press.api.account.signup',
				params: {
					email: this.email,
					referrer: this.getReferrerIfAny(),
					product: this.$route.query.product,
				},
				onSuccess(account_request) {
					this.account_request = account_request;
					this.otpRequested = true;
					this.otpResendCountdown = 30;
					toast.success(__('Verification code sent to your email'));
				},
				onError: (error) => {
					if (error?.exc_type !== 'ValidationError') {
						return;
					}
					let errorMessage = '';
					if ((error?.messages ?? []).length) {
						errorMessage = error?.messages?.[0];
					}
					// check if error message has `is already registered` substring
					if (errorMessage.includes('is already registered')) {
						localStorage.setItem('login_email', this.email);

						if (this.$route.query?.product) {
							console.log('Redirecting to create site setup',this.$route.query?.product);
							this.$router.push({
								name: 'Login',
								query: {
									redirect: `dashboard/signup?product=${this.$route.query.product}`,
									// redirect: `/dashboard/create-site/${this.$route.query.product}/setup`,
								},
							});
						} else {
							this.$router.push({
								name: 'Login',
							});
						}
					}
				},
			};
		},
		verifyOTP() {
			return {
				url: 'press.api.account.verify_otp',
				params: {
					account_request: this.account_request,
					otp: this.otp,
				},
				onSuccess(key) {
					window.open(`/dashboard/setup-account/${key}`, '_self');
				},
			};
		},
		resendOTP() {
			return {
				url: 'press.api.account.resend_otp',
			 params: {
					account_request: this.account_request,
				},
				onSuccess() {
					this.otp = '';
					this.otpResendCountdown = 30;
					toast.success(__('Verification code sent to your email'));
				},
				onError(err) {
					toast.error(
						getToastErrorMessage(err, 'Failed to resend verification code'),
					);
				},
			};
		},
		sendOTP() {
			return {
				url: 'press.api.account.send_otp',
				params: {
					email: this.email,
				},
				onSuccess() {
					this.otpSent = true;
					this.otpResendCountdown = 30;
					toast.success(__('Verification code sent to your email'));
				},
				onError(err) {
					toast.error(
						getToastErrorMessage(err, 'Failed to send verification code'),
					);
				},
			};
		},
		verifyOTPAndLogin() {
			return {
				url: 'press.api.account.verify_otp_and_login',
				params: {
					email: this.email,
					otp: this.otp,
				},
				onSuccess(res) {
					console.log('Login successful:', res);
					this.afterLogin(res);
				},
				onError(err) {
					console.error('Login failed:', err);
					toast.error(
						getToastErrorMessage(err, 'Failed to verify OTP and login'),
					);
				},
			};
		},
		oauthLogin() {
			return {
				url: 'press.api.oauth.oauth_authorize_url',
				onSuccess(url) {
					localStorage.setItem('login_email', this.email);
					window.location.href = url;
				},
			};
		},
		googleLogin() {
			return {
				url: 'press.api.google.login',
				makeParams() {
					return {
						product: this.$route.query.product,
					};
				},
				onSuccess(url) {
					window.location.href = url;
				},
			};
		},
		resetPassword() {
			return {
				url: 'press.api.account.send_reset_password_email',
				onSuccess() {
					this.resetPasswordEmailSent = true;
				},
			};
		},
		signupSettings() {
			return {
				url: 'press.api.account.signup_settings',
				params: {
					product: this.$route.query.product,
				},
				auto: true,
			};
		},
		is2FAEnabled() {
			return {
				url: 'press.api.account.is_2fa_enabled',
			};
		},
		verify2FA() {
			return {
				url: 'press.api.account.verify_2fa',
				onSuccess: async () => {
					if (this.isLogin) {
						if (!this.usePassword) {
							await this.$resources.verifyOTPAndLogin.submit();
						} else {
							await this.login();
						}
					} else if (this.hasForgotPassword) {
						await this.$resources.resetPassword.submit({
							email: this.email,
						});
					}
				},
			};
		},
		checkEmailExists() {
			return {
				url: 'press.api.account.check_email_exists',
				params: {
					email: this.email,
				},
				onSuccess(data) {
					this.emailChecked = true;
					this.userExists = data.user_exists;
					
					if (data.user_exists) {
						// User exists, show login form
						this.showEmailForm = false;
						this.showLoginForm = true;
						this.showSignupForm = false;
						// Automatically send OTP for login
						this.$resources.sendOTP.submit();
					} else {
						// User doesn't exist, show signup form
						this.showEmailForm = false;
						this.showLoginForm = false;
						this.showSignupForm = true;
						// Automatically create account request and send OTP
						this.$resources.signup.submit();
					}
				},
				onError(err) {
					toast.error(
						getToastErrorMessage(err, 'Failed to check email'),
					);
				},
			};
		},
		isCheckUserCheck() {
			return {
				url: 'press.api.site.is_check_user',
				makeParams: () => {
					return {
						email:this.email
					};
				},
				onSuccess(data) {
					console.log('isCheckUser', data);
					this.isCheckUser = data.user;
					this.listApp = data.list_app;
					this.isCheckSite = data.site;
				},
				onError(err) {
					console.error('isCheckUser', err);
				},
			};
		},
	},
	methods: {
		resetSignupState() {
			if (!this.isLogin && !this.hasForgotPassword && this.otpRequested) {
				this.otpRequested = false;
				this.account_request = '';
				this.otp = '';
			}
		},
		async submitForm() {
			if (this.isLogin) {
				if (this.isOauthLogin) {
					this.$resources.oauthLogin.submit({
						provider: this.socialLoginKey,
					});
				} else if (!this.usePassword) {
					// OTP login is handled by separate buttons
					return;
				} else if (this.email && this.password) {
					await this.checkTwoFactorAndLogin();
				}
			} else if (this.hasForgotPassword) {
				await this.checkTwoFactorAndResetPassword();
			} else {
				this.$resources.signup.submit();
			}
		},

		async checkTwoFactorAndLogin() {
			await this.$resources.is2FAEnabled.submit(
				{ user: this.email },
				{
					onSuccess: async (two_factor_enabled) => {
						if (two_factor_enabled) {
							this.$router.push({
								name: 'Login',
								query: {
									...this.$route.query,
									two_factor: 1,
								},
							});
						} else {
							await this.login();
						}
					},
				},
			);
		},

		async checkTwoFactorAndResetPassword() {
			await this.$resources.is2FAEnabled.submit(
				{ user: this.email },
				{
					onSuccess: async (two_factor_enabled) => {
						if (two_factor_enabled) {
							this.$router.push({
								name: 'Login',
								query: {
									two_factor: 1,
									forgot: 1,
								},
							});
						} else {
							await this.$resources.resetPassword.submit({
								email: this.email,
							});
						}
					},
				},
			);
		},

		verifyOTPAndLogin() {
			// Gọi trực tiếp API verify_otp_and_login thay vì kiểm tra 2FA trước
			this.$resources.verifyOTPAndLogin.submit();
		},
		getReferrerIfAny() {
			const params = location.search;
			const searchParams = new URLSearchParams(params);
			return searchParams.get('referrer');
		},
		async login() {
			await this.$session.login.submit(
				{
					email: this.email,
					password: this.password,
				},
				{
					onSuccess: (res) => {
						console.log("log in success");
						
						this.afterLogin(res);
					},
					onError: (err) => {
						if (this.$route.name === 'Login' && this.$route.query.two_factor) {
							this.$router.push({
								name: 'Login',
								query: {
									two_factor: undefined,
								},
							});
							this.twoFactorCode = '';
						}
					},
				},
			);
		},
		afterLogin(res) {
			const productId = localStorage.getItem('product_id');
			console.log("res============ >>>>>>>>>>>>>>>>>>>>>>>>>>>>", this.email);
			localStorage.setItem('login_email', this.email);
			console.log("vào đây");
			// Gọi resource isCheckUser để lấy trạng thái user
			this.$resources.isCheckUserCheck.submit({}, {
				onSuccess: (data) => {
					console.log("data============", data)
					let path = '';
					// Nếu chưa có tài khoản (user == null/undefined/falsey)
					if (!data.user) {
						let loginRoute = `/dashboard${res.dashboard_route}`;
						if (this.$route.query.redirect) {
							loginRoute = this.$route.query.redirect;
						}
						window.location.href = loginRoute;
						return;
					}

					// Đã có tài khoản nhưng chưa có site
					if (!data.site) {
						path = `/dashboard/create-site/${productId}/plan`;
					} else {
						// Đã có site
						if (data.list_app && data.list_app.includes(productId)) {
							// Đã có app (productId)
							path = `/dashboard/create-site/${productId}/summary`;
						} else {
							// Chưa có app (productId)
							path = `/dashboard/create-site/${productId}/plan`;
						}
					}
					// this.$router.push(path);
					window.location.href = path
				},
				onError: (err) => {
					// Nếu lỗi, fallback về dashboard
					let loginRoute = `/dashboard${res.dashboard_route}`;
					if (this.$route.query.redirect) {
						loginRoute = this.$route.query.redirect;
					}
					window.location.href = loginRoute;
				}
			});
		},
		
		// New methods for unified flow
		handleEmailSubmit() {
			if (this.email) {
				localStorage.setItem('login_email', this.email);
				this.$resources.checkEmailExists.submit();
			}
		},
		
		resetToEmailForm() {
			this.showEmailForm = true;
			this.showLoginForm = false;
			this.showSignupForm = false;
			this.emailChecked = false;
			this.userExists = false;
			this.otpSent = false;
			this.otpRequested = false;
			this.otp = '';
			this.account_request = '';
		},
	},
	computed: {
		error() {
			if (this.$resources.signup.error) {
				return this.$resources.signup.error;
			}

			if (this.$resources.resetPassword.error) {
				return this.$resources.resetPassword.error;
			}
		},
		saasProduct() {
			return this.$resources.signupSettings.data?.product_trial;
		},
		isLogin() {
			return this.$route.name == 'Login' && !this.$route.query.forgot;
		},
		hasForgotPassword() {
			return this.$route.name == 'Login' && this.$route.query.forgot;
		},
		is2FA() {
			return this.$route.name == 'Login' && this.$route.query.two_factor;
		},
		emailDomain() {
			return this.email?.includes('@') ? this.email?.split('@').pop() : '';
		},
		isOauthLogin() {
			return (
				this.oauthEmailDomains.has(this.emailDomain) &&
				this.emailDomain.length > 0
			);
		},
		usePassword() {
			return Boolean(this.$route.query.use_password);
		},
		oauthProviders() {
			const domains = this.$resources.signupSettings.data?.oauth_domains;
			let providers = {};

			if (domains) {
				domains.map(
					(d) =>
						(providers[d.email_domain] = {
							social_login_key: d.social_login_key,
							provider_name: d.provider_name,
						}),
				);
			}

			return providers;
		},
		oauthEmailDomains() {
			return new Set(Object.keys(this.oauthProviders));
		},
		socialLoginKey() {
			return this.oauthProviders[this.emailDomain].social_login_key;
		},
		oauthProviderName() {
			return this.oauthProviders[this.emailDomain].provider_name;
		},
		title() {
			if (this.hasForgotPassword) {
				return 'Reset password';
			} else if (this.otpRequested) {
				return __('Verify your email address');
			} else if (this.isLogin) {
				if (this.saasProduct) {
					return `Log in to your account to start using ${this.saasProduct.title}`;
				}
				return __('Log in to your account');
			} else {
				if (this.saasProduct) {
					const lang = localStorage.getItem('lang');
					return lang === 'en' ? this.saasProduct.title_en : this.saasProduct.title;
				}

				return 'Create your Frappe Cloud account';
			}
		},
		subtitle() {
			if (this.hasForgotPassword) {
				return 'Enter your email address to reset your password';
			} else {
				if (this.saasProduct) {
					return `Get started and explore the easiest way to use ${this.saasProduct.title}`;
				}
				return 'Get started and explore the easiest way to use all Frappe apps';
			}
		},
	},
};
</script>
