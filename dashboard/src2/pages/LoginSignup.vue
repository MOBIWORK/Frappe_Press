<template>
	<div class="flex h-screen overflow-hidden">
		<div class="w-full overflow-auto">
			<LoginBox
				:title="title"
				:subtitle="subtitle"
				:class="{ 'pointer-events-none': $resources.signup.loading || $resources.checkEmailExists.loading }"
			>
				<template v-slot:default>
					<!-- Unified Email Form - Initial Step -->
					<div v-if="showEmailForm && !is2FA && !hasForgotPassword && !resetPasswordEmailSent">
						<form class="flex flex-col" @submit.prevent="handleEmailSubmit">
							<FormControl
								label="Email"
								type="email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								v-model="email"
								variant="outline"
								required
							/>
							<Button
								class="mt-4"
								:loading="$resources.checkEmailExists.loading"
								variant="solid"
								type="submit"
							>
								Send verification code
							</Button>
						</form>
						
						<!-- Terms for new users -->
						<div class="mt-4 flex flex-col">
							<div>
								<span class="text-base font-normal text-gray-600">
									{{ 'By continuing, you agree to our ' }}
								</span>
								<a
									class="text-base font-normal text-gray-900 underline hover:text-gray-700"
									href="https://frappecloud.com/policies"
								>
									Terms & Policies
								</a>
							</div>
						</div>
					</div>

					<!-- Login Form - When user exists -->
					<div v-else-if="showLoginForm && !is2FA && !hasForgotPassword && !resetPasswordEmailSent">
						<form class="flex flex-col">
							<FormControl
								label="Email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								v-model="email"
								:disabled="true"
								variant="outline"
								required
							/>

							<!-- OTP Verification Input (when OTP is sent) -->
							<template v-if="otpSent">
								<FormControl
									class="mt-4"
									label="Verification code"
									placeholder="123456"
									variant="outline"
									ref="otpInput"
									v-model="otp"
									required
								/>
								<div class="mt-4 space-y-2">
									<Button
										class="w-full"
										:loading="$resources.verifyOTPAndLogin.loading"
										variant="solid"
										@click="verifyOTPAndLogin"
									>
										Submit verification code
									</Button>
									<Button
										class="w-full"
										:loading="$resources.sendOTP.loading"
										variant="outline"
										:disabled="otpResendCountdown > 0"
										@click="$resources.sendOTP.submit()"
									>
										Resend verification code
										{{
											otpResendCountdown > 0
												? `in ${otpResendCountdown} seconds`
												: ''
										}}
									</Button>
								</div>
							</template>

							<!-- Loading state while sending OTP -->
							<template v-else>
								<div class="mt-4">
									<Button
										class="w-full"
										:loading="$resources.sendOTP.loading"
										variant="solid"
										disabled
									>
										Sending verification code...
									</Button>
								</div>
							</template>
						</form>

						<div class="mt-4">
							<Button
								variant="ghost"
								@click="resetToEmailForm"
								class="text-sm"
							>
								← Use different email
							</Button>
						</div>

						<!-- Error Messages -->
						<ErrorMessage
							class="mt-2"
							:message="
								$resources.sendOTP.error ||
								$resources.verifyOTPAndLogin.error
							"
						/>
					</div>

					<!-- Signup Form - When user doesn't exist -->
					<div v-else-if="showSignupForm && !otpRequested && !resetPasswordEmailSent">
						<form class="flex flex-col">
							<FormControl
								label="Email"
								type="email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								variant="outline"
								v-model="email"
								:disabled="true"
								required
							/>
							<div class="mt-4">
								<Button
									class="w-full"
									:loading="$resources.signup.loading"
									variant="solid"
									disabled
								>
									Creating account and sending verification code...
								</Button>
							</div>
						</form>

						<div class="mt-4">
							<Button
								variant="ghost"
								@click="resetToEmailForm"
								class="text-sm"
							>
								← Use different email
							</Button>
						</div>

						<ErrorMessage class="mt-2" :message="$resources.signup.error" />
					</div>

					<!-- 2FA Section -->
					<div v-else-if="is2FA">
						<form class="flex flex-col" @submit.prevent="submitForm">
							<FormControl
								label="2FA Code from your Authenticator App"
								placeholder="123456"
								v-model="twoFactorCode"
								required
								variant="outline"
							/>
							<Button
								class="mt-4"
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
								Verify
							</Button>
							<ErrorMessage
								class="mt-2"
								:message="$resources.verify2FA.error"
							/>
						</form>
					</div>

					<!-- Forgot Password Section -->
					<div v-else-if="hasForgotPassword">
						<form class="flex flex-col" @submit.prevent="submitForm">
							<FormControl
								label="Email"
								type="email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								v-model="email"
								variant="outline"
								required
							/>
							<router-link
								class="mt-2 text-sm"
								:to="{
									name: 'Login',
									query: { ...$route.query, forgot: undefined },
								}"
							>
								I remember my password
							</router-link>
							<Button
								class="mt-4"
								:loading="$resources.resetPassword.loading"
								variant="solid"
							>
								Reset Password
							</Button>
						</form>
					</div>

					<!-- OTP Verification for Signup -->
					<div v-else-if="otpRequested">
						<form class="flex flex-col">
							<FormControl
								label="Email"
								type="email"
								placeholder="johndoe@mail.com"
								autocomplete="email"
								v-model="email"
								variant="outline"
								:disabled="true"
								required
							/>
							<FormControl
								label="Verification code"
								type="text"
								class="mt-4"
								placeholder="123456"
								maxlength="6"
								v-model="otp"
								required
								variant="outline"
							/>
							<ErrorMessage
								class="mt-2"
								:message="$resources.verifyOTP.error"
							/>
							<Button
								class="mt-4"
								variant="solid"
								:loading="$resources.verifyOTP.loading"
								@click="$resources.verifyOTP.submit()"
							>
								Verify
							</Button>
							<Button
								class="mt-2"
								variant="outline"
								:loading="$resources.resendOTP.loading"
								@click="$resources.resendOTP.submit()"
								:disabled="otpResendCountdown > 0"
							>
								Resend verification code
								{{
									otpResendCountdown > 0
										? `in ${otpResendCountdown} seconds`
										: ''
								}}
							</Button>
						</form>
						
						<div class="mt-4 space-y-2">
							<div>
								<span class="text-base font-normal text-gray-600">
									{{ 'By signing up, you agree to our ' }}
								</span>
								<a
									class="text-base font-normal text-gray-900 underline hover:text-gray-700"
									href="https://frappecloud.com/policies"
								>
									Terms & Policies
								</a>
							</div>
						</div>
					</div>

					<!-- Reset Password Success -->
					<div
						class="text-p-base text-gray-700"
						v-else-if="resetPasswordEmailSent"
					>
						<p>
							We have sent an email to
							<span class="font-semibold">{{ email }}</span
							>. Please click on the link received to reset your password.
						</p>
					</div>
				</template>
				<template v-slot:logo v-if="saasProduct">
					<div class="flex space-x-2">
						<img
							class="inline-block h-[38px] w-[38px] rounded-sm"
							:src="saasProduct?.logo"
						/>
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

export default {
	name: 'Signup',
	components: {
		LoginBox,
		GoogleIcon,
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
					toast.success('Verification code sent to your email');
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
							this.$router.push({
								name: 'Login',
								query: {
									redirect: `/dashboard/create-site/${this.$route.query.product}/setup`,
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
					toast.success('Verification code sent to your email');
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
					toast.success('Verification code sent to your email');
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
					this.afterLogin(res);
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
			this.$resources.is2FAEnabled.submit(
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
							await this.$resources.verifyOTPAndLogin.submit();
						}
					},
				},
			);
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
			let loginRoute = `/dashboard${res.dashboard_route || '/'}`;
			// if query param redirect is present, redirect to that route
			if (this.$route.query.redirect) {
				loginRoute = this.$route.query.redirect;
			}
			localStorage.setItem('login_email', this.email);
			window.location.href = loginRoute;
		},
		
		// New methods for unified flow
		handleEmailSubmit() {
			if (this.email) {
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
				return 'Verify your email address';
			} else if (this.isLogin) {
				if (this.saasProduct) {
					return `Log in to your account to start using ${this.saasProduct.title}`;
				}
				return 'Log in to your account';
			} else {
				if (this.saasProduct) {
					return `Sign up to create your ${this.saasProduct.title} site`;
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
