<template>
	<div>
		<LoginBox :class="{ 'pointer-events-none': $resources.signup.loading }">
			<div>
				<div
					class="mb-4 w-36"
					v-if="!(resetPasswordEmailSent || hasForgotPassword)"
				>
					<FormControl
						type="select"
						:options="[
							{
								label: 'Tiếng Việt',
								value: 'vi'
							}
						]"
						size="md"
						variant="outline"
						placeholder="Placeholder"
						:disabled="false"
						label=""
						modelValue="vi"
					>
						<template #prefix>
							<img src="../../assets/icon_flag_vi.svg" alt="Eye Icon" />
						</template>
					</FormControl>
				</div>

				<div
					v-if="hasForgotPassword || saasProduct || isLogin"
					class="mb-4 text-3xl font-[500] text-gray-900"
				>
					<div class="text-center" v-if="hasForgotPassword">
						<div class="mb-10 flex justify-center">
							<img
								v-if="iconCheck"
								src="../../assets/icon_key.svg"
								alt="Key Icon"
							/>
						</div>
						<div>Quên mật khẩu</div>
					</div>
					<div v-else-if="saasProduct">
						Đăng nhập vào MBW Cloud để bắt đầu sử dụng
						<span class="font-semibold">{{ saasProduct.title }}</span>
					</div>
					<div v-else-if="isLogin">Đăng nhập</div>
					<div v-else>Đăng ký</div>
				</div>

				<div v-else class="mb-4 text-3xl font-[500] text-gray-900">
					<div>Đăng ký</div>
				</div>

				<div
					class="mb-10"
					v-if="!(resetPasswordEmailSent || hasForgotPassword)"
				>
					<div class="text-base font-medium">
						<span v-if="$route.name == 'Login'"> Chưa có tài khoản? </span>
						<span v-else>Đã có tài khoản? </span>
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
								Đăng ký ngay
							</span>
							<span class="font-[600] text-red-600" v-else>Đăng nhập.</span>
						</router-link>
					</div>
				</div>
				<div
					class="text-center text-lg font-[400] text-gray-600"
					v-if="hasForgotPassword"
				>
					Một liên kết đặt lại mật khẩu sẽ được gửi tới email của bạn. Nếu bạn
					không nhận được email trong vòng vài phút, vui lòng thử lại.
				</div>
				<form class="flex flex-col" @submit.prevent="submitForm">
					<template v-if="hasForgotPassword">
						<label class="mb-2 mt-5 text-base" for="email">Email</label>
						<FormControl
							id="email"
							size="lg"
							variant="outline"
							label=""
							type="email"
							placeholder="abc@mail.com"
							autocomplete="email"
							v-model="email"
							required
						/>
						<Button
							:class="
								email
									? 'my-6 h-9 bg-red-600 text-base font-[700] text-white hover:bg-red-700'
									: 'my-6 h-9 bg-[#DFE3E8] text-base font-[700] text-white'
							"
							variant="solid"
							:loading="$resources.resetPassword.loading"
							:disabled="!email"
						>
							Gửi liên kết
						</Button>
						<router-link
							class="mb-2 text-base"
							v-if="hasForgotPassword"
							:to="{
								name: 'Login',
								query: { ...$route.query, forgot: undefined }
							}"
						>
							<div class="flex justify-center">
								<img
									v-if="iconCheck"
									src="../../assets/icon_left.svg"
									alt="Eye Icon"
								/>
								<span class="font-[600]"> Trở về trang đăng nhập</span>
							</div>
						</router-link>
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
							required
						/>
						<div class="relative mt-4">
							<div class="mb-2">
								<label class="text-base" for="password">Mật khẩu</label>
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
								required
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
						<div class="mt-2" v-if="isLogin">
							<router-link
								class="text-base"
								:to="{
									name: 'Login',
									query: { ...$route.query, forgot: 1 }
								}"
							>
								<span class="font-[600] text-red-600"> Quên mật khẩu?</span>
							</router-link>
						</div>
						<Button
							class="mt-4 h-9 bg-red-600 text-base font-[700] hover:bg-red-700"
							variant="solid"
						>
							Đăng nhập
						</Button>
						<ErrorMessage class="mt-2" :message="loginError" />
					</template>
					<template v-else>
						<label class="mb-2 text-base" for="email">Email</label>
						<FormControl
							id="email"
							size="lg"
							variant="outline"
							label=""
							type="email"
							placeholder="abc@mail.com"
							autocomplete="email"
							v-model="email"
							required
						/>
						<Button
							class="mt-4 h-9 bg-red-600 text-base font-[700] hover:bg-red-700"
							:loading="$resources.signup.loading"
							variant="solid"
						>
							Đăng ký
						</Button>
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
							Gửi liên kết thành công
						</h3>
					</template>
					<template #body-content>
						<div class="text-left text-base text-gray-600">
							Chúng tôi đã gửi một đường dẫn liên kết tới email
							<span class="text-gray-900">{{ email }}</span
							>. Vui lòng kiểm tra hộp thư để thiết lập lại mật khẩu của bạn.
						</div>
					</template>
				</Dialog>

				<Dialog v-model="signupEmailSent">
					<template #body-title>
						<h3 class="text-xl font-[500] text-gray-900">Xác thực đăng ký</h3>
					</template>
					<template #body-content>
						<div class="text-center text-base text-gray-600">
							Chúng tôi đã gửi email tới
							<span class="text-gray-900">{{ email }}</span
							>. Vui lòng nhấp vào liên kết nhận được để xác minh email và thiết
							lập tài khoản của bạn.
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

export default {
	name: 'Signup',
	components: {
		LoginBox,
		GoogleIconSolid
	},
	data() {
		return {
			iconCheck: true,
			email: null,
			password: null,
			signupEmailSent: false,
			resetPasswordEmailSent: false,
			loginError: null
		};
	},
	resources: {
		signup() {
			return {
				url: 'press.api.account.signup',
				params: {
					email: this.email,
					referrer: this.getReferrerIfAny(),
					product: this.$route.query.product
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
			if (this.isLogin) {
				if (this.email && this.password) {
					try {
						await this.$auth.login(this.email, this.password);
					} catch (error) {
						let arr_err = error.messages;
						let dic_err = {
							'Invalid login credentials':
								'Tải khoản hoặc mật khẩu không chính xác.'
						};

						this.loginError = arr_err.length
							? dic_err[arr_err[0]]
							: 'Có lỗi xảy ra.';
					}
				}
			} else if (this.hasForgotPassword) {
				this.$resources.resetPassword.submit();
			} else {
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
