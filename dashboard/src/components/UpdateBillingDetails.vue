<template>
	<Dialog
		:options="{
			title: $t('update_invoice_information'),
			actions: [
				{
					label: $t('confirm'),
					variant: 'solid',
					loading: $resources.updateBillingInformation.loading,
					onClick: () => $resources.updateBillingInformation.submit()
				}
			]
		}"
		:modelValue="show"
		@update:modelValue="$emit('update:show', $event)"
	>
		<template v-slot:body-content>
			<p class="text-base" v-if="message">
				{{ message }}
			</p>
			<AddressForm
				ref="address-form"
				class="mt-4"
				v-model:address="billingInformation"
			/>
			<ErrorMessage
				class="mt-2"
				:message="$resources.updateBillingInformation.error"
			/>
		</template>
	</Dialog>
</template>

<script>
import AddressForm from '@/components/AddressForm.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'UpdateBillingDetails',
	props: ['message', 'show'],
	emits: ['update:show', 'updated'],
	components: {
		AddressForm
	},
	data() {
		return {
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
				company_name: '',
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
				let user_detail = data.user_detail;
				if ('country' in (billingInformation || {})) {
					Object.assign(this.billingInformation, {
						address: billingInformation.address_line1,
						email_id: billingInformation.email_id,
						phone: billingInformation.phone,
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
						billing_name: billingInformation.billing_name,
						company_name: billingInformation.company_name,
						number_of_employees: billingInformation.number_of_employees,
						areas_of_concern: billingInformation.areas_of_concern
					});
				}
				Object.assign(this.billingInformation, {
					email_id: billingInformation.email_id || user_detail.email,
					phone: billingInformation.phone || user_detail.phone,
					billing_name:
						billingInformation.billing_name || user_detail.first_name
				});
			}
		},
		updateBillingInformation() {
			return {
				url: 'press.api.billing.setup_billing_info',
				params: {
					address: this.billingInformation
				},
				async onSuccess() {
					this.$emit('update:show', false);
					notify({
						icon: 'check',
						color: 'green',
						title: this.$t('address_updated_successfully')
					});
					this.$emit('updated');
				},
				validate() {
					return this.$refs['address-form'].validateValues();
				}
			};
		}
	}
};
</script>
