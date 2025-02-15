<template>
	<div>
		<header class="sticky top-0 z-10 border-b bg-white px-5 pt-2.5">
			<Breadcrumbs
				:items="[{ label: $t('billing'), route: { name: 'BillingScreen' } }]"
			/>
			<Tabs :tabs="tabs" class="-mb-px pl-0.5" />
		</header>
		<div class="mx-auto max-w-5xl overflow-auto px-5 py-5">
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
			title: `${this.$t('billing')} - EOV Cloud`
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
				{ label: this.$t('overview'), route: 'overview' },
				{ label: this.$t('invoices'), route: 'invoices' },
				{ label: this.$t('invoice_information'), route: 'payment' },
				{ label: this.$t('transaction_history'), route: 'transaction-history' },
				{
					label: this.$t('ai_service_usage_history'),
					route: 'ai-service-usage-history'
				}
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
