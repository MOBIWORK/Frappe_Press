<template>
	<LoginBox top="mt-6" py="py-0">
		<div class="mt-6">
			<!-- <div class="mb-4 w-36">
				<SelectLanguage></SelectLanguage>
			</div> -->
			<div class="text-center">
				<div class="mb-4 text-3xl font-[500] text-gray-900">
					<div>{{ $t('SetupAccountBilling_content_1') }}</div>
				</div>
				<div class="text-sm text-gray-700">
					{{ $t('SetupAccountBilling_content_3') }}
				</div>
			</div>
			<div>
				<p class="text-base" v-if="message">
					{{ message }}
				</p>
				<AddressForm
					size="lg"
					ref="address-form"
					class="mt-4"
					v-model:address="billingInformation"
				/>
				<ErrorMessage
					class="mt-2"
					:message="this.$translateMessage(msgError)"
				/>
			</div>
			<div class="text-center">
				<Button
					class="my-6 h-9 px-8 text-base font-[700] text-white"
					variant="solid"
					:loading="$resources.updateBillingInformation.loading"
					:onClick="() => $resources.updateBillingInformation.submit()"
				>
					{{ $t('Continue') }}
				</Button>
			</div>
		</div>
	</LoginBox>
</template>

<script>
import LoginBox from '@/views/partials/LoginBox.vue';
import AddressForm from '@/components/AddressForm.vue';
import { notify } from '@/utils/toast';
import SelectLanguage from '../../components/global/SelectLanguage.vue';

export default {
	name: 'SetupAccountBilling',
	props: ['message'],
	components: {
		AddressForm,
		LoginBox,
		SelectLanguage
	},
	data() {
		return {
			msgError: null,
			billingInformation: {
				address: '',
				state: '',
				county: '',
				email_id: '',
				phone: '',
				tax_code: '',
				postal_code: '',
				country: '',
				gstin: '',
				billing_name: '',
				number_of_employees: '',
				areas_of_concern: '',
				enterprise: ''
			}
		};
	},
	resources: {
		currentBillingInformation: {
			url: 'press.api.account.get_billing_information',
			auto: true,
			onSuccess(data) {
				let billingInformation = data.billing_details;
				if ('country' in (billingInformation || {})) {
					Object.assign(this.billingInformation, {
						address: billingInformation.address_line1,
						tax_code: billingInformation.tax_code,
						county: billingInformation.county,
						state: billingInformation.state,
						postal_code: billingInformation.pincode,
						country: billingInformation.country,
						enterprise: billingInformation.enterprise,
						gstin:
							billingInformation.gstin == 'Not Applicable'
								? ''
								: billingInformation.gstin,
						number_of_employees: billingInformation.number_of_employees,
						areas_of_concern: billingInformation.areas_of_concern,
						billing_name: billingInformation.billing_name,
						phone: billingInformation.phone,
						email_id: billingInformation.email_id
					});
				}

				Object.assign(this.billingInformation, {
					enterprise: billingInformation.enterprise || 'Cá nhân'
				});
			}
		},
		updateBillingInformation() {
			return {
				url: 'press.api.account.update_billing_information',
				params: {
					billing_details: this.billingInformation
				},
				async onSuccess() {
					// notify({
					// 	icon: 'check',
					// 	color: 'green',
					// 	title: this.$t('SetupAccountBilling_content_2')
					// });

					await this.$call('press.api.billing.setup_intent_success', {
						setup_intent: {}
					});

					this.$router.push('/setup-account/preliminary_survey');
				},
				async validate() {
					let a = await this.$refs['address-form'].validateValues();
					this.msgError = a;
					if (a) {
						return this.$t(a);
					}
				}
			};
		}
	}
};
</script>
