<template>
	<Dialog
		:options="{
			title: 'Thay đổi phương thức thanh toán',
			actions: [
				{
					label: 'Thay đổi',
					variant: 'solid',
					loading: $resources.changePaymentMode.loading,
					onClick: () => $resources.changePaymentMode.submit()
				}
			]
		}"
		:modelValue="modelValue"
		@update:modelValue="$emit('update:modelValue', $event)"
	>
		<template v-slot:body-content>
			<FormControl
				label="Chọn loại thanh toán"
				type="select"
				:options="paymentModeOptions"
				v-model="paymentMode"
			/>
			<p class="mb-5 mt-2 text-base text-gray-600">
				{{ paymentModeDescription }}
			</p>
			<ErrorMessage
				class="mt-2"
				:message="$resources.changePaymentMode.error"
			/>
		</template>
	</Dialog>
	<BillingInformationDialog
		v-model="showBillingInformationDialog"
		v-if="showBillingInformationDialog"
	/>
	<PrepaidCreditsDialog
		v-if="showPrepaidCreditsDialog"
		v-model:show="showPrepaidCreditsDialog"
		:minimumAmount="10000"
		@success="
			() => {
				$resources.upcomingInvoice.reload();
				showPrepaidCreditsDialog = false;
			}
		"
	/>
</template>
<script>
import { defineAsyncComponent } from 'vue';

export default {
	name: 'ChangePaymentModeDialog',
	props: ['modelValue'],
	emits: ['update:modelValue'],
	components: {
		BillingInformationDialog: defineAsyncComponent(() =>
			import('./BillingInformationDialog.vue')
		),
		PrepaidCreditsDialog: defineAsyncComponent(() =>
			import('@/components/PrepaidCreditsDialog.vue')
		)
	},
	data() {
		return {
			showBillingInformationDialog: false,
			showPrepaidCreditsDialog: false,
			paymentMode: this.$account.team.payment_mode
		};
	},
	watch: {
		show(value) {
			if (!value) {
				this.paymentMode = this.$account.team.payment_mode;
			}
		}
	},
	resources: {
		changePaymentMode() {
			return {
				url: 'press.api.billing.change_payment_mode',
				params: {
					mode: this.paymentMode
				},
				onSuccess() {
					this.$emit('update:modelValue', false);
					this.$resources.changePaymentMode.reset();
				},
				validate() {
					if (
						this.paymentMode == 'Card' &&
						!this.$account.team.default_payment_method
					) {
						this.$emit('update:modelValue', false);
						this.showBillingInformationDialog = true;
					}

					if (
						this.paymentMode == 'Prepaid Credits' &&
						this.$account.balance === 0
					) {
						// this.$emit('update:modelValue', false);
						// this.showPrepaidCreditsDialog = true;
					}

					if (
						this.paymentMode == 'Paid By Partner' &&
						!this.$account.team.partner_email
					) {
						return 'Please add a partner first from Partner section';
					}
				}
			};
		}
	},
	computed: {
		paymentModeDescription() {
			return {
				Card: `Thẻ của bạn sẽ bị tính phí cho đăng ký hàng tháng`,
				'Prepaid Credits': `Bạn sẽ bị tính phí từ số dư tài khoản của mình cho đăng ký hàng tháng`,
				'Partner Credits': `You will be charged from your partner credits on frappe.io`,
				'Paid By Partner': `Your partner will be charged for monthly subscription`
			}[this.paymentMode];
		},
		paymentModeOptions() {
			// if (this.$account.team.erpnext_partner) {
			// 	return ['Card', 'Prepaid Credits', 'Partner Credits'];
			// }
			// return ['Card', 'Prepaid Credits', 'Paid By Partner'];

			return [{ label: 'Trả trước', value: 'Prepaid Credits' }];
		}
	}
};
</script>
