<template>
	<div>
		<header class="sticky top-0 border-b bg-white px-5 pt-2.5">
			<Breadcrumbs
				:items="[{ label: 'Thanh toán', route: { name: 'BillingScreen' } }]"
			/>
			<Tabs :tabs="tabs" class="-mb-px pb-5 pl-0.5" />
		</header>
		<div class="mx-auto w-full overflow-auto px-5 py-5">
			<router-view />
		</div>
	</div>
</template>

<script>
import Tabs from '@/components/Tabs.vue';

export default {
	name: 'BillingScreen',
	pageMeta() {
		return {
			title: 'Billing - MBW Cloud'
		};
	},
	props: ['invoiceName'],
	components: {
		Tabs
	},
	computed: {
		tabs() {
			let tabRoute = subRoute => `/billing/${subRoute}`;
			let tabs = [
				{ label: 'Tổng quan', route: 'overview' },
				{ label: 'Hóa đơn', route: 'invoices' },
				{ label: 'Thông tin hóa đơn', route: 'payment' },
				{ label: 'Lịch sử giao dịch', route: 'credit-balance' }
			];

			return tabs.map(tab => {
				return {
					...tab,
					route: tabRoute(tab.route)
				};
			});
		}
	}
};
</script>
