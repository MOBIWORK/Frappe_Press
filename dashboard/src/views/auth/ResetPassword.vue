<template>
	<LoginBox>
		<div v-if="resetSuccess">
			<div class="text-center">
				<div class="mb-12 text-center">
					<div class="mb-10 flex justify-center">
						<img src="../../assets/icon_tick.svg" alt="Key Icon" />
					</div>
					<div class="text-3xl">{{ $t('ResetPassword_content_1') }}</div>
					<div class="mt-2 text-lg font-[400] text-gray-600">
						{{ $t('ResetPassword_content_2') }}
					</div>
				</div>
				<router-link to="/login">
					<Button
						class="my-6 h-9 w-full bg-red-600 text-base font-[700] text-white hover:bg-red-700"
						variant="solid"
					>
						{{ $t('return_to_login_page') }}
					</Button>
				</router-link>
			</div>
		</div>
		<div v-else>
			<div v-if="!$resources.validateResetKey.loading && email">
				<div class="my-4 text-3xl font-[500] text-gray-900">
					<div>{{ $t('Reset_Password') }}</div>
				</div>
				<form
					class="flex flex-col"
					@submit.prevent="$resources.resetPassword.submit()"
				>
					<div>
						<div>
							<div class="mb-2 mt-5">
								<label class="text-base" for="email">Email</label>
							</div>
							<FormControl
								id="email"
								size="lg"
								variant="outline"
								label=""
								:modelValue="email"
								name="email"
								autocomplete="off"
								disabled
							/>
						</div>
						<div class="relative">
							<div class="mb-2 mt-5">
								<label class="text-base" for="password">{{
									$t('Password')
								}}</label>
							</div>
							<FormControl
								id="password"
								size="lg"
								variant="outline"
								label=""
								placeholder="••••••••"
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
					</div>
					<ErrorMessage
						class="mt-6"
						:message="$resources.resetPassword.error"
					/>
					<Button
						:class="
							password
								? 'my-6 h-9  text-base font-[700] text-white '
								: 'my-6 h-9 bg-[#DFE3E8] text-base font-[700] text-white'
						"
						variant="solid"
						:disabled="!password"
						:loading="$resources.resetPassword.loading"
					>
						{{ $t('Reset_Password') }}
					</Button>
				</form>
			</div>
			<div
				class="text-center"
				v-else-if="!$resources.validateResetKey.loading && !email"
			>
				{{ $t('ResetPassword_content_3') }} <strong>{{ requestKey }}</strong>
				{{ $t('ResetPassword_content_4') }}
				<router-link class="underline" to="/login"
					><span class="font-[600] text-blue-600 hover:text-blue-700">{{
						$t('login')
					}}</span></router-link
				>.
			</div>
		</div>
	</LoginBox>
</template>

<script>
import LoginBox from '@/views/partials/LoginBox.vue';

export default {
	name: 'ResetPassword',
	components: {
		LoginBox
	},
	props: ['requestKey'],
	data() {
		return {
			iconCheck: true,
			resetSuccess: false,
			email: null,
			password: null
		};
	},
	resources: {
		validateResetKey() {
			return {
				url: 'press.api.account.get_user_for_reset_password_key',
				params: {
					key: this.requestKey
				},
				onSuccess(email) {
					this.email = email || null;
					// this.email = null;
				},
				auto: true
			};
		},
		resetPassword() {
			return {
				url: 'press.api.account.reset_password',
				params: {
					key: this.requestKey,
					password: this.password
				},
				onSuccess() {
					this.resetSuccess = true;
					// window.location.reload();
				}
			};
		}
	},
	methods: {
		changeIconEye() {
			this.iconCheck = !this.iconCheck;
		}
	}
};
</script>
