<template>
	<div class="grid min-h-screen grid-cols-1 md:grid-cols-2" v-if="!$resources.validateRequestKey.loading && email">
		<!-- Left Column: Background and Logo -->
		<div class="col-span-1 hidden h-screen bg-gray-50 md:flex">
			<div v-if="saasProduct" class="relative h-screen w-full overflow-hidden">
				<!-- Background Image -->
				<img 
					:src="saasProduct?.background" 
					alt="Background" 
					class="h-full w-full object-contain"
				/>

				<!-- Product Logo Overlay -->
				<!-- <div class="absolute left-8 top-8 z-10">
					<img 
						class="h-[80px] w-auto rounded-md shadow-lg transition-all duration-300 hover:shadow-xl" 
						:src="saasProduct?.logo" 
					/>
				</div> -->
			</div>

			<div v-else class="relative h-screen w-full overflow-hidden">
				<!-- Background Image -->
				<img 
					src="/public/bg1.png" 
					alt="Background" 
					class="h-full w-full object-contain" 
				/>

				<!-- Logo on top -->
				<div class="absolute left-8 top-8 z-10">
					<FCLogo class="h-16 w-auto drop-shadow-lg transition-all duration-300 hover:drop-shadow-xl" />
				</div>
			</div>
		</div>

		<!-- Right Column: Auth Forms - set to full width and height -->
		<div class="relative col-span-1 flex h-full w-full items-center justify-center py-8 md:overflow-auto md:bg-white">
			<LoginBox 
				:title="invitedBy ? __('Invitation to join') : __('Set up your account')"
				:subtitle="invitedBy ? `Invitation by ${invitedBy}` : ''"
				class="w-full h-full md:h-auto md:max-w-md transition-all duration-300 shadow-xl rounded-xl"
			>
				<template v-slot:logo v-if="saasProduct">
					<div class="flex mb-4 w-full justify-center">
						<img 
							class="h-16 w-auto rounded-md shadow-md transition-all duration-300 hover:shadow-lg" 
							:src="saasProduct?.logo" 
							alt="Product Logo"
						/>
					</div>
				</template>
				
				<form class="mt-6 flex flex-col space-y-4 w-full" @submit.prevent="submitForm">
					<template v-if="is2FA">
						<FormControl 
							label="2FA Code from your Authenticator App" 
							placeholder="123456"
							v-model="twoFactorCode" 
							variant="outline"
							required 
							class="w-full focus-within:shadow-sm transition-all duration-300"
						/>
						<Button 
							class="mt-4 w-full transform transition-all duration-300 hover:shadow-md hover:-translate-y-0.5" 
							:loading="$resources.verify2FA.loading" 
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
						<ErrorMessage class="mt-2 w-full" :message="$resources.verify2FA.error" />
					</template>
					<template v-else>
						<div class="space-y-4 w-full">
							<template v-if="!userExists">
								<div class="flex gap-2 w-full">
									<FormControl 
										:label="__('First name')" 
										type="text" 
										v-model="firstName" 
										name="fname"
										autocomplete="given-name" 
										variant="outline" 
										required
										:disabled="Boolean(oauthSignup)" 
										class="w-full focus-within:shadow-sm transition-all duration-300"
									/>
									<FormControl 
										:label="__('Last name')" 
										type="text" 
										v-model="lastName" 
										name="lname"
										autocomplete="family-name" 
										variant="outline" 
										required
										:disabled="Boolean(oauthSignup)" 
										class="w-full focus-within:shadow-sm transition-all duration-300"
									/>
								</div>
							</template>
							<FormControl 
								label="Email" 
								type="text" 
								:modelValue="email" 
								variant="outline" 
								disabled 
								class="w-full"
							/>
							<FormControl 
								type="select" 
								:options="countries" 
								v-if="!isInvitation" 
								:label="__('Country')"
								v-model="country" 
								variant="outline" 
								required 
								class="w-full focus-within:shadow-sm transition-all duration-300"
							/>
						</div>
						<ErrorMessage class="mt-4 w-full" :message="$resources.setupAccount.error" />
						<Button 
							class="mt-4 w-full transform transition-all duration-300 hover:shadow-md hover:-translate-y-0.5" 
							variant="solid" 
							:loading="$resources.setupAccount.loading"
						>
							{{
								is2FA ? __('Verify') : isInvitation ? __('Accept') : __('Create account')
							}}
						</Button>
					</template>
				</form>
				
				<!-- Language Selector -->
				<template v-slot:footer>
					<div class="flex items-center justify-center py-4 border-t border-gray-100 mt-6 w-full">
						<SelectLanguage class="w-full opacity-80 hover:opacity-100 transition-opacity duration-300" />
					</div>
				</template>
			</LoginBox>
		</div>
	</div>

	<!-- Trường hợp không có email -->
	<div class="mt-20 px-6 text-center flex flex-col items-center justify-center" v-else-if="!$resources.validateRequestKey.loading && !email">
		<div class="p-6 bg-white rounded-lg shadow-md max-w-md">
			<p class="text-gray-700 mb-4">Verification link is invalid or expired.</p>
			<Link to="/signup" class="text-blue-600 hover:text-blue-800 transition-colors duration-300 font-medium">Sign up</Link>
			<p class="mt-2">for a new account.</p>
		</div>
	</div>

	<!-- Loading -->
	<div v-else class="flex items-center justify-center min-h-screen">
		<div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
	</div>
</template>

<script>
import LoginBox from '../components/auth/LoginBox.vue';
import Link from '@/components/Link.vue';
import Form from '@/components/Form.vue';
import { DashboardError } from '../utils/error';
import SelectLanguage from '../components/SelectLanguage.vue';

export default {
	name: 'SetupAccount',
	components: {
		LoginBox,
		Link,
		Form,
		SelectLanguage
	},
	props: ['requestKey', 'joinRequest'],
	data() {
		return {
			email: null,
			firstName: null,
			lastName: null,
			errorMessage: null,
			userExists: null,
			twoFactorCode: null,
			invitationToTeam: null,
			isInvitation: null,
			oauthSignup: 0,
			oauthDomain: false,
			country: 'Vietnam', // Default value set to Vietnam
			invitedBy: null,
			invitedByParentTeam: false,
			countries: [],
			saasProduct: null,
			signupValues: {},
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
						: null,
				},
				auto: true,
				onSuccess(res) {
					if (res && res.email) {
						this.email = res.email;
						this.firstName = res.first_name;
						this.lastName = res.last_name;
						// Only override the default Vietnam value if response has a specific country
						this.country = res.country || this.country; 
						this.userExists = res.user_exists;
						this.invitationToTeam = res.team;
						this.invitedBy = res.invited_by;
						this.isInvitation = res.is_invitation;
						this.invitedByParentTeam = res.invited_by_parent_team;
						this.oauthSignup = res.oauth_signup;
						this.oauthDomain = res.oauth_domain;
						this.countries = res.countries;
						this.saasProduct = res.product_trial;
					}
				},
			};
		},
		setupAccount() {
			return {
				url: 'press.api.account.setup_account',
				params: {
					key: this.requestKey,
					first_name: this.firstName,
					last_name: this.lastName,
					country: this.country,
					is_invitation: this.isInvitation,
					user_exists: this.userExists,
					invited_by_parent_team: this.invitedByParentTeam,
					oauth_signup: this.oauthSignup,
					oauth_domain: this.oauthDomain,
				},
				onSuccess() {
					// let path = '/dashboard/create-site/plan'
					let path = '/dashboard/create-site/app-selector';
					//Đăng ký account xong -> 
					if (this.saasProduct) {
						path = `/dashboard/create-site/${this.saasProduct.name}/plan`;
					}
					if (this.isInvitation) {
						path = '/dashboard/sites';
					}
					window.location.href = path;
				},
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
				onSuccess() {
					this.$resources.setupAccount.submit();
				},
			};
		},
	},
	computed: {
		is2FA() {
			return (
				this.$route.name === 'Setup Account' && this.$route.query.two_factor
			);
		},
	},
	methods: {
		submitForm() {
			if (this.invitedBy) {
				this.$resources.is2FAEnabled.submit(
					{
						user: this.email,
					},
					{
						onSuccess: (two_factor_enabled) => {
							if (two_factor_enabled) {
								this.$router.push({
									name: 'Setup Account',
									query: {
										...this.$route.query,
										two_factor: 1,
									},
								});
							} else {
								this.$resources.setupAccount.submit();
							}
						},
					},
				);
			} else {
				this.$resources.setupAccount.submit();
			}
		},
	},
};
</script>
