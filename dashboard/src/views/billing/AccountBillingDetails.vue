<template>
	<Card
		title="Thông tin thanh toán"
		subtitle="Thông tin thanh toán của bạn được hiển thị trong hóa đơn hàng tháng"
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
		<div class="divide-y" v-if="$resources.billingDetails.data">
			<ListItem
				title="Tên công ty"
				:description="$resources.billingDetails.data.billing_name"
			/>
			<ListItem
				title="Email"
				:description="$resources.billingDetails.data.address.email_id"
			/>
			<ListItem
				title="Số điện thoại"
				:description="$resources.billingDetails.data.address.phone"
			/>
			<ListItem
				title="Loại doanh nghiệp"
				:description="$resources.billingDetails.data.address.enterprise"
			/>
			<ListItem
				v-if="$resources.billingDetails.data.address.enterprise == 'Công ty'"
				title="Mã số thuế"
				:description="$resources.billingDetails.data.address.tax_code"
			/>
			<ListItem
				title="Địa chỉ thanh toán"
				:description="
					$resources.billingDetails.data.billing_address || 'Chưa đặt'
				"
			/>
			<ListItem
				v-if="$account.team.country == 'India'"
				title="Tax ID"
				:description="$resources.billingDetails.data.gstin || 'Chưa đặt'"
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
	}
};
</script>
