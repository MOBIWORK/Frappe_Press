<template>
	<div>
		<header class="sticky top-0 z-10 border-b bg-white px-5 pt-2.5">
			<Breadcrumbs
				:items="[{ label: 'Thanh toán', route: { name: 'BillingScreen' } }]"
			/>
			<Tabs :tabs="tabs" class="-mb-px pl-0.5" />
		</header>
		<div class="mx-auto max-w-4xl py-5">
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
				{ label: 'Phương thức thanh toán', route: 'payment' },
				{ label: 'Số dư tín dụng', route: 'credit-balance' }
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
