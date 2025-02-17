<template>
	<Dialog
		:options="{ title: $t('FinalizeInvoicesDialog_1') }"
		modelValue="show"
	>
		<template #body-content>
			<div class="prose text-base">
				{{ $t('FinalizeInvoicesDialog_2') }}
				<ul class="pt-2">
					<li
						class="font-semibold"
						v-for="invoice in $resources.unpaidInvoices.data"
					>
						{{
							$date(invoice.period_end).toLocaleString({
								month: 'long',
								year: 'numeric'
							})
						}}
						-
						{{ invoice.amount_due + ' VND' }}
					</li>
				</ul>
				{{ $t('FinalizeInvoicesDialog_3') }}
				<Link to="/billing/invoices/">{{ $t('here') }}</Link
				>. {{ $t('FinalizeInvoicesDialog_4') }}
			</div>
		</template>
		<template #actions>
			<Button
				variant="solid"
				class="w-full"
				@click="$resources.finalizeInvoices.submit()"
			>
				{{ $t('FinalizeInvoicesDialog_5') }}
			</Button>
		</template>
	</Dialog>
</template>

<script>
export default {
	name: 'FinalizeInvoicesDialog',
	props: {
		show: Boolean,
		msg: String
	},
	resources: {
		finalizeInvoices: {
			url: 'press.api.billing.finalize_invoices'
		},
		unpaidInvoices: {
			url: 'press.api.billing.unpaid_invoices',
			auto: true
		}
	}
};
</script>
