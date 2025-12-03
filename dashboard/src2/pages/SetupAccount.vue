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
								:label="__('Phone Number')" 
								type="tel" 
								v-model="phone" 
								variant="outline" 
								required
								class="w-full focus-within:shadow-sm transition-all duration-300"
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
				
				<!-- Voucher Display -->
				<template v-slot:voucher v-if="displayVouchers.length > 0">
					<div class="mt-6 w-full overflow-y-scroll max-h-48">
						<div
							v-for="voucher in displayVouchers"
							:key="voucher.code"
							class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4 shadow-sm mb-3"
						>
							<div class="flex items-start gap-3">
								<div class="flex-1 min-w-0">
									<h3 class="text-sm font-semibold text-gray-900">
										{{ voucher.name }}
									</h3>
									<div v-if="voucher.description" class="text-xs text-gray-600 mt-2" v-html="voucher.description"></div>
								</div>
								<div class="flex-shrink-0">
									<svg
										xmlns="http://www.w3.org/2000/svg"
										class="h-5 w-5 text-green-500"
										fill="none"
										viewBox="0 0 24 24"
										stroke="currentColor"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
										/>
									</svg>
								</div>
							</div>
						</div>
					</div>
				</template>
				
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

	<FloatingVoucher :vouchers="displayVouchers" />
</template>

<script>
import LoginBox from '../components/auth/LoginBox.vue';
import Link from '@/components/Link.vue';
import Form from '@/components/Form.vue';
import FloatingVoucher from '../components/FloatingVoucher.vue';
import { DashboardError } from '../utils/error';
import SelectLanguage from '../components/SelectLanguage.vue';
import { toast } from 'vue-sonner';
import { getToastErrorMessage } from '../utils/toast';
export default {
	name: 'SetupAccount',
	components: {
		LoginBox,
		Link,
		Form,
		SelectLanguage,
		FloatingVoucher
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
			country: 'Vietnam',
			invitedBy: null,
			invitedByParentTeam: false,
			countries: [],
			saasProduct: null,
			signupValues: {},
			phone: '',
			utm_source: '',
			utm_campaign: '',
			displayVouchers: [],
			voucherProduct: '',
			teamName: '',
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
					phone: this.phone,
					country: this.country,
					language: this.getSelectedLanguage(),  
					is_invitation: this.isInvitation,
					user_exists: this.userExists,
					invited_by_parent_team: this.invitedByParentTeam,
					oauth_signup: this.oauthSignup,
					oauth_domain: this.oauthDomain,
					utm_source: this.utm_source,
					utm_campaign: this.utm_campaign,
				},
				async onSuccess(response) {
					if (this.displayVouchers.length > 0 && response && response.team) {
						this.teamName = response.team;
						localStorage.setItem('applied_vouchers', JSON.stringify({
							vouchers: this.displayVouchers,
							team: response.team
						}));
						
						await this.$resources.applyVouchersResource.submit();
					}
					let path = '/dashboard/create-site/app-selector';
					if (this.saasProduct && (this.saasProduct.name === 'go1_cms' || this.saasProduct.name === 'mbw_cms')) {
						path = `/dashboard/create-site/${this.saasProduct.name}/template`;
					} else if (this.saasProduct) {
						path = `/dashboard/create-site/${this.saasProduct.name}/plan`;
					}
					if (this.isInvitation) {
						path = '/dashboard/sites';
					}
					window.location.href = path;
				},
				validate(){
					const phone = this.phone.trim();
					const digitsOnly = /^\d+$/;
				
					if (!digitsOnly.test(phone)) {
						toast.error(__('Phone number can only contain digits'));
						return false;
					}
					if (this.language === 'vi' && phone.length !== 10) {
						toast.error(__('Phone number must be 10 digits'));
						return false;
					}
					return true;
				}
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
		applyVouchersResource() {
			return {
				url: 'press.api.voucher.validate_and_apply_vouchers',
				makeParams() {
					return {
						team: this.teamName,
						product: this.voucherProduct,
						utm_source: this.utm_source,
						utm_campaign: this.utm_campaign
					};
				},
				auto: false,
				onSuccess(response) {
					if (response && response.success && response.applied_count > 0) {
						toast.success(__(`Successfully applied ${response.applied_count} voucher(s) to your account!`));
						localStorage.removeItem('eligible_vouchers');
					}
				},
				onError(error) {
					toast.error(getToastErrorMessage(error, 'Failed to apply vouchers'));
				}
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
		getSelectedLanguage() {
			// 1. Check if SelectLanguage component has set a value
			const languageSelector = this.$children?.find(child => child.$options.name === 'SelectLanguage');
			if (languageSelector && languageSelector.defaultLanguage) {
				return languageSelector.defaultLanguage;
			}
			
			// 2. Check localStorage
			const storedLang = localStorage.getItem('lang');
			if (storedLang) {
				return storedLang;
			}
			
			// 3. Default to Vietnamese
			localStorage.setItem('lang', 'vi');
			return 'vi';
		},
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
		
		loadVouchers() {
			try {
				const storedData = sessionStorage.getItem('eligible_vouchers');
				if (storedData) {
					const data = JSON.parse(storedData);
					this.displayVouchers = data.vouchers || [];
					this.voucherProduct = data.product || '';
					// Update utm params if they exist in stored data
					if (data.utm_source) this.utm_source = data.utm_source;
					if (data.utm_campaign) this.utm_campaign = data.utm_campaign;
				}
			} catch (error) {
			console.error('Error loading vouchers:', error);
		}
	},
		
		formatCurrency(amount) {
			if (!amount) return '0đ';
			return new Intl.NumberFormat('vi-VN', {
				style: 'currency',
				currency: 'VND'
			}).format(amount);
		},
		
		formatDate(date) {
			if (!date) return '';
			return new Date(date).toLocaleDateString('vi-VN', {
				year: 'numeric',
				month: '2-digit',
				day: '2-digit'
			});
		},
	},
	mounted() {
		if (!localStorage.getItem('lang')) {
			localStorage.setItem('lang', 'vi');
		}
		
		const urlParams = new URLSearchParams(window.location.search);
		this.utm_source = urlParams.get('utm_source') || '';
		this.utm_campaign = urlParams.get('utm_campaign') || '';
		
		// Load vouchers from sessionStorage
		this.loadVouchers();
	},
};
</script>
