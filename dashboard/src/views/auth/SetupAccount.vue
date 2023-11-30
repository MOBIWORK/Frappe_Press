<template>
	<LoginBox>
		<div v-if="!dashboardRoute">
			<div class="mb-4 w-36">
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
						<img
							v-if="iconCheck"
							src="../../assets/icon_flag_vi.svg"
							alt="Eye Icon"
						/>
					</template>
				</FormControl>
			</div>
			<div v-if="!$resources.validateRequestKey.loading && email">
				<div class="mb-4 text-3xl font-[500] text-gray-900">
					<div v-if="!isInvitation">Đăng ký tài khoản</div>
					<div v-else>Lời mời tham gia nhóm: {{ invitationToTeam }}</div>
				</div>
				<div class="mb-10">
					<div class="text-base font-medium">
						<span>Đã có tài khoản? </span>
						<router-link
							class="text-base font-medium"
							:to="{
								name: $route.name == 'Login' ? 'Signup' : 'Login',
								query: { ...$route.query, forgot: undefined }
							}"
						>
							<span class="font-[600] text-red-600">Đăng nhập.</span>
						</router-link>
					</div>
				</div>
				<form
					class="flex flex-col"
					@submit.prevent="$resources.setupAccount.submit()"
				>
					<div>
						<div>
							<div class="mb-2 mt-4">
								<label class="text-base" for="email">Email</label>
							</div>
							<FormControl
								id="email"
								size="lg"
								variant="outline"
								v-if="oauthSignup == 0"
								label=""
								type="text"
								:modelValue="email"
								disabled
							/>
						</div>
						<template v-if="oauthSignup == 0">
							<div>
								<div class="mb-2 mt-4">
									<label class="text-base" for="lname">Họ</label>
								</div>
								<FormControl
									id="lname"
									size="lg"
									variant="outline"
									placeholder="---"
									label=""
									type="text"
									v-model="lastName"
									name="lname"
									autocomplete="family-name"
									required
								/>
							</div>
							<div>
								<div class="mb-2 mt-4">
									<label class="text-base" for="fname">Tên</label>
								</div>
								<FormControl
									id="fname"
									size="lg"
									variant="outline"
									placeholder="---"
									label=""
									type="text"
									v-model="firstName"
									name="fname"
									autocomplete="given-name"
									required
								/>
							</div>
							<div class="relative">
								<div class="mb-2 mt-4">
									<label class="text-base" for="password">Mật khẩu</label>
								</div>
								<FormControl
									id="password"
									size="lg"
									variant="outline"
									placeholder="••••••••"
									label=""
									:type="iconCheck ? 'password' : 'text'"
									v-model="password"
									name="password"
									autocomplete="new-password"
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
						</template>
						<div>
							<div class="mb-2 mt-4">
								<label class="text-base" for="country">Đất nước</label>
							</div>
							<FormControl
								id="country"
								type="select"
								size="lg"
								variant="outline"
								placeholder="---"
								label=""
								:options="countries"
								v-if="!isInvitation"
								v-model="country"
								required
							/>
						</div>
						<Form
							v-if="signupFields.length > 0"
							:fields="signupFields"
							v-model="signupValues"
						/>
						<div class="mt-4 flex items-start">
							<label class="text-base text-gray-900">
								<FormControl
									size="lg"
									type="checkbox"
									v-model="termsAccepted"
								/>
								<!-- By clicking on
								<span>{{ isInvitation ? 'Accept' : 'Submit' }}</span
								>, you accept our -->
								Tôi đã đọc và đồng ý với
								<Link class="border-none" href="#" target="_blank"
									><span class="text-blue-500 hover:text-blue-700"
										>Điều khoản dịch vụ
									</span></Link
								>
								và
								<Link class="border-none" href="#" target="_blank"
									><span class="text-blue-500 hover:text-blue-700">
										Chính sách quyền riêng tư
									</span></Link
								>
								<!-- &#38;
								<Link href="https://frappecloud.com/cookie-policy" target="_blank">
									Cookie Policy
								</Link> -->
							</label>
						</div>
					</div>
					<ErrorMessage class="mt-4" :message="$resources.setupAccount.error" />
					<Button
						class="my-6 h-9 bg-red-600 text-base font-[700] text-white hover:bg-red-700"
						variant="solid"
						:loading="$resources.setupAccount.loading"
					>
						{{ isInvitation ? 'Chấp nhận' : 'Đăng ký' }}
					</Button>
				</form>
			</div>
			<div
				class="text-center"
				v-else-if="!$resources.validateRequestKey.loading && !email"
			>
				Liên kết xác minh không hợp lệ hoặc đã hết hạn.
				<Link to="/signup"
					><span class="font-[600] text-red-600 hover:text-red-700"
						>Đăng ký</span
					></Link
				>
				một tài khoản mới.
			</div>
			<div v-else></div>
		</div>
		<div v-else>
			<div class="text-center">
				<div class="mb-12 text-center">
					<div class="mb-10 flex justify-center">
						<img src="../../assets/icon_tick.svg" alt="Key Icon" />
					</div>
					<div class="text-3xl">Đăng ký thành công</div>
					<div class="mt-2 text-lg font-[400] text-gray-600">
						Tài khoản của bạn đã được tạo thành công, đăng nhập để trải nghiệm
						dịch vụ của chúng tôi.
					</div>
				</div>
				<router-link :to="dashboardRoute">
					<Button
						class="my-6 h-9 w-full bg-red-600 text-base font-[700] text-white hover:bg-red-700"
						variant="solid"
					>
						Trở về trang đăng nhập
					</Button>
				</router-link>
			</div>
		</div>
	</LoginBox>
</template>

<script>
import LoginBox from '@/views/partials/LoginBox.vue';
import Link from '@/components/Link.vue';
import Form from '@/components/Form.vue';

export default {
	name: 'SetupAccount',
	components: {
		LoginBox,
		Link,
		Form
	},
	props: ['requestKey', 'joinRequest'],
	data() {
		return {
			iconCheck: true,
			dashboardRoute: null,
			email: null,
			firstName: null,
			lastName: null,
			password: null,
			errorMessage: null,
			userExists: null,
			invitationToTeam: null,
			isInvitation: null,
			oauthSignup: 0,
			country: null,
			termsAccepted: false,
			invitedByParentTeam: false,
			countries: [],
			saasProduct: null,
			signupValues: {}
		};
	},
	resources: {
		validateRequestKey() {
			return {
				url: 'press.api.account.validate_request_key',
				params: {
					key: this.requestKey,
					timezone: window.Intl
						? Intl.DateTimeFormat().resolvedOptions().timeZone
						: null
				},
				auto: true,
				onSuccess(res) {
					if (res && res.email) {
						this.email = res.email;
						this.firstName = res.first_name;
						this.lastName = res.last_name;
						this.country = res.country;
						this.userExists = res.user_exists;
						this.invitationToTeam = res.team;
						this.isInvitation = res.is_invitation;
						this.invitedByParentTeam = res.invited_by_parent_team;
						this.oauthSignup = res.oauth_signup;
						this.countries = res.countries;
						this.saasProduct = res.saas_product;
					}
				}
			};
		},
		setupAccount() {
			return {
				url: 'press.api.account.setup_account',
				params: {
					key: this.requestKey,
					password: this.password,
					first_name: this.firstName,
					last_name: this.lastName,
					country: this.country,
					is_invitation: this.isInvitation,
					user_exists: this.userExists,
					invited_by_parent_team: this.invitedByParentTeam,
					accepted_user_terms: this.termsAccepted,
					oauth_signup: this.oauthSignup,
					signup_values: this.signupValues
				},
				onSuccess(res) {
					if (res) {
						this.dashboardRoute = res.dashboard_route || '/';
						// this.$router.push(res.dashboard_route || '/');
					}
					window.location.reload();
				}
			};
		}
	},
	methods: {
		showFormFields() {
			let show = true;
			show = !this.userExists;
			show = this.oauthSignup == 0;
			return show;
		},

		changeIconEye() {
			this.iconCheck = !this.iconCheck;
		}
	},
	computed: {
		signupFields() {
			let fields = this.saasProduct?.signup_fields || [];
			return fields.map(df => {
				if (df.fieldtype == 'Select') {
					df.options = df.options
						.split('\n')
						.map(o => o.trim())
						.filter(Boolean);
				}
				df.required = true;
				return df;
			});
		}
	}
};
</script>
