<template>
	<Card
		title="Thông tin hóa đơn"
		subtitle="Thông tin của bạn được sử dụng trong hóa đơn điện tử"
	>
		<template #actions>
			<Button @click="editBillingDetails = true">Cập nhật</Button>
		</template>
		<UpdateBillingDetails
			v-model="editBillingDetails"
			@updated="
				editBillingDetails = false;
				$resources.billingDetails.reload();
			"
		/>
		<div class="divide-y" v-if="infoBilling">
			<ListItem
				title="Đối tượng"
				:description="infoBilling.address.enterprise"
			/>
			<ListItem
				:title="
					infoBilling.address.enterprise == `Công ty` ? `Tên công ty` : `Họ tên`
				"
				:description="infoBilling.billing_name"
			/>
			<ListItem
				v-if="infoBilling.address.enterprise == 'Công ty'"
				title="Mã số thuế"
				:description="infoBilling.address.tax_code"
			/>
			<ListItem title="Email" :description="infoBilling.address.email_id" />
			<ListItem
				title="Số điện thoại"
				:description="infoBilling.address.phone"
			/>
			<ListItem
				title="Địa chỉ thanh toán"
				:description="infoBilling.billing_address || 'Chưa đặt'"
			/>
			<ListItem
				v-if="$account.team.country == 'India'"
				title="Tax ID"
				:description="infoBilling.gstin || 'Chưa đặt'"
			/>
		</div>
	</Card>
</template>
<script>
import { defineAsyncComponent } from 'vue';

export default {
	name: 'AccountBillingDetails',
	emits: ['updated'],
	components: {
		UpdateBillingDetails: defineAsyncComponent(() =>
			import('@/components/UpdateBillingDetails.vue')
		)
	},
	resources: {
		billingDetails: 'press.api.billing.details'
	},
	data() {
		return {
			editBillingDetails: false
		};
	},
	computed: {
		infoBilling() {
			return this.$resources.billingDetails.data;
		}
	}
};
</script>
