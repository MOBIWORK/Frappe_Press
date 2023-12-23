<template>
	<Card title="Số dư tiền nạp" subtitle="Lịch sử số dư tiền nạp của bạn">
		<div class="max-h-96 divide-y">
			<div
				class="grid grid-cols-6 items-center gap-x-8 py-4 text-base text-gray-600 md:grid-cols-6"
			>
				<span class="hidden md:inline">Ngày</span>
				<span class="col-span-2 md:col-span-1">Mô tả</span>
				<span>Số tiền</span>
				<span>Số tiền đã nạp</span>
				<span>Số dư</span>
				<span>Trạng thái</span>
			</div>
			<div
				class="grid grid-cols-6 items-center gap-x-8 py-4 text-base text-gray-900 md:grid-cols-6"
				v-for="d in $resources.balances.data"
				:key="d.name"
			>
				<div class="hidden md:block">
					{{ formatDate(d) }}
				</div>
				<div class="col-span-2 whitespace-nowrap text-gray-700 md:col-span-1">
					<div>
						{{ getDescription(d) }}
					</div>
					<div class="md:hidden">{{ formatDate(d) }}</div>
				</div>
				<div class="whitespace-nowrap text-gray-700">
					{{ d.formatted.amount }}
				</div>
				<div class="whitespace-nowrap text-gray-700">
					{{ d.formatted.amount }}
				</div>
				<div class="whitespace-nowrap">{{ d.formatted.ending_balance }}</div>
				<div>{{ getStatus(d) }}</div>
			</div>
		</div>
	</Card>
</template>
<script>
export default {
	name: 'AccountBillingCreditBalance',
	resources: {
		balances: 'press.api.billing.balances'
	},
	methods: {
		getStatus(d) {
			var statusDoc = {
				0: 'Chờ thanh toán',
				1: 'Đã thanh toán',
				2: 'Đã hủy'
			};
			return statusDoc[d.docstatus];
		},
		formatDate(d) {
			return this.$date(d.creation).toFormat('dd-MM-yyyy');
		},
		getDescription(d) {
			if (d.type === 'Applied To Invoice' && d.formatted.invoice_for) {
				return `Hóa đơn cho ${d.formatted.invoice_for}`;
			}

			return d.amount < 0 ? d.type : d.source;
		}
	}
};
</script>
