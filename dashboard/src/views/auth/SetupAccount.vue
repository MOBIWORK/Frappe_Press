<template>
	<LoginBox>
		<div v-if="!dashboardRoute">
			<div v-if="!$resources.validateRequestKey.loading">
				<div class="mb-4 text-3xl font-[500] text-gray-900">
					<div class="flex justify-center" v-if="!isInvitation">
						{{ $t('set_up_your_account') }}
					</div>
					<div class="flex justify-center" v-else>
						{{ $t('SetupAccount_content_1') }}: {{ invitationToTeam }}
					</div>
				</div>
				<form class="flex flex-col" @submit.prevent="submitForm">
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
									<label class="text-base" for="firstName">{{
										$t('full_name')
									}}</label>
								</div>
								<FormControl
									id="firstName"
									size="lg"
									variant="outline"
									placeholder="---"
									label=""
									type="text"
									v-model="firstName"
									name="firstName"
								/>
								<ErrorMessage
									class="mt-4"
									:message="this.$translateMessage(inputError.firstName)"
								/>
							</div>
							<div>
								<div class="mb-2 mt-4">
									<label class="text-base" for="phone">{{ $t('phone') }}</label>
								</div>
								<FormControl
									id="phone"
									size="lg"
									variant="outline"
									placeholder="---"
									label=""
									type="text"
									name="phone"
									v-model="phone"
									@keyup="validPhone"
								/>
								<ErrorMessage
									class="mt-4"
									:message="this.$translateMessage(inputError.phone)"
								/>
							</div>
							<div class="relative">
								<div class="mb-2 mt-4">
									<label class="text-base" for="password">{{
										$t('password')
									}}</label>
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
								class="mt-4"
								:message="this.$translateMessage(inputError.password)"
							/>
						</template>
						<div>
							<div class="mb-2 mt-4">
								<label class="text-base" for="country">{{
									$t('country')
								}}</label>
							</div>
							<FormControl
								class="custom-form-btn"
								type="select"
								id="country"
								size="lg"
								variant="outline"
								placeholder="---"
								label=""
								:options="countries"
								v-if="!isInvitation"
								v-model="country"
							/>
						</div>
						<Form
							v-if="signupFields.length > 0"
							:fields="signupFields"
							v-model="signupValues"
						/>
						<div class="mt-4 flex items-start">
							<FormControl
								id="term_policy"
								name="term_policy"
								size="lg"
								type="checkbox"
								v-model="termsAccepted"
							/>
							<label class="ml-2 text-base text-gray-900" for="term_policy">
								{{ $t('NewServer_content_1') }}
								<Link
									class="border-none"
									href="http://mbwcloud.com/terms"
									target="_blank"
									><span class="text-blue-500 hover:text-blue-700"
										>{{ $t('NewServer_content_2') }}
									</span></Link
								>
								{{ $t('and') }}
								<Link
									class="border-none"
									href="https://cloud.eov.solutions/privacy"
									target="_blank"
									><span class="text-blue-500 hover:text-blue-700">
										{{ $t('Privacy_Policy') }}
									</span></Link
								>
								{{ $t('of_EOV_Cloud') }}
							</label>
						</div>
						<ErrorMessage
							class="mt-4"
							:message="this.$translateMessage(inputError.termsAccepted)"
						/>
					</div>
					<ErrorMessage class="mt-4" :message="$resources.setupAccount.error" />
					<Button
						class="my-6 h-9 text-base font-[700] text-white"
						variant="solid"
						:loading="$resources.setupAccount.loading"
					>
						{{ isInvitation ? $t('agree') : $t('sign_up') }}
					</Button>
				</form>
			</div>
			<div
				class="text-center"
				v-else-if="!$resources.validateRequestKey.loading && !email"
			>
				{{ $t('SetupAccount_content_2') }}
				<Link to="/signup"
					><span class="font-[600] text-blue-600 hover:text-blue-700">{{
						$t('sign_up')
					}}</span></Link
				>
				{{ $t('SetupAccount_content_3') }}
			</div>
		</div>
		<div v-else>
			<div class="text-center">
				<div class="mb-12 text-center">
					<div class="mb-10 flex justify-center">
						<img src="../../assets/icon_tick.svg" alt="Key Icon" />
					</div>
					<div class="text-3xl">{{ $t('registration_successful') }}</div>
					<div class="mt-2 text-lg font-[400] text-gray-600">
						{{ $t('SetupAccount_content_4') }}
					</div>
				</div>
				<router-link :to="dashboardRoute">
					<Button
						class="my-6 h-9 w-full text-base font-[700] text-white"
						variant="solid"
					>
						{{ $t('return_to_login_page') }}
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
import SelectLanguage from '../../components/global/SelectLanguage.vue';

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
			iconCheck: true,
			dashboardRoute: null,
			email: null,
			firstName: null,
			phone: null,
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
			signupValues: {},
			inputError: {
				firstName: null,
				phone: null,
				password: null,
				country: null,
				termsAccepted: null
			}
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
						this.phone = res.phone;
						this.country = res.country;
						this.userExists = res.user_exists;
						this.invitationToTeam = res.team;
						this.isInvitation = res.is_invitation;
						this.invitedByParentTeam = res.invited_by_parent_team;
						this.oauthSignup = res.oauth_signup;
						this.countries = res.countries.map(el => ({
							label: el,
							value: el
						}));
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
					phone: this.phone,
					country: this.country,
					is_invitation: this.isInvitation,
					user_exists: this.userExists,
					invited_by_parent_team: this.invitedByParentTeam,
					accepted_user_terms: this.termsAccepted,
					oauth_signup: this.oauthSignup,
					signup_values: this.signupValues,
					lang: this.$i18n.locale
				},
				onSuccess(res) {
					this.dashboardRoute = '/setup-account/billing';
					window.location.href = '/dashboard/setup-account/billing';
					//this.dashboardRoute = '/';
					//window.location.href = '/dashboard';
				}
			};
		}
	},
	methods: {
		async submitForm() {
			let numErr = 0;
			// firstName
			let rs = this.$validdateInput(this.firstName, 'full_name');
			numErr += rs[0];
			this.inputError.firstName = rs[1];
			// phone
			rs = this.$validdateInput(this.phone, 'phone');
			numErr += rs[0];
			this.inputError.phone = rs[1];
			// password
			rs = this.$validdateInput(this.password, 'password1');
			numErr += rs[0];
			this.inputError.password = rs[1];
			console.log(this.inputError.password);
			// termsAccepted
			rs = this.$validdateInput(this.termsAccepted, 'term');
			numErr += rs[0];
			this.inputError.termsAccepted = rs[1];

			if (numErr) {
				return;
			}
			this.$resources.setupAccount.submit();
		},
		validPhone(e) {
			let value = e.target.value.replace(/[^0-9]/gm, '');
			this.phone = value;
		},
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
