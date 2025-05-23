<template>
	<div>
		<Card
			v-if="profileData && profileData.profile_created"
			:title="$t('Payout_Preferences')"
			:subtitle="$t('PublisherPayoutInfoCard_content_1')"
		>
			<div class="divide-y-2">
				<ListItem
					:title="$t('Payout_Method')"
					:description="payoutMethod || $t('not_set')"
				/>

				<ListItem
					v-if="payoutMethod == 'PayPal'"
					title="PayPal ID"
					:description="payPalId || $t('not_set')"
				/>

				<ListItem
					v-if="payoutMethod == 'Bank Transfer'"
					title="Account Holder Name"
					:description="acName || $t('not_set')"
				/>

				<ListItem
					v-if="payoutMethod == 'Bank Transfer'"
					title="Account Number"
					:description="acNumber || $t('not_set')"
				/>
			</div>

			<template #actions>
				<Button icon-left="edit" @click="showEditProfileDialog = true">{{
					$t('Edit')
				}}</Button>
			</template>
		</Card>

		<Dialog
			:options="{
				title: $t('Edit_Publisher_Profile'),
				actions: [
					{
						variant: 'solid',
						label: $t('save_changes'),
						loading: $resources.updatePublisherProfile.loading,
						onClick: () => $resources.updatePublisherProfile.submit()
					}
				]
			}"
			v-model="showEditProfileDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<FormControl
						:label="$t('Preferred_Payment_Method')"
						type="select"
						:options="[
							'MBWCloud Credits',
							'Frappe Cloud Credits',
							'Bank Transfer',
							'PayPal'
						]"
						v-model="payoutMethod"
					/>

					<FormControl
						v-if="payoutMethod == 'PayPal'"
						label="PayPal ID"
						v-model="payPalId"
					/>

					<FormControl
						label="GSTIN (if applicable)"
						v-if="
							payoutMethod != 'MBWCloud Credits' &&
							payoutMethod != 'Frappe Cloud Credits'
						"
						v-model="gstin"
					/>

					<FormControl
						v-if="payoutMethod == 'Bank Transfer'"
						label="Account Number"
						v-model="acNumber"
					/>

					<FormControl
						v-if="payoutMethod == 'Bank Transfer'"
						label="Account Holder Name"
						v-model="acName"
					/>

					<FormControl
						label="Bank Name, Branch, IFS Code"
						v-if="payoutMethod == 'Bank Transfer'"
						type="textarea"
						v-model="otherDetails"
					/>
				</div>

				<ErrorMessage
					class="mt-4"
					:message="$resources.updatePublisherProfile.error"
				/>
			</template>
		</Dialog>
	</div>
</template>

<script>
export default {
	props: ['profileData'],
	emits: ['profileUpdated'],
	data() {
		return {
			showEditProfileDialog: false,
			payoutMethod: '',
			payPalId: '',
			acNumber: '',
			acName: '',
			gstin: '',
			otherDetails: ''
		};
	},
	mounted() {},
	resources: {
		updatePublisherProfile() {
			return {
				url: 'press.api.marketplace.update_publisher_profile',
				params: {
					profile_data: {
						preferred_payout_method: this.payoutMethod,
						paypal_id: this.payPalId,
						bank_account_number: this.acNumber,
						bank_account_holder_name: this.acName,
						gstin: this.gstin,
						other_bank_details: this.otherDetails
					}
				},
				onSuccess() {
					this.showEditProfileDialog = false;
					this.$emit('profileUpdated');
				}
			};
		}
	},
	watch: {
		profileData(data) {
			if (data && data.profile_created) {
				this.payoutMethod = data.profile_info.preferred_payout_method;
				this.payPalId = data.profile_info.paypal_id;
				this.acNumber = data.profile_info.bank_account_number;
				this.acName = data.profile_info.bank_account_holder_name;
				this.gstin = data.profile_info.gstin;
				this.otherDetails = data.profile_info.other_bank_details;
			}
		}
	}
};
</script>
