<template>
	<div>
		<LoginBox :class="{ 'pointer-events-none': $resources.signup.loading }">
			<div>
				<!-- <div
					class="mb-4 w-36"
					v-if="!(resetPasswordEmailSent || hasForgotPassword)"
				>
					<SelectLanguage></SelectLanguage>
				</div> -->

				<div
					v-if="hasForgotPassword || saasProduct || isLogin"
					class="mb-4 text-3xl font-[500] text-gray-900"
				>
					<div class="flex items-center gap-[10px]" v-if="hasForgotPassword">
						<router-link
							class="text-base font-medium"
							:to="{
								name: 'Login',
								query: { ...$route.query, forgot: undefined }
							}"
						>
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
								<path d="M13.8297 18.9993C13.5271 19.0004 13.2403 18.8643 13.0497 18.6293L8.21968 12.6293C7.91636 12.2603 7.91636 11.7283 8.21968 11.3593L13.2197 5.35932C13.5731 4.93406 14.2044 4.87586 14.6297 5.22932C15.0549 5.58278 15.1131 6.21406 14.7597 6.63932L10.2897 11.9993L14.6097 17.3593C14.8594 17.659 14.912 18.0766 14.7444 18.4289C14.5769 18.7812 14.2198 19.0039 13.8297 18.9993Z" fill="#171717"/>
							</svg>
						</router-link>
						<div class="font-semibold text-[20px] leading-[21px] text-[#383838]">{{ $t('forgot_password') }}</div>
					</div>
					<div v-else-if="saasProduct">
						{{ $t('Auth_content_1') }}
						<span class="font-semibold">{{ saasProduct.title }}</span>
					</div>
					<div class="flex justify-center" v-else-if="isLogin">{{ $t('login') }}</div>
					<div class="flex justify-center" v-else>{{ $t('Sign_Up_Account') }}</div>
				</div>

				<div v-else class="mb-4 text-3xl font-[500] text-gray-900 flex justify-center">
					<div>{{ $t('Sign_Up_Account') }}</div>
				</div>

				<!-- <div
					class="mb-10"
					v-if="!(resetPasswordEmailSent || hasForgotPassword)"
				>
					<div class="text-base font-medium">
						<span v-if="$route.name == 'Login'">
							{{ $t('no_account_yet') }}?
						</span>
						<span v-else>{{ $t('already_have_an_account') }}? </span>
						<router-link
							class="text-base font-medium"
							:to="{
								name: $route.name == 'Login' ? 'Signup' : 'Login',
								query: { ...$route.query, forgot: undefined }
							}"
						>
							<span
								class="font-[600] text-red-600"
								v-if="$route.name == 'Login'"
							>
								{{ $t('register_now') }}
							</span>
							<span class="font-[600] text-red-600" v-else
								>{{ $t('login') }}.</span
							>
						</router-link>
					</div>
				</div> -->
				
				<form class="flex flex-col mt-8" @submit.prevent="submitForm">
					<template v-if="hasForgotPassword">
						<label class="mb-2 mt-5 text-base" for="email">Email</label>
						<FormControl
							id="email"
							size="lg"
							variant="outline"
							label=""
							placeholder="abc@mail.com"
							autocomplete="email"
							v-model="email"
						/>
						<ErrorMessage
							class="mt-2"
							:message="
								this.$translateMessage(inputError.email1) ||
								this.$translateMessage(ressetPassError)
							"
						/>
						<Button
							:class="
								email
									? 'my-6 h-9 text-base font-[700] text-white'
									: 'my-6 h-9 bg-[#DFE3E8] text-base font-[700] text-white'
							"
							variant="solid"
							:loading="$resources.resetPassword.loading"
							:disabled="!email"
						>
							{{ $t('send_link') }}
						</Button>
						
					</template>
					<template v-else-if="isLogin">
						<label class="mb-2 text-base" for="email">Email</label>
						<FormControl
							id="email"
							size="lg"
							variant="outline"
							label=""
							placeholder="abc@mail.com"
							autocomplete="email"
							v-model="email"
						/>
						<ErrorMessage
							class="mt-2"
							:message="this.$translateMessage(inputError.email)"
						/>
						<div class="relative mt-4">
							<div class="mb-2">
								<label class="text-base" for="password">{{
									$t('password')
								}}</label>
							</div>
							<FormControl
								id="password"
								size="lg"
								variant="outline"
								label=""
								:type="iconCheck ? 'password' : 'text'"
								placeholder="••••••••"
								v-model="password"
								name="password"
								autocomplete="current-password"
							/>
							<span
								class="absolute right-4 top-[60%]"
								v-on:click="changeIconEye"
							>
								<img
									v-if="iconCheck"
									src="../../assets/icon_eye.svg"
									alt="Eye Icon"
								/>
								<img
									v-if="iconCheck == false"
									src="../../assets/icon_eye_slash.svg"
									alt="Eye Icon Slash"
								/>
							</span>
						</div>
						<ErrorMessage
							class="mt-2"
							:message="this.$translateMessage(inputError.password)"
						/>
						<div class="mt-4 flex justify-end" v-if="isLogin">
							<router-link
								class="text-base"
								:to="{
									name: 'Login',
									query: { ...$route.query, forgot: 1 }
								}"
							>
								<span class="font-[400] text-[#171717] text-[14px]">
									{{ $t('forgot_password') }}?</span
								>
							</router-link>
						</div>
						<ErrorMessage
							class="mt-2"
							:message="this.$translateMessage(loginError)"
						/>
						<Button
							class="mt-7 h-9 text-base font-[700]"
							variant="solid"
						>
							{{ $t('login') }}
						</Button>
						<div class="mt-8 text-center border-t">
							<div class="transform -translate-y-1/2">
							<span class="px-2 text-xs leading-8 tracking-wider text-gray-800 bg-white">
								{{ $t('Or') }}
							</span>
							</div>
						</div>
						<div class="flex justify-center items-center" v-if="!disableSignup">
							<span class="font-normal text-[14px] leading-[17px] text-[#171717]">{{ $t('no_account_yet') }}?</span>
							<span>&nbsp;&nbsp;</span>
							<router-link class="text-base text-blue-500 font-semibold" 
							:to="{
								name: $route.name == 'Login' ? 'Signup' : 'Login',
								query: { ...$route.query, forgot: undefined }
							}">
							{{ $t('SIGN_UP') }}
							</router-link>
						</div>
					</template>
					<template v-else>
						<label class="mb-2 text-base" for="email">Email</label>
						<FormControl
							id="email"
							size="lg"
							variant="outline"
							label=""
							placeholder="abc@mail.com"
							autocomplete="email"
							v-model="email"
						/>
						<ErrorMessage
							class="mt-2"
							:message="this.$translateMessage(inputError.email1)"
						/>
						<Button
							class="mt-7 h-9 text-base font-[700]"
							:loading="$resources.signup.loading"
							variant="solid"
						>
							{{ $t('sign_up') }}
						</Button>
						<div class="mt-8 text-center border-t">
							<div class="transform -translate-y-1/2">
							<span class="px-2 text-xs leading-8 tracking-wider text-gray-800 bg-white">
								{{ $t('Or') }}
							</span>
							</div>
						</div>
						<div class="flex justify-center items-center" v-if="!disableSignup">
							<span class="font-normal text-[14px] leading-[17px] text-[#171717]">{{ $t('already_have_an_account') }}?</span>
							<span>&nbsp;&nbsp;</span>
							<router-link class="text-base text-blue-500 font-semibold" 
							:to="{
								name: $route.name == 'Login' ? 'Signup' : 'Login',
								query: { ...$route.query, forgot: undefined }
							}">
							{{ $t('LOGIN') }}
							</router-link>
						</div>
					</template>
					<ErrorMessage class="mt-2" :message="$resources.signup.error" />
				</form>
				<!-- <div class="flex flex-col" v-if="!hasForgotPassword">
					<div class="-mb-2 mt-6 border-t text-center">
						<div class="-translate-y-1/2 transform">
							<span
								class="font-sm relative bg-white px-2 text-base leading-8 text-gray-600"
							>
								{{ isLogin ? 'Hoặc đăng nhập bằng' : 'Hoặc tiếp tục bằng' }}
							</span>
						</div>
					</div>
					<div class="flex justify-center">
						<Button
							v-if="$resources.signupSettings.data?.enable_google_oauth === 1"
							class="rounded-[57px] px-4 py-5"
							variant="outline"
							:loading="$resources.googleLogin.loading"
							@click="$resources.googleLogin.submit()"
						>
							<div>
								<div class="flex items-center">
									<img src="../../assets/google_logo.svg" alt="Google Logo" />
									<span class="ml-2 text-base font-[500] text-gray-600"
										>Google</span
									>
								</div>
							</div>
						</Button>
					</div>
				</div> -->

				<Dialog v-model="resetPasswordEmailSent">
					<template #body-title>
						<h3 class="text-xl font-[500] text-gray-900">
							{{ $t('send_link_success') }}
						</h3>
					</template>
					<template #body-content>
						<div class="text-left text-base text-gray-600">
							{{ $t('Auth_content_3') }}
							<span class="text-gray-900">{{ email }}</span
							>{{ $t('Auth_content_4') }}
						</div>
					</template>
				</Dialog>

				<Dialog v-model="signupEmailSent">
					<template #body-title>
						<h3 class="text-xl font-[500] text-gray-900">
							{{ $t('registration_verification') }}
						</h3>
					</template>
					<template #body-content>
						<div class="text-center text-base text-gray-600">
							{{ $t('Auth_content_5') }}
							<span class="text-gray-900">{{ email }}</span
							>{{ $t('Auth_content_6') }}
						</div>
					</template>
				</Dialog>
			</div>
		</LoginBox>
	</div>
</template>

<script>
import LoginBox from '@/views/partials/LoginBox.vue';
import GoogleIconSolid from '@/components/icons/GoogleIconSolid.vue';
import SelectLanguage from '../../components/global/SelectLanguage.vue';
import { FormControl } from 'frappe-ui'

export default {
	name: 'Signup',
	components: {
		LoginBox,
		GoogleIconSolid,
		SelectLanguage,
		FormControl
	},
	data() {
		return {
			iconCheck: true,
			email: null,
			password: null,
			signupEmailSent: false,
			resetPasswordEmailSent: false,
			loginError: null,
			ressetPassError: null,
			signupError: null,
			inputError: {
				email: null,
				email1: null,
				password: null
			}
		};
	},
	resources: {
		signup() {
			return {
				url: 'press.api.account.signup',
				params: {
					email: this.email,
					referrer: this.getReferrerIfAny(),
					product: this.$route.query.product,
					lang: this.$i18n.locale
				},
				onSuccess() {
					this.signupEmailSent = true;
				}
			};
		},
		googleLogin() {
			return {
				url: 'press.api.oauth.google_login',
				onSuccess(r) {
					window.location = r;
				}
			};
		},
		resetPassword() {
			return {
				url: 'press.api.account.send_reset_password_email',
				params: {
					email: this.email
				},
				onSuccess() {
					this.resetPasswordEmailSent = true;
				},
				async onError(err) {
					let errMsg = err.messages[0] || '';
					if (errMsg.includes('does not exist')) {
						this.ressetPassError = 'Auth_content_8';
					} else if (
						errMsg.includes(
							'You hit the rate limit because of too many requests. Please try after sometime.'
						)
					) {
						this.ressetPassError = 'Auth_content_9';
					}
				}
			};
		},
		signupSettings() {
			return {
				url: 'press.api.account.signup_settings',
				params: {
					product: this.$route.query.product
				},
				auto: true
			};
		}
	},
	methods: {
		changeIconEye() {
			this.iconCheck = !this.iconCheck;
		},

		async submitForm() {
			let numErr = 0;
			if (this.isLogin) {
				// email
				let rs = this.$validdateInput(this.email, 'email1');
				numErr += rs[0];
				this.inputError.email = rs[1];
				// password
				rs = this.$validdateInput(this.password, 'password');
				numErr += rs[0];
				this.inputError.password = rs[1];

				if (numErr) {
					return;
				}
				if (this.email && this.password) {
					try {
						await this.$auth.login(this.email, this.password);
					} catch (error) {
						let arr_err = error.messages;
						let dic_err = {
							'Invalid login credentials': 'incorrect_account_or_password',
							'Your account has been locked and will resume after 60 seconds':
								'Auth_content_7'
						};

						this.loginError = arr_err.length
							? dic_err[arr_err[0]]
							: 'an_error_occurred';
					}
				}
			} else if (this.hasForgotPassword) {
				// email
				let rs = this.$validdateInput(this.email, 'email');
				numErr += rs[0];
				this.inputError.email1 = rs[1];

				if (numErr) {
					return;
				}
				this.$resources.resetPassword.submit();
			} else {
				// email
				let rs = this.$validdateInput(this.email, 'email');
				numErr += rs[0];
				this.inputError.email1 = rs[1];

				if (numErr) {
					return;
				}
				this.$resources.signup.submit();
			}
		},
		getReferrerIfAny() {
			const params = location.search;
			const searchParams = new URLSearchParams(params);
			return searchParams.get('referrer');
		}
	},
	computed: {
		saasProduct() {
			return this.$resources.signupSettings.data?.saas_product;
		},
		isLogin() {
			return this.$route.name == 'Login' && !this.$route.query.forgot;
		},
		hasForgotPassword() {
			return this.$route.name == 'Login' && this.$route.query.forgot;
		}
	}
};
</script>
