<template>
	<Alert title="Thiết lập tài khoản" v-if="!$account.hasBillingInfo">
		{{ message }}
		<template #actions>
			<Button
				variant="solid"
				@click="
					this.$account.team.billing_address
						? (showPrepaidCreditsDialog = true)
						: (editBillingDetails = true)
				"
				class="whitespace-nowrap"
			>
				{{
					this.$account.team.billing_address
						? 'Thêm Số Dư'
						: 'Xác nhận thông tin'
				}}
			</Button>
		</template>
		<!-- <BillingInformationDialog v-model="showCardDialog" v-if="showCardDialog" /> -->
		<UpdateBillingDetails
			v-model="editBillingDetails"
			@updated="
				editBillingDetails = false;
				$resources.billingDetails.reload();
				this.$emit('updated');
			"
		/>
		<PrepaidCreditsDialog
			v-if="showPrepaidCreditsDialog"
			v-model:show="showPrepaidCreditsDialog"
			:minimum-amount="2000"
			@success="handleAddPrepaidCreditsSuccess"
		/>
	</Alert>
</template>
<script>
import { defineAsyncComponent } from 'vue';

export default {
	name: 'AlertBillingInformation',
	emits: ['updated'],
	components: {
		// BillingInformationDialog: defineAsyncComponent(() =>
		// 	import('./BillingInformationDialog.vue')
		// ),
		PrepaidCreditsDialog: defineAsyncComponent(() =>
			import('./PrepaidCreditsDialog.vue')
		),
		UpdateBillingDetails: defineAsyncComponent(() =>
			import('@/components/UpdateBillingDetails.vue')
		)
	},
	resources: {
		billingDetails: 'press.api.billing.details'
	},
	data() {
		return {
			showCardDialog: false,
			showPrepaidCreditsDialog: false,
			editBillingDetails: false
		};
	},
	methods: {
		handleAddPrepaidCreditsSuccess() {
			this.showPrepaidCreditsDialog = false;
		}
	},
	computed: {
		isDefaultPaymentModeCard() {
			return this.$account.team.payment_mode == 'Card';
		},
		message() {
			if (this.$account.team.billing_address) {
				return 'Số dư tài khoản của bạn đã hết. Vui lòng nạp thêm tiền vào tài khoản của bạn để tiếp tục sử dụng dịch vụ.';
			} else {
				return 'Bạn chưa xác nhận thông tin thanh toán của mình. Thêm nó để bắt đầu tạo trang web.';
			}
		}
	}
};
</script>
